from PyQt5 import QtOpenGL, QtWidgets

import time
import sys
import signal
import moderngl
import logging

from argparse import ArgumentParser
from jsonrpc import Dispatcher

from flystim.stimuli import RotatingBars, ExpandingEdges, RandomBars, SequentialBars, SineGrating, RandomGrid
from flystim.stimuli import Checkerboard, MovingPatch

from flystim.square import SquareProgram

from flystim.screen import Screen
from flystim.rpc import Server

class StimDisplay(QtOpenGL.QGLWidget):
    """
    Class that controls the stimulus display on one screen.  It contains the pyglet window object for that screen,
    and also controls rendering of the stimulus, toggling corner square, and/or debug information.
    """

    def __init__(self, screen, server):
        """
        :param screen: Screen object (from flystim.screen) corresponding to the screen on which the stimulus will
        be displayed.
        """

        # call super constructor
        super().__init__(make_qt_format(vsync=screen.vsync))

        # configure window to reside on a specific screen
        # re: https://stackoverflow.com/questions/6854947/how-to-display-a-window-on-a-secondary-display-in-pyqt
        desktop = QtWidgets.QDesktopWidget()
        rectScreen = desktop.screenGeometry(screen.id)
        self.move(rectScreen.left(), rectScreen.top())
        self.resize(rectScreen.width(), rectScreen.height())

        # stimulus initialization
        self.stim = None

        # stimulus state
        self.stim_started = False
        self.stim_start_time = None

        # profiling information
        self.profile_frame_count = None
        self.profile_start_time = None
        self.profile_last_time = None
        self.profile_frame_times = None

        # save handles to screen and server
        self.screen = screen
        self.server = server

        # make OpenGL programs that are used by stimuli
        cls_list = [RotatingBars, ExpandingEdges, RandomBars, SequentialBars, SineGrating, RandomGrid,
                    MovingPatch, Checkerboard]
        self.render_programs = {cls.__name__: cls(screen=screen) for cls in cls_list}

        # make program for rendering the corner square
        self.square_program = SquareProgram(screen=screen)

        # initialize background color
        self.idle_background = 0.5

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context()

        # initialize stimuli programs
        for render_program in self.render_programs.values():
            render_program.initialize(self.ctx)

        # initialize square program
        self.square_program.initialize(self.ctx)

    def paintGL(self):
        # handle RPC input
        self.server.process()

        # set the viewport to fill the window
        # ref: https://github.com/pyqtgraph/pyqtgraph/issues/422
        self.ctx.viewport = (0, 0, self.width()*self.devicePixelRatio(), self.height()*self.devicePixelRatio())

        # draw the stimulus
        if self.stim is not None:
            if self.stim_started:
                t = time.time()
                self.stim.paint_at(t-self.stim_start_time)
                self.profile_frame_count += 1

                if (self.profile_last_time is not None) and (self.profile_frame_times is not None):
                    self.profile_frame_times.append(t - self.profile_last_time)

                self.profile_last_time = t
            else:
                self.stim.paint_at(0)
        else:
            self.ctx.clear(self.idle_background, self.idle_background, self.idle_background)

        # draw the corner square
        self.square_program.paint()

        # update the window
        self.update()

    ###########################################
    # control functions
    ###########################################

    def load_stim(self, name, *args, **kwargs):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        """

        self.stim = self.render_programs[name]
        self.stim.configure(*args, **kwargs)

    def start_stim(self, t):
        """
        Starts the stimulus animation, using the given time as t=0
        :param t: Time corresponding to t=0 of the animation
        """

        self.stim_started = True
        self.stim_start_time = t

        self.profile_frame_count = 0
        self.profile_start_time = time.time()

        self.profile_last_time = None
        self.profile_frame_times = []

    def stop_stim(self):
        """
        Stops the stimulus animation and removes it from the display.
        """

        # print profiling information if applicable

        if ((self.profile_frame_count is not None) and
            (self.profile_start_time is not None) and
            (self.stim is not None)):

            profile_duration = time.time() - self.profile_start_time
            if profile_duration > 0:
                logging.info('{} ({}): ave {:0.1f}, min {:0.1f}, max {:0.1f} fps'.format(
                    self.stim.__class__.__name__,
                    self.screen.name,
                    self.profile_frame_count / profile_duration,
                    1.0 / max(self.profile_frame_times),
                    1.0 / min(self.profile_frame_times) if min(self.profile_frame_times) != 0 else -1,
                    )
                )

        # reset stim variables

        self.stim = None

        self.stim_started = False
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

    return format


def main():
    """
    This file is typically run as a command-line program launched as a Subprocess, so the command-line arguments
    are typically filled by the launching program, rather than explictly by a user.
    """

    ####################################
    # Set up logging
    ####################################

    logging.basicConfig(level=logging.DEBUG)

    ####################################
    # Create QApplication
    ####################################

    app = QtWidgets.QApplication([])

    ####################################
    # initialize the stimulus display
    ####################################

    # set up command line parser
    parser = ArgumentParser()
    parser.add_argument('--id', type=int)
    parser.add_argument('--name', type=str)
    parser.add_argument('--width', type=float)
    parser.add_argument('--height', type=float)
    parser.add_argument('--rotation', type=float)
    parser.add_argument('--offset', type=float, nargs=3)
    parser.add_argument('--square_loc', type=str)
    parser.add_argument('--square_side', type=float)
    parser.add_argument('--fullscreen', action='store_true')
    parser.add_argument('--vsync', action='store_true')

    # parse command line arguments
    args = parser.parse_args()

    # create the screen object used to pass arguments into StimDisplay constructor
    screen = Screen(id=args.id, name=args.name, width=args.width, height=args.height, rotation=args.rotation,
                    offset=args.offset, fullscreen=args.fullscreen, vsync=args.vsync, square_side=args.square_side,
                    square_loc=args.square_loc)

    # create a dispatcher to keep track of RPC methods
    dispatcher = Dispatcher()

    # create the StimDisplay object
    stim_display = StimDisplay(screen=screen, server=Server(dispatcher))

    # register functions
    dispatcher.add_method(stim_display.load_stim)
    dispatcher.add_method(stim_display.start_stim)
    dispatcher.add_method(stim_display.stop_stim)
    dispatcher.add_method(stim_display.start_corner_square)
    dispatcher.add_method(stim_display.stop_corner_square)
    dispatcher.add_method(stim_display.white_corner_square)
    dispatcher.add_method(stim_display.black_corner_square)
    dispatcher.add_method(stim_display.set_corner_square)
    dispatcher.add_method(stim_display.show_corner_square)
    dispatcher.add_method(stim_display.hide_corner_square)
    dispatcher.add_method(stim_display.set_idle_background)

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
