# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import moderngl
import numpy as np
import os.path

class Sine:
    def __init__(self, a_coeff, b_coeff, c_coeff, d_coeff):
        # save settings
        self.a_coeff = a_coeff
        self.b_coeff = b_coeff
        self.c_coeff = c_coeff
        self.d_coeff = d_coeff

class SineProgram:
    def __init__(self, screen):
        # save settings
        self.screen = screen

        # initialize ModernGL variables
        self.prog = None
        self.vbo = None
        self.vao = None

    def initialize(self, ctx):
        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # load vertex shader
        vertex_shader = open(os.path.join(shader_dir, 'sine.vert'), 'r').read()

        # load fragment shader
        fragment_shader = open(os.path.join(shader_dir, 'sine.frag'), 'r').read()

        # create OpenGL program
        self.prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # create position data to cover entire screen
        vbo_data = np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0])
        self.vbo = ctx.buffer(vbo_data.astype('f4').tobytes())

        # create the layout of input data
        vao_content = [
            (self.vbo, '2f', 'pos')
        ]

        # create vertex array object
        self.vao = ctx.vertex_array(self.prog, vao_content)

        # write screen parameters
        self.prog['screen_offset'].value = tuple(self.screen.offset)
        self.prog['screen_vector'].value = tuple(self.screen.vector)
        self.prog['screen_height'].value = self.screen.height

    def paint(self, content):
        self.prog['a_coeff'].value = content.a_coeff
        self.prog['b_coeff'].value = content.b_coeff
        self.prog['c_coeff'].value = content.c_coeff
        self.prog['d_coeff'].value = content.d_coeff

        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
