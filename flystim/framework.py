from PyQt6 import QtOpenGL, QtWidgets, QtOpenGLWidgets, QtGui

import time
import sys
import signal
import moderngl
import numpy as np
import pandas as pd
import platform
import qimage2ndarray
from skimage.transform import downscale_local_mean

from flystim import stimuli
from flystim.trajectory import make_as_trajectory, return_for_time_t

from flystim.perspective import GenPerspective
from flystim.square import SquareProgram
from flystim.screen import Screen
from math import radians

from flyrpc.transceiver import MySocketServer
from flyrpc.util import get_kwargs


class StimDisplay(QtOpenGLWidgets.QOpenGLWidget): #class StimDisplay(QtOpenGL.QGLWidget):
    """
    Class that controls the stimulus display on one screen.  It contains the pyglet window object for that screen,
    and also controls rendering of the stimulus, toggling corner square, and/or debug information.
    """

    def __init__(self, screen, server, app):
        """
        Initialize the StimDisplay obect.

        :param screen: Screen object (from flystim.screen) corresponding to the screen on which the stimulus will
        be displayed.
        """

        # call super constructor
        super().__init__()

        # In PyQt6, need to set the format after init.
        qt_format = make_qt_format(vsync=screen.vsync)
        QtGui.QSurfaceFormat.setDefaultFormat(qt_format)
        self.setFormat(qt_format)
        self.setUpdateBehavior(QtOpenGLWidgets.QOpenGLWidget.UpdateBehavior.PartialUpdate)

        # configure window to reside on a specific screen
        # re: https://stackoverflow.com/questions/6854947/how-to-display-a-window-on-a-secondary-display-in-pyqt
        if platform.system() == 'Windows':
            desktop = QtGui.QScreen() #desktop = QtWidgets.QDesktopWidget()
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

        # Initialize stuff for rendering & saving stim frames
        self.stim_frames = []
        self.append_stim_frames = False

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

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context() # TODO: can we make this run headless in render_movie_mode?
        self.ctx.enable(moderngl.BLEND) # enable alpha blending
        self.ctx.enable(moderngl.DEPTH_TEST) # enable depth test

        # initialize square program
        self.square_program.initialize(self.ctx)

    def get_stim_time(self, t):
        stim_time = 0

        if self.stim_started:
            stim_time += t - self.stim_start_time

        return stim_time

    def clear_viewport(self, viewport):
        self.ctx.clear(red=self.idle_background, green=self.idle_background, blue=self.idle_background, alpha=1.0, viewport=viewport)

    def paintGL(self):
        # t0 = time.time() # benchmarking

        # quit if desired
        if self.server.shutdown_flag.is_set():
            self.app.quit()

        # handle RPC input
        self.server.process_queue()

        # get display size and set viewports
        display_width = self.width()*self.devicePixelRatio()
        display_height = self.height()*self.devicePixelRatio()

        self.subscreen_viewports = [sub.get_viewport(display_width, display_height) for sub in self.screen.subscreens]
        # Get viewport for corner square
        self.square_program.set_viewport(display_width, display_height)

        self.ctx.clear(0, 0, 0, 1) # clear the previous frame across the whole display
        # draw the stimulus
        if self.stim_list:
            t = time.time()
            if self.use_fly_trajectory:
                self.set_global_fly_pos(return_for_time_t(self.fly_x_trajectory, self.get_stim_time(t)),
                                        return_for_time_t(self.fly_y_trajectory, self.get_stim_time(t)),
                                        0)
                self.set_global_theta_offset(return_for_time_t(self.fly_theta_trajectory, self.get_stim_time(t)))  # deg -> radians

            # For each subscreen associated with this screen: get the perspective matrix
            perspectives = [get_perspective(self.global_fly_pos, self.global_theta_offset, self.global_phi_offset, x.pa, x.pb, x.pc, self.screen.horizontal_flip) for x in self.screen.subscreens]

            for stim in self.stim_list:
                if self.stim_started:
                    stim.paint_at(self.get_stim_time(t),
                                  self.subscreen_viewports,
                                  perspectives,
                                  fly_position=self.global_fly_pos.copy(),
                                  fly_heading=[self.global_theta_offset+0, self.global_phi_offset+0])
                else:
                    [self.clear_viewport(viewport=x) for x in self.subscreen_viewports]

            self.profile_frame_times.append(t)
        else:
            [self.clear_viewport(viewport=x) for x in self.subscreen_viewports]

        # draw the corner square
        self.square_program.paint()

        # update the window
        self.ctx.finish()
        self.update()

        # clear the buffer objects
        for stim in self.stim_list:
            if self.stim_started:
                stim.vbo.release()
                stim.vao.release()

        if self.stim_started:
            # print('paintGL {:.2f} ms'.format((time.time()-t0)*1000)) #benchmarking

            if self.append_stim_frames:
                # grab frame buffer, convert to array, grab blue channel, append to list of stim_frames
                self.stim_frames.append(qimage2ndarray.rgb_view(self.grabFrameBuffer())[:, :, 2])

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
        self.fly_x_trajectory = make_as_trajectory(x_trajectory)
        self.fly_y_trajectory = make_as_trajectory(y_trajectory)
        self.fly_theta_trajectory = make_as_trajectory(theta_trajectory)

    def load_stim(self, name, hold=False, **kwargs):
        """
        Load the stimulus with the given name, using the given params.

        After the stimulus is loaded, the background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        """
        if hold is False:
            self.stim_list = []

        stim = getattr(stimuli, name)(screen=self.screen)
        stim.initialize(self.ctx)
        stim.kwargs = kwargs
        stim.configure(**stim.kwargs) # Configure stim on load
        self.stim_list.append(stim)

    def start_stim(self, t, append_stim_frames=False):
        """
        Start the stimulus animation, using the given time as t=0.

        :param t: Time corresponding to t=0 of the animation
        :param append_stim_frames: bool, append frames to stim_frames list, for saving stim movie. May affect performance.
        """
        self.profile_frame_times = []
        self.stim_frames = []
        self.append_stim_frames = append_stim_frames

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
        self.perspective = get_perspective(self.global_fly_pos, self.global_theta_offset, self.global_phi_offset, self.screen.subscreens[0].pa, self.screen.subscreens[0].pb, self.screen.subscreens[0].pc, self.screen.horizontal_flip)

    def save_rendered_movie(self, file_path, downsample_xy=4):
        """
        Save rendered stim frames from stim_frames as 3D np array
        Must be used with append_stim_frames in start_stim

        :param file_path: full file path of saved array
        """
        pre_size = np.stack(self.stim_frames, axis=2).shape
        mov = downscale_local_mean(np.stack(self.stim_frames, axis=2), factors=(downsample_xy, downsample_xy, 1)).astype('uint8')
        np.save(file_path, mov)
        print('Downsampled from {} to {} and saved to {}'.format(pre_size, mov.shape, file_path), flush=True)

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


def get_perspective(fly_pos, theta, phi, pa, pb, pc, horizontal_flip):
    """
    :param fly_pos: (x, y, z) position of fly, meters
    :param theta: fly heading angle along azimuth, degrees
    :param phi: fly heading angle along elevation, degrees
    :params (pa, pb, pc): xyz coordinates of screen corners, meters
    :param horizontal_flip: Boolean, apply horizontal flip to image, for rear-projection displays
    """

    perspective = GenPerspective(pa=pa, pb=pb, pc=pc, fly_pos=fly_pos, horizontal_flip=horizontal_flip)

    """
    With (theta, phi, roll) = (0, 0, 0): fly looks down +y axis, +x is to the right, and +z is above the fly's head
        +theta rotates view ccw around z axis / -theta is cw around z axis (looking down at xy plane)
        +phi tilts fly view up towards the sky (+z) / -phi tilts down towards the ground (-z)
        +roll rotates fly view cw around y axis / -roll rotates ccw around y axis

    theta = yaw around z
    phi = pitch around x
    roll = roll around y

    """
    roll = 0 # Set roll=0 until we have a need too change it
    return perspective.rotz(theta).rotx(radians(phi)).roty(radians(roll)).matrix


def make_qt_format(vsync):
    """
    Initializes the Qt OpenGL format.
    :param vsync: If True, use VSYNC, otherwise update as fast as possible
    """

    # create format with default settings
    format = QtGui.QSurfaceFormat() #format = QtOpenGL.QGLFormat()

    # use OpenGL 3.3
    format.setVersion(3, 3)
    format.setProfile(QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile) #format.setProfile(QtOpenGL.QGLFormat.CoreProfile)

    # use VSYNC
    if vsync:
        format.setSwapInterval(1)
    else:
        format.setSwapInterval(0)

    # TODO: determine what these lines do and whether they are necessary
    format.setSamples(8) # format.setSampleBuffers(True)
    format.setDepthBufferSize(24)

    # needed to enable transparency and each color inidividually??
    format.setRedBufferSize(8)
    format.setGreenBufferSize(8)
    format.setBlueBufferSize(8)
    format.setRedBufferSize(8)
    format.setAlphaBufferSize(8) #format.setAlpha(True)

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
    server.register_function(stim_display.save_rendered_movie)
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
    sys.exit(app.exec()) #sys.exit(app.exec_())

if __name__ == '__main__':
    main()
