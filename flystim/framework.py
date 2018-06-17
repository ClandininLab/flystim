from PyQt5 import QtOpenGL, QtWidgets

import time
import moderngl

from argparse import ArgumentParser

from flystim.bars import BarProgram
from flystim.sine import SineProgram
from flystim.stimuli import RotatingBars, ExpandingEdges, GaussianNoise, SequentialBars, SineGrating

from flystim.square import SquareProgram

from flystim.screen import Screen
from flystim.rpc import RpcServer

class StimDisplay(QtOpenGL.QGLWidget):
    """
    Class that controls the stimulus display on one screen.  It contains the pyglet window object for that screen,
    and also controls rendering of the stimulus, toggling corner square, and/or debug information.
    """

    def __init__(self, screen):
        """
        :param screen: Screen object (from flystim.screen) corresponding to the screen on which the stimulus will
        be displayed.
        :param square_pos: Position of the square (lr, ll, ur, ul)
        :param square_side: Side length of the corner square, in meters.  Note that in order for the displayed length
        to be correct, the dimensions provided in the screen object must be right...
        """

        # call super constructor
        super().__init__(make_qt_format(vsync=screen.vsync))

        # configure window
        # TODO: allow other window sizes
        self.setFixedSize(1280, 720)

        # stimulus initialization
        self.stim = None

        # stimulus state
        self.stim_started = False
        self.stim_start_time = None

        # make RPC handler
        self.rpc_server = self.make_rpc_server()

        # make OpenGL programs that are used by stimuli
        self.bar_program = BarProgram(screen=screen)
        self.sine_program = SineProgram(screen=screen)
        self.square_program = SquareProgram(screen=screen)

        # background color
        self.set_idle_background_color(0.5, 0.5, 0.5)

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context()

        # initialize rendering programs
        self.bar_program.initialize(self.ctx)
        self.sine_program.initialize(self.ctx)
        self.square_program.initialize(self.ctx)

    def paintGL(self):
        # handle RPC input
        self.rpc_server.update()

        # draw the stimulus
        if self.stim is not None:
            if self.stim_started:
                self.stim.paint_at(time.time()-self.stim_start_time)
            else:
                self.stim.paint_at(0)
        else:
            self.ctx.clear(*self.idle_background_color)

        # draw the corner square
        self.square_program.paint()

        # update the window
        self.update()

    ###########################################
    # control functions
    ###########################################

    def load_stim(self, name, params):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        :param params: Parameters used to instantiate the class (e.g., period, bar width, etc.)
        """

        if name == 'RotatingBars':
            self.stim = RotatingBars(program=self.bar_program, **params)
        elif name == 'ExpandingEdges':
            self.stim = ExpandingEdges(program=self.bar_program, **params)
        elif name == 'GaussianNoise':
            self.stim = GaussianNoise(program=self.bar_program, **params)
        elif name == 'SequentialBars':
            self.stim = SequentialBars(program=self.bar_program, **params)
        elif name == 'SineGrating':
            self.stim = SineGrating(program=self.sine_program, **params)
        else:
            raise ValueError('Invalid stimulus.')

    def start_stim(self, t):
        """
        Starts the stimulus animation, using the given time as t=0
        :param t: Time corresponding to t=0 of the animation
        """

        self.stim_started = True
        self.stim_start_time = t

    def stop_stim(self):
        """
        Stops the stimulus animation and removes it from the display.  The background color reverts to idle_background
        """

        self.stim = None

        self.stim_started = False
        self.stim_start_time = None

    # corner square options

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
        Make the corner square white.
        """

        self.square_program.color = 1.0

    def black_corner_square(self):
        """
        Make the corner square black.
        """

        self.square_program.color = 0.0

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

    # background color

    def set_idle_background_color(self, r, g, b):
        """
        Sets the RGB color of the background when there is no stimulus being displayed (sometimes called the
        interleave period).
        """

        self.idle_background_color = (r, g, b)

    ###########################################
    # initialization functions
    ###########################################

    def make_rpc_server(self):
        # create the RpcServer object
        rpc_server = RpcServer()

        # stimulus control functions
        rpc_server.register_function(self.load_stim, 'load_stim')
        rpc_server.register_function(self.start_stim, 'start_stim')
        rpc_server.register_function(self.stop_stim, 'stop_stim')

        # corner square control functions
        rpc_server.register_function(self.start_corner_square, 'start_corner_square')
        rpc_server.register_function(self.stop_corner_square, 'stop_corner_square')
        rpc_server.register_function(self.white_corner_square, 'white_corner_square')
        rpc_server.register_function(self.black_corner_square, 'black_corner_square')
        rpc_server.register_function(self.show_corner_square, 'show_corner_square')
        rpc_server.register_function(self.hide_corner_square, 'hide_corner_square')

        # background control functions
        rpc_server.register_function(self.set_idle_background_color, 'set_idle_background_color')

        return rpc_server


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
    # Create QApplication
    ####################################

    app = QtWidgets.QApplication([])

    ####################################
    # initialize the stimulus display
    ####################################

    # set up command line parser
    parser = ArgumentParser()
    parser.add_argument('--id', type=int)
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
    screen = Screen(id=args.id, width=args.width, height=args.height, rotation=args.rotation,
                    offset=args.offset, fullscreen=args.fullscreen, vsync=args.vsync,
                    square_side=args.square_side, square_loc=args.square_loc)

    # create the StimDisplay object
    stim_display = StimDisplay(screen=screen)
    stim_display.show()

    ####################################
    # Run QApplication
    ####################################

    # Use Ctrl+C to exit.
    try:
        app.exec_()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
