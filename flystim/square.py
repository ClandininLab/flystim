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
        self.draw = True

    def initialize(self, ctx):
        # save context
        self.ctx = ctx

        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # create OpenGL program
        prog = self.ctx.program(vertex_shader=open(os.path.join(shader_dir, 'rect.vert'), 'r').read(),
                                     fragment_shader=open(os.path.join(shader_dir, 'mono.frag'), 'r').read())

        # create VBO to represent vertex positions
        vert_data = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0])
        vbo_vert = self.ctx.buffer(vert_data.astype('f4').tobytes())

        # create VBO to represent spatial extent of square
        xy_data = self.make_xy_data()
        vbo_xy = self.ctx.buffer(xy_data.astype('f4').tobytes())

        # create VBO to represent vertex square color
        color_data = np.zeros(1)
        self.vbo_color = self.ctx.buffer(color_data.astype('f4').tobytes())

        # create the layout of input data
        vao_content = [
            (vbo_vert, '2f', 'pos'),
            (vbo_xy, '1f 1f 1f 1f/i', 'x_min', 'x_max', 'y_min', 'y_max'),
            (self.vbo_color, '1f/i', 'color')
        ]

        # create vertex array object
        self.vao = self.ctx.vertex_array(prog, vao_content)

    def make_xy_data(self):
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

        # create rectangle with appropriate width and height
        xy_data = np.array([offset_x - w/2, offset_x + w/2, offset_y - h/2, offset_y + h/2])

        return xy_data

    def paint(self):
        if self.draw:
            # write color data
            color_data = np.array([self.color])
            self.vbo_color.write(color_data.astype('f4').tobytes())

            # render to screen
            self.vao.render(mode=moderngl.TRIANGLE_STRIP, instances=1)

        if self.toggle:
            self.color = 1.0 - self.color
