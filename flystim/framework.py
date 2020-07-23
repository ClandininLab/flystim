from PyQt5 import QtOpenGL, QtWidgets

import time
import sys
import signal
import moderngl
import numpy as np
import pandas as pd
import platform

from flystim import stimuli
from flystim.trajectory import Trajectory

from flystim.perspective import GenPerspective
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
        self.stim_started = False
        self.stim_start_time = None

        # profiling information
        self.profile_frame_times = []

        # save handles to screen and server
        self.screen = screen
        self.server = server
        self.app = app

        # make program for rendering the corner square
        self.square_program = SquareProgram(screen=screen)

        # initialize background color
        self.idle_background = 0.5

        # set the closed-loop parameters
        self.set_global_fly_pos(0, 0, 0)
        self.set_global_theta_offset(0) # deg -> radians
        self.set_global_phi_offset(0) # deg -> radians

        self.use_fly_trajectory = False
        self.fly_x_trajectory = None
        self.fly_y_trajectory = None
        self.fly_theta_trajectory = None

        self.perspective = get_perspective(self.global_fly_pos, self.global_theta_offset, self.global_phi_offset, screen=self.screen)

        # save history for behavior analysis and stim-behavior alignment
        self.save_history_flag = False

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND) # enable alpha blending
        self.ctx.enable(moderngl.DEPTH_TEST) # enable depth test

        # initialize square program
        self.square_program.initialize(self.ctx)

    def get_stim_time(self, t):
        stim_time = 0

        if self.stim_started:
            stim_time += t - self.stim_start_time

        return stim_time

    def paintGL(self):
        # t0 = time.time() #benchmarking
        # quit if desired
        if self.server.shutdown_flag.is_set():
            self.app.quit()

        # handle RPC input
        self.server.process_queue()

        # set the viewport to fill the window
        # ref: https://github.com/pyqtgraph/pyqtgraph/issues/422
        self.ctx.viewport = (0, 0, self.width()*self.devicePixelRatio(), self.height()*self.devicePixelRatio())

        # draw the stimulus
        t = time.time()
        if self.stim_list:
            self.ctx.clear(0, 0, 0, 1)
            if self.use_fly_trajectory:
                self.set_global_fly_pos(self.fly_x_trajectory.eval_at(self.get_stim_time(t)),
                                        self.fly_y_trajectory.eval_at(self.get_stim_time(t)),
                                        0)
                self.set_global_theta_offset(self.fly_theta_trajectory.eval_at(self.get_stim_time(t)))  # deg -> radians
            self.perspective = get_perspective(self.global_fly_pos, self.global_theta_offset, self.global_phi_offset, screen=self.screen)

            for stim in self.stim_list:
                if self.stim_started:
                    stim.paint_at(self.get_stim_time(t), self.perspective, fly_position=self.global_fly_pos.copy())
                else:
                    self.ctx.clear(self.idle_background, self.idle_background, self.idle_background, 1.0)

            self.profile_frame_times.append(t)

            # Save stim_time AND global positions and offsets
            if self.save_history_flag:
                profile_frame_count = len(self.profile_frame_times)

                ### All of these are preallocated rather than using the append call, in case append is slow. Perhaps useful to test later since append is much cleaner...
                self.square_history[profile_frame_count-1] = int(self.square_program.color) #stim_time
                self.stim_time_from_start_history[profile_frame_count-1] = self.get_stim_time(t)
                self.stim_time_history[profile_frame_count-1] = t #redundant with profile_frame_times, but to match lenght with other preallocated variables, kept here.
                self.global_fly_posx_history[profile_frame_count-1] = self.global_fly_pos[0]
                self.global_fly_posy_history[profile_frame_count-1] = self.global_fly_pos[1]
                self.global_theta_offset_history[self.profile_frame_count-1] = self.global_theta_offset
                #self.global_fly_posz_history[self.profile_frame_count-1] = self.global_fly_pos[2]
                #self.global_phi_offset_history[self.profile_frame_count-1] = self.global_phi_offset

        else:
            self.ctx.clear(self.idle_background, self.idle_background, self.idle_background, 1.0)


        # draw the corner square
        self.square_program.paint() #must come after saving history to match length??

        # update the window
        self.ctx.finish()
        self.update()

        # clear the buffer objects
        for stim in self.stim_list:
            if self.stim_started:
                stim.vbo.release()
                stim.vao.release()

        # print('paintGL {:.2f} ms'.format((time.time()-t0)*1000)) #benchmarking

    ###########################################
    # control functions
    ###########################################

    def set_fly_trajectory(self, x_trajectory, y_trajectory, theta_trajectory):
        """
        :param x_trajectory: meters, dict from Trajectory including time, value pairs
        :param y_trajectory: meters, dict from Trajectory including time, value pairs
        :param theta_trajectory: degrees on the azimuthal plane, dict from Trajectory including time, value pairs
        """
        self.use_fly_trajectory = True
        self.fly_x_trajectory = Trajectory.from_dict(x_trajectory)
        self.fly_y_trajectory = Trajectory.from_dict(y_trajectory)
        self.fly_theta_trajectory = Trajectory.from_dict(theta_trajectory)

    def load_stim(self, name, hold=False, **kwargs):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        """

        if hold is False:
            self.stim_list = []

        stim = getattr(stimuli, name)(screen=self.screen)
        stim.initialize(self.ctx)
        stim.kwargs = kwargs
        stim.configure(**stim.kwargs) #Configure stim on load
        self.stim_list.append(stim)

    def start_stim(self, t):
        """
        Starts the stimulus animation, using the given time as t=0
        :param t: Time corresponding to t=0 of the animation
        """

        self.profile_frame_times = []

        if self.save_history_flag:
            self.square_history = np.zeros(self.estimated_n_frames)
            self.stim_time_history = np.zeros(self.estimated_n_frames)
            self.stim_time_from_start_history = np.zeros(self.estimated_n_frames)
            self.global_fly_posx_history = np.zeros(self.estimated_n_frames)
            self.global_fly_posy_history = np.zeros(self.estimated_n_frames)
            self.global_theta_offset_history = np.zeros(self.estimated_n_frames)
            #self.global_fly_posz_history = np.zeros(self.estimated_n_frames)
            #self.global_phi_offset_history = np.zeros(self.estimated_n_frames)

        self.stim_started = True
        self.stim_start_time = t

    def stop_stim(self, print_profile=False):
        """
        Stops the stimulus animation and removes it from the display.
        """
        # clear texture
        self.ctx.clear_samplers()

        for stim in self.stim_list:
            stim.prog.release()

        # print profiling information if applicable

        if (print_profile):
            # filter out frame times of duration zero
            fps_data = np.diff(np.array(self.profile_frame_times))
            fps_data = fps_data[fps_data != 0]

            if len(fps_data) > 0:
                fps_data = pd.Series(1.0/fps_data)
                stim_names = ', '.join([type(stim).__name__ for stim in self.stim_list])
                if print_profile:
                    print('*** ' + stim_names + ' ***')
                    print(fps_data.describe(percentiles=[0.01, 0.05, 0.1, 0.9, 0.95, 0.99]))
                    print('*** end of statistics ***')

        # reset stim variables

        self.stim_list = []

        self.stim_started = False
        self.stim_start_time = None

        self.profile_frame_times = []

        self.use_fly_trajectory = False
        self.fly_x_trajectory = None
        self.fly_y_trajectory = None
        self.fly_theta_trajectory = None
        self.set_global_fly_pos(0, 0, 0)
        self.set_global_theta_offset(0)
        self.set_global_phi_offset(0)
        self.perspective = get_perspective(self.global_fly_pos, self.global_theta_offset, self.global_phi_offset, screen=self.screen)

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

    def set_save_path(self, save_path=""):
        if self.save_history_flag:
            self.save_path = save_path

    def set_save_prefix(self, save_prefix=""):
        if self.save_history_flag:
            self.save_prefix = save_prefix

    def set_save_history_params(self, save_history_flag=True, save_path="", save_prefix="", fs_frame_rate_estimate=120, stim_duration=65):
        self.save_history_flag = save_history_flag
        if save_history_flag:
            self.save_path = save_path
            self.save_prefix = save_prefix
            self.estimated_n_frames = fs_frame_rate_estimate * stim_duration
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


def get_perspective(fly_pos, theta, phi, screen):
    """
    :param fly_pos: (x, y, z) position of fly, meters
    :param theta: fly heading angle along azimuth, radians
    :param phi: fly heading angle along elevation, radians
    :param screen: flystim.screen object
    """
    pa = screen.tri_list[0].pa.cart  # [x, y, z] in meters
    pb = screen.tri_list[0].pb.cart
    pc = screen.tri_list[0].pc.cart

    perspective = GenPerspective(pa=pa, pb=pb, pc=pc, fly_pos=fly_pos)

    """
    rotate screen and eye position
    Absent any change in fly heading,  (i.e. theta, phi = 0, 0) fly is looking
    down the positive x axis and above the fly is +z
    +theta is ccw around z axis, -theta is cw around z axis (looking down at xy plane)
    -phi tilts fly view up towards the sky (+z), +phi tilts down towards the ground (-z)

    """
    return perspective.roty(phi).rotx(radians(0)).rotz(radians(0)+theta).matrix


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
    server.register_function(stim_display.set_fly_trajectory)
    server.register_function(stim_display.load_stim)
    server.register_function(stim_display.start_stim)
    server.register_function(stim_display.stop_stim)
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
