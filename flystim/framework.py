from PyQt5 import QtOpenGL, QtWidgets

import time
import sys
import signal
import moderngl
import numpy as np
import pandas as pd
import platform

from flystim import stimuli

# from flystim.stimuli import ContrastReversingGrating, RotatingBars, ExpandingEdges, RandomBars, SequentialBars, SineGrating, RandomGrid
# from flystim.stimuli import Checkerboard, MovingPatch, ConstantBackground, ArbitraryGrid
from flystim import GenPerspective
from flystim.square import SquareProgram
from flystim.screen import Screen
from math import radians

from flyrpc.transceiver import MySocketServer
from flyrpc.util import get_kwargs


class StimDisplay(QtOpenGL.QGLWidget):
    """
    Class that controls the stimulus display on one screen.  It contains the pyglet window object for that screen,
    and also controls rendering of the stimulus, toggling corner square, and/or debug information.
    """

    def __init__(self, screen, server, app):
        """
        :param screen: Screen object (from flystim.screen) corresponding to the screen on which the stimulus will
        be displayed.
        """

        # call super constructor
        super().__init__(make_qt_format(vsync=screen.vsync))

        # configure window to reside on a specific screen
        # re: https://stackoverflow.com/questions/6854947/how-to-display-a-window-on-a-secondary-display-in-pyqt
        if platform.system() == 'Windows':
            desktop = QtWidgets.QDesktopWidget()
            rectScreen = desktop.screenGeometry(screen.id)
            self.move(rectScreen.left(), rectScreen.top())
            self.resize(rectScreen.width(), rectScreen.height())

        # stimulus initialization
        self.stim_list = []

        # stimulus state
        self.stim_paused = True
        self.stim_start_time = None
        self.stim_offset_time = 0

        # profiling information
        self.profile_frame_count = None
        self.profile_start_time = None
        self.profile_last_time = None
        self.profile_frame_times = None

        # save handles to screen and server
        self.screen = screen
        self.server = server
        self.app = app

        # cls_list = [MovingPatch]
        # self.render_programs = {cls.__name__: cls(screen=screen) for cls in cls_list}

        # make program for rendering the corner square
        self.square_program = SquareProgram(screen=screen)

        # initialize background color
        self.idle_background = 0.5

        # set the closed-loop parameters
        self.global_theta_offset = 0
        self.global_phi_offset = 0
        self.global_fly_pos = np.array([0, 0, 0], dtype=float)

        self.perspective = get_perspective(self.global_fly_pos, self.global_theta_offset, self.global_phi_offset)

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)

        # initialize square program
        self.square_program.initialize(self.ctx)

    def get_stim_time(self, t):
        stim_time = self.stim_offset_time

        if not self.stim_paused:
            stim_time += t - self.stim_start_time

        return stim_time

    def paintGL(self):
        # quit if desired
        if self.server.shutdown_flag.is_set():
            self.app.quit()

        # handle RPC input
        self.server.process_queue()

        # set the viewport to fill the window
        # ref: https://github.com/pyqtgraph/pyqtgraph/issues/422
        self.ctx.viewport = (0, 0, self.width()*self.devicePixelRatio(), self.height()*self.devicePixelRatio())

        # draw the stimulus
        if self.stim_list:
            t = time.time()

            self.ctx.clear(0, 0, 0, 1)
            self.ctx.enable(moderngl.BLEND)

            for stim in self.stim_list:
                stim.configure(**stim.kwargs)
                stim.paint_at(self.get_stim_time(t), get_perspective(self.global_fly_pos, self.global_theta_offset, self.global_phi_offset))

            # try:
            #     # TODO: make sure that profile information is still accurate
            #     self.profile_frame_count += 1
            #     if (self.profile_last_time is not None) and (self.profile_frame_times is not None):
            #         self.profile_frame_times.append(t - self.profile_last_time)
            #     self.profile_last_time = t
            # except:
            #     pass
        else:
            self.ctx.clear(self.idle_background, self.idle_background, self.idle_background, 1.0)

        # draw the corner square
        self.square_program.paint()

        # update the window
        self.ctx.finish()
        self.update()


    ###########################################
    # control functions
    ###########################################

    def update_stim(self, rate, t):
        for stim, config_options in self.stim_list:
            if isinstance(stim, (SineGrating, RotatingBars)):
                # get the time that will be passed to the stimulus
                t = self.get_stim_time(t)

                # get the spatial period, rate, and offset (in degrees)
                period = config_options.kwargs.get('period', 20)
                old_rate = config_options.kwargs.get('rate', 10)
                old_offset = config_options.kwargs.get('offset', 0)

                # set the new rate and offset
                config_options.kwargs['rate'] = rate
                config_options.kwargs['offset'] = (rate - old_rate) * (360 / period) * t + old_offset

    def load_stim(self, name, hold=False, **kwargs):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        """

        if hold is False:
            self.stim_list = []
            self.stim_offset_time = 0

        stim = getattr(stimuli, name)(screen=self.screen)
        stim.initialize(self.ctx)
        stim.kwargs = kwargs
        self.stim_list.append(stim)

    def start_stim(self, t):
        """
        Starts the stimulus animation, using the given time as t=0
        :param t: Time corresponding to t=0 of the animation
        """

        self.profile_frame_count = 0
        self.profile_start_time = time.time()

        self.profile_last_time = None
        self.profile_frame_times = []

        self.stim_paused = False
        self.stim_start_time = t

    def pause_stim(self, t):
        self.stim_paused = True
        self.stim_offset_time = t - self.stim_start_time + self.stim_offset_time
        self.stim_start_time = t

    def stop_stim(self, print_profile = True):
        """
        Stops the stimulus animation and removes it from the display.
        """

        # print profiling information if applicable

        if ((self.profile_frame_count is not None) and
            (self.profile_start_time is not None) and
            (self.stim_list)):

            profile_duration = time.time() - self.profile_start_time

            # filter out frame times of duration zero
            fps_data = np.array(self.profile_frame_times)
            fps_data = fps_data[fps_data != 0]

            if len(fps_data) > 0:
                fps_data = pd.Series(1.0/fps_data)
                stim_names = ', '.join([type(stim).__name__ for stim, _ in self.stim_list])
                if print_profile:
                    print('*** ' + stim_names + ' ***')
                    print(fps_data.describe(percentiles=[0.01, 0.05, 0.1, 0.9, 0.95, 0.99]))
                    print()

        # reset stim variables

        self.stim_list = []
        self.stim_offset_time = 0

        self.stim_paused = True
        self.stim_start_time = None

        self.profile_frame_count = None
        self.profile_start_time = None

        self.profile_last_time = None
        self.profile_frame_times = None

    def start_corner_square(self):
        """
        Start toggling the corner square.
        """

        self.square_program.toggle = True

    def stop_corner_square(self):
        """
        Stop toggling the corner square.
        """

        self.square_program.toggle = False

    def white_corner_square(self):
        """
        Stop the corner square from toggling, then make it white.
        """

        self.set_corner_square(1.0)

    def black_corner_square(self):
        """
        Stop the corner square from toggling, then make it black.
        """

        self.set_corner_square(0.0)

    def set_corner_square(self, color):
        """
        Stop the corner square from toggling, then set it to the desired color.
        """

        self.stop_corner_square()
        self.square_program.color = color

    def show_corner_square(self):
        """
        Show the corner square.
        """

        self.square_program.draw = True

    def hide_corner_square(self):
        """
        Hide the corner square.  Note that it will continue to toggle if self.should_toggle_square is True,
        even though nothing will be displayed.
        """

        self.square_program.draw = False

    def set_idle_background(self, color):
        """
        Sets the monochrome color of the background when there is no stimulus being displayed (sometimes called the
        interleave period).
        """

        self.idle_background = color

    def set_global_fly_pos(self, x, y, z):
        self.global_fly_pos = np.array([x, y, z], dtype=float)

    def set_global_theta_offset(self, value):
        self.global_theta_offset = radians(value)

    def set_global_phi_offset(self, value):
        self.global_phi_offset = radians(value)


def get_perspective(fly_pos, theta, phi):
    # nominal position
    perspective = GenPerspective(pa=(+1, -1, -1), pb=(+1, +1, -1), pc=(+1, -1, 1), pe=fly_pos)

    # rotate screen and eye position
    return perspective.roty(-radians(phi)).rotz(radians(theta))


def make_qt_format(vsync):
    """
    Initializes the Qt OpenGL format.
    :param vsync: If True, use VSYNC, otherwise update as fast as possible
    """

    # create format with default settings
    format = QtOpenGL.QGLFormat()

    # use OpenGL 3.3
    format.setVersion(3, 3)
    format.setProfile(QtOpenGL.QGLFormat.CoreProfile)

    # use VSYNC
    if vsync:
        format.setSwapInterval(1)
    else:
        format.setSwapInterval(0)

    # TODO: determine what these lines do and whether they are necessary
    format.setSampleBuffers(True)
    format.setDepthBufferSize(24)

    # needed to enable transparency
    format.setAlpha(True)

    return format


def main():
    # get the configuration parameters
    kwargs = get_kwargs()

    # get the screen
    screen = Screen.deserialize(kwargs.get('screen', {}))

    # launch the server
    server = MySocketServer(host=kwargs['host'], port=kwargs['port'], threaded=True, auto_stop=True, name=screen.name)

    # launch application
    app = QtWidgets.QApplication([])

    # create the StimDisplay object
    screen = Screen.deserialize(kwargs.get('screen', {}))
    stim_display = StimDisplay(screen=screen, server=server, app=app)

    # register functions
    server.register_function(stim_display.load_stim)
    server.register_function(stim_display.start_stim)
    server.register_function(stim_display.stop_stim)
    server.register_function(stim_display.pause_stim)
    server.register_function(stim_display.update_stim)
    server.register_function(stim_display.start_corner_square)
    server.register_function(stim_display.stop_corner_square)
    server.register_function(stim_display.white_corner_square)
    server.register_function(stim_display.black_corner_square)
    server.register_function(stim_display.set_corner_square)
    server.register_function(stim_display.show_corner_square)
    server.register_function(stim_display.hide_corner_square)
    server.register_function(stim_display.set_idle_background)
    server.register_function(stim_display.set_global_fly_pos)
    server.register_function(stim_display.set_global_theta_offset)
    server.register_function(stim_display.set_global_phi_offset)

    # display the stimulus
    if screen.fullscreen:
        stim_display.showFullScreen()
    else:
        stim_display.show()

    ####################################
    # Run QApplication
    ####################################

    # Use Ctrl+C to exit.
    # ref: https://stackoverflow.com/questions/2300401/qapplication-how-to-shutdown-gracefully-on-ctrl-c
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
