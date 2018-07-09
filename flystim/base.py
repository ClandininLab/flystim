# note: the starting point for this code was the examples directory of the ModernGL project

import moderngl
import numpy as np
import os.path
from string import Template

class BaseProgram:
    def __init__(self, screen, uniforms=None, calc_color=None):
        """
        :param screen: Object containing screen size information
        :param uniforms: List of glsl.Uniform objects representing the uniform variables used in the shader
        :param calc_color: GLSL shader code used to compute the monochromatic color of each pixel as a function
        of spherical coordinates (r, theta, phi), which should be assumed to have been calculated before the calc_color
        code has run (see base.template)
        """
        # set screen
        self.screen = screen

        # set uniform declarations
        if uniforms is None:
            uniforms = []
        self.uniforms = uniforms

        # set color program
        if calc_color is None:
            calc_color = 'color = 0.0;'
        self.calc_color = calc_color

    def initialize(self, ctx):
        """
        :param ctx: ModernGL context
        """

        # save context
        self.ctx = ctx

        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # load the vertex shader
        vertex_shader = open(os.path.join(shader_dir, 'base.vert'), 'r').read()

        # convert list of uniforms to GLSL code
        decl_uniforms = ''.join(str(uniform)+';\n' for uniform in self.uniforms)

        # load the fragment shader
        fragment_shader_template = Template(open(os.path.join(shader_dir, 'base.template'), 'r').read())
        fragment_shader = fragment_shader_template.substitute(
            decl_uniforms=decl_uniforms,
            calc_color=self.calc_color
        )

        self.prog = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # create VBO to represent vertex positions
        pts = np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0])
        vbo = self.ctx.buffer(pts.astype('f4').tobytes())

        # create vertex array object
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'vert_pos')

        # write screen parameters
        if self.prog.get('screen_offset', None) is not None:
            self.prog['screen_offset'].value = tuple(self.screen.offset)
        if self.prog.get('screen_vector', None) is not None:
            self.prog['screen_vector'].value = tuple(self.screen.vector)
        if self.prog.get('screen_height', None) is not None:
            self.prog['screen_height'].value = self.screen.height

    def paint_at(self, t):
        """
        :param t: current time in seconds
        """

        self.ctx.clear()
        self.eval_at(t)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)

    def eval_at(self, t):
        """
        :param t: current time in seconds
        """

        pass
