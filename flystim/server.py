import pyglet
import pyglet.gl as gl
import numpy as np

from argparse import ArgumentParser
from xmlrpc.server import SimpleXMLRPCServer

def vec(lis):
    return np.array(lis, dtype='float')

class ServerArgParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # argument tag used to identify the process
        self.add_argument('--tag', type=str, default=None)

        # monitor physical definition
        self.add_argument('--id', type=int, default=0)
        self.add_argument('--pa', type=float, nargs=3, default=[-1, -1, -1])
        self.add_argument('--pb', type=float, nargs=3, default=[+1, -1, -1])
        self.add_argument('--pc', type=float, nargs=3, default=[-1, +1, -1])

class DisplayServer:
    def __init__(self, id, pa, pb, pc, near_clip=1e-2, far_clip=100, side=2.5e-2):
        # save settings
        self.pa = pa
        self.pb = pb
        self.pc = pc
        self.n = near_clip
        self.f = far_clip

        # compute normal vectors
        self.set_norm_vecs()

        # initialize variables
        self.set_pe(0, 0, 0)

        # initialize graphics
        self.gl_vertices = []
        self.gl_colors = []

        # initialize corner square
        w = np.linalg.norm(self.pb-self.pa)
        h = np.linalg.norm(self.pc-self.pa)
        urx = 1
        ury = 1
        llx = urx - 2/w * side
        lly = ury - 2/h * side
        self.hud_vertices = [llx, lly, urx, lly, urx, ury, llx, ury]
        self.hud_colors = [255]*12

        # create server
        # self.server = SimpleXMLRPCServer(addr=('127.0.0.1', 0), logRequests=False)
        # self.server.register_function(self.set_pe)
        # self.server.register_function(self.set_background_color)

        # get the appropriate screen
        display = pyglet.window.get_platform().get_default_display()
        screen = display.get_screens()[id]

        # get the appropriate window
        self.window = pyglet.window.Window(screen=screen, fullscreen=False, resizable=True, visible=False)

        # initialize the background color
        self.set_background_color(0, 0, 0)

        # draw objects
        @self.window.event
        def on_draw():
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            # load the perspective-corrected projection matrix
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadMatrixf(self.gl_proj_mat)

            # load the model view matrix
            # (is this necessary?)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            n_vert = len(self.gl_vertices) // 3
            if n_vert > 0:
                pyglet.graphics.draw(n_vert, gl.GL_TRIANGLES, ('v3f', self.gl_vertices), ('c3B', self.gl_colors))

            # load the orthographic projection matrix
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()

            # load the model view matrix
            # (is this necessary?)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', self.hud_vertices), ('c3B', self.hud_colors))

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
        #self.server.handle_request()

    ###########################################
    # functions accessible through the server
    ###########################################

    def set_background_color(self, r, g, b):
        gl.glClearColor(r, g, b, 0)

    def set_pe(self, x, y, z):
        self.pe = vec([x, y, z])
        self.update_proj_mat()

    ###########################################
    # project matrix calculation
    ###########################################

    def set_norm_vecs(self):
        # function need only be called once, after pa/pb/pc are defined
        # ref: http://csc.lsu.edu/~kooima/articles/genperspective/

        self.vr = self.pb - self.pa
        self.vr /= np.linalg.norm(self.vr)

        self.vu = self.pc - self.pa
        self.vu /= np.linalg.norm(self.vu)

        self.vn = np.cross(self.vr, self.vu)
        self.vn /= np.linalg.norm(self.vn)

        # Rotation matrix
        self.M = np.array([
            [self.vr[0], self.vu[0], self.vn[0], 0],
            [self.vr[1], self.vu[1], self.vn[1], 0],
            [self.vr[2], self.vu[2], self.vn[2], 0],
            [0, 0, 0, 1]], dtype='float')

    def update_proj_mat(self):
        # function should be called whenever pe is updated
        # ref: http://csc.lsu.edu/~kooima/articles/genperspective/

        # Determine frustum extents
        va = self.pa - self.pe
        vb = self.pb - self.pe
        vc = self.pc - self.pe

        # Determine distance to screen
        d = -np.dot(self.vn, va)

        # Compute screen coordinates
        l = np.dot(self.vr, va) * self.n/d
        r = np.dot(self.vr, vb) * self.n/d
        b = np.dot(self.vu, va) * self.n/d
        t = np.dot(self.vu, vc) * self.n/d

        # Projection matrix
        P = np.array([
            [(2.0*self.n) / (r - l), 0, (r + l) / (r - l), 0],
            [0, (2.0*self.n) / (t - b), (t + b) / (t - b), 0],
            [0, 0, -(self.f + self.n) / (self.f - self.n), -(2.0*self.f*self.n) / (self.f - self.n)],
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
    parser = ServerArgParser()
    args = parser.parse_args()

    display_server = DisplayServer(id=args.id, pa=vec(args.pa), pb=vec(args.pb), pc=vec(args.pc))

    pyglet.clock.schedule(display_server.update)

    display_server.window.set_visible()
    pyglet.app.run()

if __name__ == '__main__':
    main()