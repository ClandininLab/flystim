from PyQt5 import QtOpenGL, QtWidgets

import time
import sys
import signal
import moderngl
import numpy as np
import pandas as pd
import platform
import os

from flystim.stimuli import ContrastReversingGrating, RotatingBars, ExpandingEdges, RandomBars, SequentialBars, SineGrating, RandomGrid
from flystim.stimuli import Checkerboard, MovingPatch, ConstantBackground, ArbitraryGrid
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

        # make OpenGL programs that are used by stimuli
        cls_list = [ContrastReversingGrating, RotatingBars, ExpandingEdges, RandomBars, SequentialBars, SineGrating, RandomGrid,
                    MovingPatch, Checkerboard, ConstantBackground, ArbitraryGrid]
        self.render_programs = {cls.__name__: cls(screen=screen) for cls in cls_list}

        # make program for rendering the corner square
        self.square_program = SquareProgram(screen=screen)

        # initialize background color
        self.idle_background = 0.5

        # set the closed-loop parameters
        self.global_theta_offset = 0
        self.global_phi_offset = 0
        self.global_fly_pos = np.array([0, 0, 0], dtype=float)

        # save history for behavior analysis and stim-behavior alignment
        self.save_history_flag = False

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context()

        # initialize stimuli programs
        for render_program in self.render_programs.values():
            render_program.initialize(self.ctx)

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
            stim_time = self.get_stim_time(t)

            self.ctx.clear(0, 0, 0, 1)
            self.ctx.enable(moderngl.BLEND)

            for stim, config_options in self.stim_list:
                stim.apply_config_options(config_options)
                stim.paint_at(stim_time, global_fly_pos=self.global_fly_pos,
                              global_theta_offset=self.global_theta_offset,
                              global_phi_offset=self.global_phi_offset)

            # Save stim_time AND global positions and offsets
            if self.save_history_flag:
                self.square_history[self.profile_frame_count] = int(self.square_program.color) #stim_time
                self.stim_time_history[self.profile_frame_count] = t
                self.stim_time_from_start_history[self.profile_frame_count] = stim_time
                self.global_fly_posx_history[self.profile_frame_count] = self.global_fly_pos[0]
                self.global_fly_posy_history[self.profile_frame_count] = self.global_fly_pos[1]
                self.global_theta_offset_history[self.profile_frame_count] = self.global_theta_offset
                #self.global_fly_posz_history[self.profile_frame_count] = self.global_fly_pos[2]
                #self.global_phi_offset_history[self.profile_frame_count] = self.global_phi_offset

            self.profile_frame_count += 1
        else:
            self.ctx.clear(self.idle_background, self.idle_background, self.idle_background, 1.0)


        # draw the corner square
        self.square_program.paint() #must come after saving history to match length??

        # update the window
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

    def load_stim(self, name, hold=False, *args, **kwargs):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        """

        if hold is False:
            self.stim_list = []
            self.stim_offset_time = 0

        stim = self.render_programs[name]
        config_options = stim.make_config_options(*args, **kwargs)

        self.stim_list.append((stim, config_options))

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

        if self.save_history_flag:
            self.square_history = np.zeros(self.estimated_n_frames)
            self.stim_time_history = np.zeros(self.estimated_n_frames)
            self.stim_time_from_start_history = np.zeros(self.estimated_n_frames)
            self.global_fly_posx_history = np.zeros(self.estimated_n_frames)
            self.global_fly_posy_history = np.zeros(self.estimated_n_frames)
            self.global_theta_offset_history = np.zeros(self.estimated_n_frames)
            #self.global_fly_posz_history = np.zeros(self.estimated_n_frames)
            #self.global_phi_offset_history = np.zeros(self.estimated_n_frames)

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

    def set_save_path(self, save_path):
        self.save_path = save_path

    def set_save_prefix(self, save_prefix):
        self.save_prefix = save_prefix

    def set_save_history_params(self, save_history_flag=True, save_path="", save_prefix="", fs_frame_rate_estimate=120, stim_duration=65):
        self.save_history_flag = save_history_flag
        if save_history_flag:
            self.save_path = save_path
            self.save_prefix = save_prefix
            self.estimated_n_frames = int(np.ceil(fs_frame_rate_estimate * stim_duration))
            self.square_history = []
            self.stim_time_history = []
            self.stim_time_from_start_history = []
            self.global_fly_posx_history = []
            self.global_fly_posy_history = []
            self.global_theta_offset_history = []
            #self.global_fly_posz_history = []
            #self.global_phi_offset_history = []

    def save_history(self):
        np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_square.txt', np.array(self.square_history), fmt='%i', delimiter='\n')
        np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_timestamps.txt', np.array(self.stim_time_history), delimiter='\n')
        np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_timestamps_from_start.txt', np.array(self.stim_time_from_start_history), delimiter='\n')
        np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_posx.txt', np.array(self.global_fly_posx_history), delimiter='\n')
        np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_posy.txt', np.array(self.global_fly_posy_history), delimiter='\n')
        np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_theta.txt', np.array(self.global_theta_offset_history), delimiter='\n')
        #np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_fly_posz.txt', np.array(self.global_fly_posz_history), delimiter='\n')
        #np.savetxt(self.save_path+os.path.sep+self.save_prefix+'_fs_phi_offset.txt', np.array(self.global_phi_offset_history), delimiter='\n')

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
    server.register_function(stim_display.set_save_path)
    server.register_function(stim_display.set_save_prefix)
    server.register_function(stim_display.set_save_history_params)
    server.register_function(stim_display.save_history)

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
