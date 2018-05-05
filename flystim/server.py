import pyglet
import pyglet.gl as gl
import numpy as np

from argparse import ArgumentParser

def vec(lis):
    return np.array(lis, dtype='float')

class StimArgParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # argument tag used to identify the process
        self.add_argument('--tag', type=str, default=None)

        # monitor physical definition
        # defaults are for MacBook Pro (Retina, 15-inch, Mid 2015)
        self.add_argument('--id', type=int, default=0)
        self.add_argument('--pa', type=float, nargs=3, default=[-0.166, -0.1035, -1])
        self.add_argument('--pb', type=float, nargs=3, default=[+0.166, -0.1035, -1])
        self.add_argument('--pc', type=float, nargs=3, default=[-0.166, +0.1035, -1])

class GlItem:
    def __init__(self, gl_type, dims):
        # save settings
        self.gl_type = gl_type
        self.dims = dims

        # set up vertex data
        self.vertex_data = []
        self.vertex_format = 'v{:d}f'.format(self.dims)

        # set up color data
        self.color_data = []
        self.color_format = 'c3B'

    def draw(self):
        if self.num_vertices > 0:
            pyglet.graphics.draw(self.num_vertices,
                                 self.gl_type,
                                 (self.vertex_format, self.vertex_data),
                                 (self.color_format, self.color_data))

    @property
    def num_vertices(self):
        return len(self.vertex_data) // self.dims

class GlItem2D(GlItem):
    def __init__(self, gl_type):
        super().__init__(gl_type=gl_type, dims=2)

class GlItem3D(GlItem):
    def __init__(self, gl_type):
        super().__init__(gl_type=gl_type, dims=3)

class StimDisplay:
    def __init__(self, id, pa, pb, pc, draw_pd_square=True, draw_debug_info=True):
        # save settings
        self.id = id
        self.pa = pa
        self.pb = pb
        self.pc = pc
        self.draw_pd_square = draw_pd_square
        self.draw_debug_info = draw_debug_info

        # list initialization
        self.stim = None

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
        self.set_background_color(0, 0, 0)
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

            # draw 3D items
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
            if self.draw_pd_square:
                self.pd_square.draw()

            if self.draw_debug_info:
                self.id_label.draw()
                self.clock_display.draw()

        # handle escape key
        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.ESCAPE:
                self.window.close()

    ###########################################
    # frame update function
    ###########################################

    def update(self, dt):
        pass

    ###########################################
    # control functions
    ###########################################

    # debug options

    def show_debug_info(self):
        self.draw_debug_info = True

    def hide_debug_info(self):
        self.draw_debug_info = False

    # photodiode square options

    def show_pd_square(self):
        self.draw_pd_square = True

    def hide_pd_square(self):
        self.hide_pd_square = False

    def set_pd_square(self):
        self.pd_square.color_data = [255] * 12

    def clear_pd_square(self):
        self.pd_square.color_data = [0] * 12

    def toggle_pd_square(self):
        self.pd_square.color_data = [255 - elem for elem in self.pd_square.color_data]

    # background color

    def set_background_color(self, r, g, b):
        gl.glClearColor(r, g, b, 0)

    # eye position

    def set_pe(self, x, y, z):
        self.pe = vec([x, y, z])
        self.update_proj_mat()

    ###########################################
    # initialization functions
    ###########################################

    def init_window(self):
        display = pyglet.window.get_platform().get_default_display()
        screen = display.get_screens()[self.id]
        self.window = pyglet.window.Window(screen=screen, fullscreen=True, visible=False)

    def init_pd_square(self, square_side=0.5e-2):
        self.pd_square = GlItem2D(gl.GL_QUADS)

        # compute upper right corner coordinates
        urx = self.window.width
        ury = self.window.height

        # compute lower left corner coordinates
        llx = urx - self.window.width/self.screen_width * square_side
        lly = ury - self.window.height/self.screen_height * square_side

        # compute vertices of the square
        self.pd_square.vertex_data = [llx, lly, urx, lly, urx, ury, llx, ury]

        # compute colors of the vertices
        self.pd_square.color_data = [255]*12

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
            [0, 0, 0, 1]], dtype='float')

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
            [0, 0, -1, 0]], dtype='float')

        # Translation matrix
        T = np.array([
            [1, 0, 0, -self.pe[0]],
            [0, 1, 0, -self.pe[1]],
            [0, 0, 1, -self.pe[2]],
            [0, 0, 0, 1]], dtype='float')

        # Compute overall projection matrix
        offAxis = np.dot(np.dot(P, self.M.T), T)

        # Format matrix for OpenGL
        self.gl_proj_mat = (gl.GLfloat * 16)(*offAxis.flatten('F'))

def main():
    parser = StimArgParser()
    args = parser.parse_args()

    stim = StimDisplay(id=args.id, pa=vec(args.pa), pb=vec(args.pb), pc=vec(args.pc))

    pyglet.clock.schedule(stim.update)

    stim.window.set_visible()
    pyglet.app.run()

if __name__ == '__main__':
    main()