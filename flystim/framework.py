import pyglet
import pyglet.gl as gl
import time
import numpy as np

from argparse import ArgumentParser

from flystim import graphics
from flystim import cylinder

from flystim.screen import Screen
from flystim.projection import Projection
from flystim.rpc import RpcServer

class StimDisplay:
    """
    Class that controls the stimulus display on one screen.  It contains the pyglet window object for that screen,
    and also controls rendering of the stimulus, toggling corner square, and/or debug information.
    """

    def __init__(self, screen, draw_text=True):
        """
        :param screen: Screen object (from flystim.screen) corresponding to the screen on which the stimulus will
        be displayed.
        :param draw_text: Boolean.  If True, draw debug information (FPS, screen ID#, etc.).
        """

        # save settings
        self.screen = screen
        self.draw_text = draw_text

        # stimulus initialization
        self.stim = None
        self.stim_started = False
        self.stim_start_time = None

        # projection matrix initialization
        self.projection = Projection(screen=screen)
        self.gl_proj_mat = (gl.GLfloat * 16)(*self.projection.mat.flatten('F'))

        # initialize the window
        self.init_window()

        # initialize corner square
        self.init_corner_square()

        # initialize text labels
        self.init_text_labels()

        # background color
        self.set_idle_background(0.5, 0.5, 0.5)
        self.set_background_color(*self.idle_background)

        # draw objects
        @self.window.event
        def on_draw():
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            ###################
            # 3D drawing
            ###################

            # load the perspective-corrected projection matrix
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadMatrixf(self.gl_proj_mat)

            # load the model view matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            # draw stimulus
            if self.stim is not None:
                self.stim.draw()

            ###################
            # 2D drawing
            ###################

            # load the orthographic projection matrix
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            gl.glOrtho(0, self.window.width, 0, self.window.height, -1, 1)

            # load the model view matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            # draw corner square
            self.corner_square.draw()
            self.toggle_corner_square()

            # draw debug text
            if self.draw_text:
                for text_label in self.text_labels:
                    text_label.draw()

    ###########################################
    # scheduled functions
    ###########################################

    def update(self):
        if self.stim is not None and self.stim_started:
            self.stim.eval_at(time.time()-self.stim_start_time)

    ###########################################
    # control functions
    ###########################################

    # stimulus options

    def load_stim(self, name, params):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        :param params: Parameters used to instantiate the class (e.g., period, bar width, etc.)
        """

        if name == 'RotatingBars':
            self.stim = cylinder.RotatingBars(**params)
        elif name == 'ExpandingEdges':
            self.stim = cylinder.ExpandingEdges(**params)
        elif name == 'GaussianNoise':
            self.stim = cylinder.GaussianNoise(**params)
        elif name == 'SequentialBars':
            self.stim = cylinder.SequentialBars(**params)
        else:
            raise ValueError('Invalid class name.')

        self.set_background_color(*self.stim.background)
        self.stim.eval_at(0)

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

        self.set_background_color(*self.idle_background)

    # corner square options

    def toggle_corner_square(self):
        """
        Flips the color of the corner square from black to white or vice versa.
        """

        self.corner_square.color_data = [1 - elem for elem in self.corner_square.color_data]

    # background color

    def set_idle_background(self, r, g, b):
        """
        Sets the RGB color of the background when there is no stimulus being displayed (sometimes called the
        interleave period).
        """

        self.idle_background = (r, g, b)

    def set_background_color(self, r, g, b):
        """
        Sets the background color to the given RGB value.  Takes effect next time the glClear function is called.
        """

        gl.glClearColor(r, g, b, 0)

    ###########################################
    # initialization functions
    ###########################################

    def init_window(self):
        """
        Creates a pyglet window on the specified screen.  Can be fullscreen or windowed.
        """

        display = pyglet.window.get_platform().get_default_display()
        screen = display.get_screens()[self.screen.id]

        self.window = pyglet.window.Window(screen=screen, fullscreen=self.screen.fullscreen)

    def init_corner_square(self, square_side=2e-2):
        """
        Creates a graphics object for the toggling corner square used to monitor for dropped frames.
        :param square_side: Side length of the corner square, in meters.  Note that in order for the displayed length
        to be correct, the dimensions provided in the screen object must be right...
        """

        if self.screen.id == 1:
        # corner square in bottom right
            urx = self.window.width
            ury = self.window.height/self.screen.height * square_side

            # compute lower left corner coordinates
            llx = urx - self.window.width/self.screen.width * square_side
            lly = 0

        elif self.screen.id == 2:
        # corner square in bottom left
            urx = self.window.width/self.screen.width * square_side
            ury = self.window.height/self.screen.height * square_side

            # compute lower left corner coordinates
            llx = 0
            lly = 0
        else:
            urx = self.window.width
            ury = self.window.height/self.screen.height * square_side

            # compute lower left corner coordinates
            llx = urx - self.window.width/self.screen.width * square_side
            lly = 0

        # create corner square graphics object
        self.corner_square = graphics.Item2D(gl.GL_QUADS)

        # fill corner square information
        self.corner_square.vertex_data = [llx, lly, urx, lly, urx, ury, llx, ury]
        self.corner_square.color_data = [1]*12

    def init_text_labels(self):
        """
        Creates labels used for debug purposes (e.g., frames per second, the ID # of the screen, etc.)
        """

        self.text_labels = []

        # FPS display
        clock_display = pyglet.window.FPSDisplay(self.window)
        self.text_labels.append(clock_display)

        # Screen ID
        id_label = pyglet.text.Label(
            'ID: {:d}'.format(self.screen.id),
            x = self.window.width - 10,
            y = 10,
            font_size = 24,
            bold = True,
            color = (127, 127, 127, 127),
            anchor_x = 'right'
        )
        self.text_labels.append(id_label)

class StimControl(RpcServer):
    """
    Class to interpret incoming remote procedure calls from a PIPE and relay them to the StimDisplay class.
    """

    def __init__(self, stim_display):
        """
        :param stim_display: StimDisplay object to be controlled by the RPCs.
        """

        # save settings
        self.stim_display = stim_display

        # call super constructor
        super().__init__()

    def handle(self, method, args):
        """
        Mapping from method name to StimDisplay functions.
        :param method: Name of the method.
        :param args: List of positional arguments to be passed to the method.
        :return:
        """

        if method == 'load_stim':
            self.stim_display.load_stim(*args)
        elif method == 'start_stim':
            self.stim_display.start_stim(*args)
        elif method == 'stop_stim':
            self.stim_display.stop_stim(*args)
        else:
            raise ValueError('Invalid method.')

def main():
    """
    This file is typically run as a command-line program launched as a Subprocess, so the command-line arguments
    are typically filled by the launching program, rather than explictly by a user.
    """

    # set up command line parser
    parser = ArgumentParser()
    parser.add_argument('--id', type=int)
    parser.add_argument('--pa', type=float, nargs=3)
    parser.add_argument('--pb', type=float, nargs=3)
    parser.add_argument('--pc', type=float, nargs=3)
    parser.add_argument('--fullscreen', action='store_true')

    # parse command line arguments
    args = parser.parse_args()

    # initialize the display
    pa = np.array(args.pa, dtype=float)
    pb = np.array(args.pb, dtype=float)
    pc = np.array(args.pc, dtype=float)
    screen = Screen(id=args.id, pa=pa, pb=pb, pc=pc, fullscreen=args.fullscreen)
    stim_display = StimDisplay(screen=screen)

    # initialize the control handler
    stim_control = StimControl(stim_display)

    # schedule regular tasks
    # the dt argument is required by pyglet but not used
    # in this code base
    pyglet.clock.schedule(lambda dt: stim_display.update())
    pyglet.clock.schedule(lambda dt: stim_control.update())

    # Run application
    # Use Ctrl+C to exit.
    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
