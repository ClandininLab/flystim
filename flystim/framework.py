import pyglet
import pyglet.gl as gl
import time

from argparse import ArgumentParser

from flystim import graphics
from flystim import cylinder

from flystim.screen import Screen
from flystim.projection import Projection
from flystim.rpc import RpcServer

class StimDisplay:
    def __init__(self, screen, draw_text=True):
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
        self.set_idle_background(0.0, 0.0, 0.0)
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

        # handle escape key
        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.ESCAPE:
                self.close()

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

    def load_stim(self, name, *args, **kwargs):
        if name == 'RotatingBars':
            self.stim = cylinder.RotatingBars(*args, **kwargs)
        elif name == 'ExpandingEdges':
            self.stim = cylinder.ExpandingEdges(*args, **kwargs)
        elif name == 'GaussianNoise':
            self.stim = cylinder.GaussianNoise(*args, **kwargs)
        elif name == 'SequentialBars':
            self.stim = cylinder.SequentialBars(*args, **kwargs)
        else:
            raise ValueError('Invalid class name.')

        self.set_background_color(*self.stim.background)
        self.stim.eval_at(0)

    def start_stim(self, t):
        self.stim_started = True
        self.stim_start_time = t

    def stop_stim(self):
        self.stim = None
        self.stim_started = False
        self.stim_start_time = None

        self.set_background_color(*self.idle_background)

    def close(self):
        self.window.close()

    # debug options

    def show_text(self):
        self.draw_text = True

    def hide_text(self):
        self.draw_text = False

    # corner square options

    def toggle_corner_square(self):
        self.corner_square.color_data = [1 - elem for elem in self.corner_square.color_data]

    # background color

    def set_idle_background(self, r, g, b):
        self.idle_background = (r, g, b)

    def set_background_color(self, r, g, b):
        gl.glClearColor(r, g, b, 0)

    ###########################################
    # initialization functions
    ###########################################

    def init_window(self):
        display = pyglet.window.get_platform().get_default_display()
        screen = display.get_screens()[self.screen.id]

        self.window = pyglet.window.Window(screen=screen, fullscreen=False)

    def init_corner_square(self, square_side=0.5e-2):
        # compute upper right corner coordinates
        urx = self.window.width
        ury = self.window.height

        # compute lower left corner coordinates
        llx = urx - self.window.width/self.screen.width * square_side
        lly = ury - self.window.height/self.screen.height * square_side

        # create corner square graphics object
        self.corner_square = graphics.Item2D(gl.GL_QUADS)

        # fill corner square information
        self.corner_square.vertex_data = [llx, lly, urx, lly, urx, ury, llx, ury]
        self.corner_square.color_data = [1]*12

    def init_text_labels(self):
        self.text_labels = []

        # FPS display
        # TODO: customize its display
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
    def __init__(self, stim_display):
        # save settings
        self.stim_display = stim_display

        # call super constructor
        super().__init__()

    def handle(self, method, args, kwargs):
        if method == 'load_stim':
            self.stim_display.load_stim(*args, **kwargs)
        elif method == 'start_stim':
            self.stim_display.start_stim(*args, **kwargs)
        elif method == 'stop_stim':
            self.stim_display.stop_stim(*args, **kwargs)
        else:
            raise ValueError('Invalid method.')

class StimArgParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # monitor physical definition
        # defaults are for MacBook Pro (Retina, 15-inch, Mid 2015)
        self.add_argument('--id', type=int, default=0)
        self.add_argument('--pa', type=float, nargs=3, default=[-0.166, -0.1035, -0.3])
        self.add_argument('--pb', type=float, nargs=3, default=[+0.166, -0.1035, -0.3])
        self.add_argument('--pc', type=float, nargs=3, default=[-0.166, +0.1035, -0.3])

def main():
    # parse command line arguments
    parser = StimArgParser()
    args = parser.parse_args()

    # initialize the display
    screen = Screen(id=args.id, pa=args.pa, pb=args.pb, pc=args.pc)
    stim_display = StimDisplay(screen=screen)

    # initialize the control handler
    stim_control = StimControl(stim_display)

    # schedule regular tasks
    # the dt argument is required by pyglet but not used
    # in this code base
    pyglet.clock.schedule(lambda dt: stim_display.update())
    pyglet.clock.schedule(lambda dt: stim_control.update())

    # run the application
    pyglet.app.run()

if __name__ == '__main__':
    main()