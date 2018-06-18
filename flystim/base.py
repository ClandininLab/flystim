# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import moderngl
import numpy as np
import os.path
from string import Template

class BaseProgram:
    def __init__(self, screen, uniform_declarations=None, color_program=None):
        # set screen
        self.screen = screen

        # set uniform declarations
        if uniform_declarations is None:
            uniform_declarations = ''
        self.uniform_declarations = uniform_declarations

        # set color program
        if color_program is None:
            color_program = 'out_color = vec4(0.0, 0.0, 0.0, 1.0);'
        self.color_program = color_program

    def initialize(self, ctx):
        # save context
        self.ctx = ctx

        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # load the vertex shader
        vertex_shader = open(os.path.join(shader_dir, 'base.vert'), 'r').read()

        # load the fragment shader
        fragment_shader_template = Template(open(os.path.join(shader_dir, 'base.template'), 'r').read())
        fragment_shader = fragment_shader_template.substitute(
            uniform_declarations=self.uniform_declarations,
            color_program=self.color_program
        )

        self.prog = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # create VBO to represent vertex positions
        pts = np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0])
        vbo = self.ctx.buffer(pts.astype('f4').tobytes())

        # create vertex array object
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'vert_pos')

        # write screen parameters
        self.prog['screen_offset'].value = tuple(self.screen.offset)
        self.prog['screen_vector'].value = tuple(self.screen.vector)
        self.prog['screen_height'].value = self.screen.height

    def configure(self, background_color=None):
        # set background color
        if background_color is None:
            background_color = (0.0, 0.0, 0.0)
        self.background_color = background_color

    def eval_at(self, t):
        pass

    def paint_at(self, t):
        self.ctx.clear(*self.background_color)

        self.eval_at(t)

        self.vao.render(mode=moderngl.TRIANGLE_STRIP)