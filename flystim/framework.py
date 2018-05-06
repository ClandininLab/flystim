import pyglet
import pyglet.gl as gl
import numpy as np
import time

# handle I/O
import sys
import json
from threading import Thread
from queue import Queue, Empty
from argparse import ArgumentParser

from flystim import graphics
from flystim import cylinder

class StimDisplay:
    def __init__(self, id, pa, pb, pc, draw_debug_info=True, in_pipe=None):
        # save settings
        self.id = id
        self.pa = StimDisplay.vec(pa)
        self.pb = StimDisplay.vec(pb)
        self.pc = StimDisplay.vec(pc)
        self.draw_debug_info = draw_debug_info
        self.in_pipe = in_pipe

        # stimulus initialization
        self.stim = None
        self.stim_started = False
        self.stim_start_time = None

        # initialize normal vectors
        self.init_norm_vecs()

        # set initial eye position
        # (this will trigger a projection matrix update)
        self.set_pe(0, 0, 0)

        # initialize the window
        self.init_window()

        # initialize PD square
        # (requires the window to have been initialized)
        self.init_pd_square()

        # miscellaneous initialization
        self.idle_background_color = (0.0, 0.0, 0.0)
        self.set_background_color(*self.idle_background_color)
        self.init_clock_display()

        # initialize the ID label
        self.init_id_label()

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

            # draw PD square
            self.pd_square.draw()
            self.toggle_pd_square()

            if self.draw_debug_info:
                self.id_label.draw()
                self.clock_display.draw()

        # handle escape key
        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.ESCAPE:
                self.window.close()

    ###########################################
    # scheduled functions
    ###########################################

    def update(self, dt):
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

        self.set_background_color(*self.stim.background_color)
        self.stim.eval_at(0)

    def start_stim(self, t):
        self.stim_started = True
        self.stim_start_time = t

    def stop_stim(self):
        self.stim = None
        self.stim_started = False
        self.stim_start_time = None

        self.set_background_color(*self.idle_background_color)

    # debug options

    def show_debug_info(self):
        self.draw_debug_info = True

    def hide_debug_info(self):
        self.draw_debug_info = False

    # photodiode square options

    def toggle_pd_square(self):
        self.pd_square.color_data = [1 - elem for elem in self.pd_square.color_data]

    # background color

    def set_idle_background_color(self, r, g, b):
        self.idle_background_color = (r, g, b)

    def set_background_color(self, r, g, b):
        gl.glClearColor(r, g, b, 0)

    # eye position

    def set_pe(self, x, y, z):
        self.pe = StimDisplay.vec([x, y, z])
        self.update_proj_mat()

    ###########################################
    # initialization functions
    ###########################################

    def init_window(self):
        display = pyglet.window.get_platform().get_default_display()
        screen = display.get_screens()[self.id]

        self.window = pyglet.window.Window(screen=screen, fullscreen=False)

    def init_pd_square(self, square_side=0.5e-2):
        self.pd_square = graphics.Item2D(gl.GL_QUADS)

        # compute upper right corner coordinates
        urx = self.window.width
        ury = self.window.height

        # compute lower left corner coordinates
        llx = urx - self.window.width/self.screen_width * square_side
        lly = ury - self.window.height/self.screen_height * square_side

        # compute vertices of the square
        self.pd_square.vertex_data = [llx, lly, urx, lly, urx, ury, llx, ury]

        # compute colors of the vertices
        self.pd_square.color_data = [1]*12

    def init_clock_display(self):
        self.clock_display = pyglet.window.FPSDisplay(self.window)

    def init_id_label(self):
        self.id_label = pyglet.text.Label(
            'ID: {:d}'.format(self.id),
            x = self.window.width - 10,
            y = 10,
            font_size = 24,
            bold = True,
            color = (127, 127, 127, 127),
            anchor_x = 'right'
        )

    def init_norm_vecs(self):
        # ref: http://csc.lsu.edu/~kooima/articles/genperspective/

        self.vr = self.pb - self.pa
        self.screen_width = np.linalg.norm(self.vr)
        self.vr /= self.screen_width

        self.vu = self.pc - self.pa
        self.screen_height = np.linalg.norm(self.vu)
        self.vu /= self.screen_height

        self.vn = np.cross(self.vr, self.vu)
        self.vn /= np.linalg.norm(self.vn)

        # Rotation matrix
        self.M = np.array([
            [self.vr[0], self.vu[0], self.vn[0], 0],
            [self.vr[1], self.vu[1], self.vn[1], 0],
            [self.vr[2], self.vu[2], self.vn[2], 0],
            [0, 0, 0, 1]], dtype=float)

    ###########################################
    # projection matrix calculation
    ###########################################

    def update_proj_mat(self, n=1e-2, f=100):
        # function should be called whenever pe is updated
        # ref: http://csc.lsu.edu/~kooima/articles/genperspective/

        # Determine frustum extents
        va = self.pa - self.pe
        vb = self.pb - self.pe
        vc = self.pc - self.pe

        # Determine distance to screen
        d = -np.dot(self.vn, va)

        # Compute screen coordinates
        l = np.dot(self.vr, va) * n/d
        r = np.dot(self.vr, vb) * n/d
        b = np.dot(self.vu, va) * n/d
        t = np.dot(self.vu, vc) * n/d

        # Projection matrix
        P = np.array([
            [(2.0*n) / (r - l), 0, (r + l) / (r - l), 0],
            [0, (2.0*n) / (t - b), (t + b) / (t - b), 0],
            [0, 0, -(f + n) / (f - n), -(2.0*f*n) / (f - n)],
            [0, 0, -1, 0]], dtype=float)

        # Translation matrix
        T = np.array([
            [1, 0, 0, -self.pe[0]],
            [0, 1, 0, -self.pe[1]],
            [0, 0, 1, -self.pe[2]],
            [0, 0, 0, 1]], dtype=float)

        # Compute overall projection matrix
        offAxis = np.dot(np.dot(P, self.M.T), T)

        # Format matrix for OpenGL
        self.gl_proj_mat = (gl.GLfloat * 16)(*offAxis.flatten('F'))

    ###########################################
    # static methods
    ###########################################

    @staticmethod
    def vec(lis):
        return np.array(lis, dtype=float)

# function to feed lines from a stream to a queue
def stream_to_queue(s, q):
    for line in s:
        q.put(line)

class StimControl:
    def __init__(self, stim_display):
        # save pointer to stim_display
        self.stim_display = stim_display

        # create thread to handle I/O
        self.s = sys.stdin
        self.q = Queue()
        self.t = Thread(target=stream_to_queue, args=(self.s, self.q))
        self.t.daemon = True
        self.t.start()

    def update(self, dt):
        while True:
            try:
                line = self.q.get_nowait()
            except Empty:
                break

            self.handle(line)

    def handle(self, line):
        request = json.loads(line)

        cmd_name = request[0]
        kwargs = request[1]

        if cmd_name == 'load_stim':
            self.stim_display.load_stim(**kwargs)
        elif cmd_name == 'start_stim':
            self.stim_display.start_stim(**kwargs)
        elif cmd_name == 'stop_stim':
            self.stim_display.stop_stim()
        else:
            raise ValueError('Invalid command.')

class ServerArgParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # monitor physical definition
        self.add_argument('--id', type=int, default=0)
        self.add_argument('--pa', type=float, nargs=3, default=[-0.166, -0.1035, -0.3])
        self.add_argument('--pb', type=float, nargs=3, default=[+0.166, -0.1035, -0.3])
        self.add_argument('--pc', type=float, nargs=3, default=[-0.166, +0.1035, -0.3])

def main():
    parser = ServerArgParser()
    args = parser.parse_args()

    # initialize the display
    stim_display = StimDisplay(id=args.id, pa=args.pa, pb=args.pb, pc=args.pc)

    # initialize the control handler
    stim_control = StimControl(stim_display)

    # schedule regular tasks
    pyglet.clock.schedule(stim_display.update)
    pyglet.clock.schedule(stim_control.update)

    # run the application
    pyglet.app.run()

if __name__ == '__main__':
    main()