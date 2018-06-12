# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import moderngl
import numpy as np
import os.path

from flystim.screen import Screen

class SquareProgram:
    def __init__(self, screen):
        # save settings
        self.screen = screen

        # initialize settings
        self.color = 1.0
        self.toggle = True
        self.draw = True

        # make the vertex data
        self.vert_data = self.make_vert_data()

        # initialize ModernGL variables
        self.prog = None
        self.vbo_vert = None
        self.vbo_color = None
        self.vao = None

    def initialize(self, ctx):
        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # load vertex shader
        vertex_shader = open(os.path.join(shader_dir, 'generic.vert'), 'r').read()

        # load fragment shader
        fragment_shader = open(os.path.join(shader_dir, 'generic.frag'), 'r').read()

        # create OpenGL program
        self.prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # create VBO to represent vertex positions (four vertices, two floats each)
        self.vbo_vert = ctx.buffer(self.vert_data.astype('f4').tobytes())

        # create VBO to represent vertex colors (four vertices, one color each)
        color_data = np.zeros(4*1)
        self.vbo_color = ctx.buffer(color_data.astype('f4').tobytes())

        # create the layout of input data
        vao_content = [
            (self.vbo_vert, '2f', 'pos'),
            (self.vbo_color, '1f', 'color')
        ]

        # create vertex array object
        self.vao = ctx.vertex_array(self.prog, vao_content)

    def paint(self):
        if self.draw:
            color_data = self.color*np.ones(4)
            self.vbo_color.write(color_data.astype('f4').tobytes())
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

        if self.toggle:
            self.color = 1.0 - self.color

    def make_vert_data(self):
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

        # set 2D offset
        offset = np.array([offset_x, offset_y])

        # create rectangle with appropriate width and height
        vert_data = np.column_stack(([-w/2, -h/2], [+w/2, -h/2], [-w/2, +h/2], [+w/2, +h/2]))

        # add offset
        vert_data += offset[:, None]

        # flatten using column-major order
        vert_data = vert_data.flatten('F')

        return vert_data


def main():

    screen = Screen()
    stim_gl = SquareProgram(screen=screen)

    from flystim.stim_window import run_stim
    run_stim(stim_gl, width=1280, height=720, title='Square Stimulus')


if __name__ == "__main__":
    main()
