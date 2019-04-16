# note: the starting point for this code was the examples directory of the ModernGL project

import moderngl
import numpy as np
import os.path
from string import Template
from math import pi, radians

class BaseConfigOptions:
    def __init__(self, *args, box_min_x=-180, box_max_x=180, box_min_y=0, box_max_y=180, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.box_min_x = radians(box_min_x)
        self.box_max_x = radians(box_max_x)
        self.box_min_y = radians(box_min_y)
        self.box_max_y = radians(box_max_y)

class BaseProgram:
    def __init__(self, screen, uniforms=None, functions=None, calc_color=None):
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

        # set function declarations
        if functions is None:
            functions = []
        self.functions = functions

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

        # convert list of functions to GLSL code
        decl_functions = ''.join(str(function)+'\n' for function in self.functions)

        # load the fragment shader
        fragment_shader_template = Template(open(os.path.join(shader_dir, 'base.template'), 'r').read())
        fragment_shader = fragment_shader_template.substitute(
            decl_uniforms=decl_uniforms,
            decl_functions=decl_functions,
            calc_color=self.calc_color
        )

        self.prog = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # create a flat list of all of the 5-tuples that describe the screen coordinates
        data = []

        for tri in self.screen.tri_list:
            for pt in [tri.pa, tri.pb, tri.pc]:
                data.extend(pt.ndc)
                data.extend(pt.cart)

        data = np.array(data, dtype=float)

        # create a VBO for the vertex data
        vbo = self.ctx.buffer(data.astype('f4').tobytes())

        # create vertex array object
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'vert_pos', 'vert_col')

    def configure(self, *args, **kwargs):
        pass

    def paint_at(self, t, global_fly_pos, global_theta_offset):
        """
        :param t: current time in seconds
        """

        self.prog['box_min_x'].value = self.box_min_x
        self.prog['box_max_x'].value = self.box_max_x
        self.prog['box_min_y'].value = self.box_min_y
        self.prog['box_max_y'].value = self.box_max_y

        self.prog['global_fly_pos'].value = tuple(global_fly_pos)
        self.prog['global_theta_offset'].value = global_theta_offset

        self.eval_at(t)
        self.vao.render(mode=moderngl.TRIANGLES)

    def eval_at(self, t):
        """
        :param t: current time in seconds
        """

        pass

    def make_config_options(self, *args, **kwargs):
        return BaseConfigOptions(*args, **kwargs)

    def apply_config_options(self, config_options):
        self.box_min_x = config_options.box_min_x
        self.box_max_x = config_options.box_max_x
        self.box_min_y = config_options.box_min_y
        self.box_max_y = config_options.box_max_y

        self.configure(*config_options.args, **config_options.kwargs)