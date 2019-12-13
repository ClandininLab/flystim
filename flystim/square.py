# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import moderngl
import numpy as np
import os.path

class SquareProgram:
    def __init__(self, screen):
        # save settings
        self.screen = screen

        # initialize settings
        self.color = 1.0
        self.toggle = True
        self.toggle_prob = screen.square_toggle_prob
        self.draw = True

    def initialize(self, ctx):
        """
        :param ctx: ModernGL context
        """

        # save context
        self.ctx = ctx

        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # create OpenGL program
        self.prog = self.ctx.program(vertex_shader=open(os.path.join(shader_dir, 'square.vert'), 'r').read(),
                                     fragment_shader=open(os.path.join(shader_dir, 'square.frag'), 'r').read())

        # create VBO to represent vertex positions
        pts = self.make_vert_pts()
        vbo = self.ctx.buffer(pts.astype('f4').tobytes())

        # create vertex array object
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'pos')

    def make_vert_pts(self):
        """
        Returns a numpy array of the vertex coordinates in NDC space of the photodiode square
        """

        # compute width and height in NDC
        w = 2.0*self.screen.square_side/self.screen.width
        h = 2.0*self.screen.square_side/self.screen.height

        # compute vertical offset in NDC
        if self.screen.square_loc[0] == 'l':
            offset_y = -1.0 + h/2
        elif self.screen.square_loc[0] == 'u':
            offset_y = +1.0 - h/2
        else:
            raise ValueError('Invalid square location.')

        # compute horizontal offset in NDC
        if self.screen.square_loc[1] == 'l':
            offset_x = -1.0 + w/2
        elif self.screen.square_loc[1] == 'r':
            offset_x = +1.0 - w/2
        else:
            raise ValueError('Invalid square location.')

        # determine rectangular bounds
        x_min = offset_x - w/2
        x_max = offset_x + w/2
        y_min = offset_y - h/2
        y_max = offset_y + h/2

        # return vertex point data
        return np.array([x_min, y_min, x_max, y_min, x_min, y_max, x_max, y_max])

    def paint(self):
        if self.draw:
            # write color
            self.prog['color'].value = self.color

            # render to screen
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

        if self.toggle:
            if random.random() < self.square_toggle_prob:
                self.color = 1.0 - self.color
