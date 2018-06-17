# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import moderngl

import numpy as np
import os.path

from math import pi

class Bar:
    def __init__(self, theta_min, theta_max, phi_min=0, phi_max=pi, color=1.0):
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.phi_min = phi_min
        self.phi_max = phi_max
        self.color = color

    def normalized(self):
        # calculate new theta range
        new_theta_min = self.theta_min % (2*pi)
        new_theta_max = new_theta_min + (self.theta_max - self.theta_min)

        # return new bar
        return Bar(theta_min=new_theta_min, theta_max=new_theta_max, phi_min=self.phi_min, phi_max=self.phi_max,
                   color=self.color)

    def shift_theta(self, amount):
        # calculate new theta range
        new_theta_min = self.theta_min + amount
        new_theta_max = self.theta_max + amount

        # return new bar
        return Bar(theta_min=new_theta_min, theta_max=new_theta_max, phi_min=self.phi_min, phi_max=self.phi_max,
                   color=self.color)

class BarProgram:
    def __init__(self, screen, max_bars=128, text_width=8000, text_height=4000):
        # save settings
        self.screen = screen
        self.max_bars = max_bars
        self.text_width = text_width
        self.text_height = text_height

    def initialize(self, ctx):
        # save context
        self.ctx = ctx

        # set up equirectangular map generator
        self.setup_equi_prog()

        # set up texture rendering program
        self.setup_text_prog()

        # set up texture and framebuffer
        self.setup_texture()

    def setup_equi_prog(self):
        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # equirectangular map generator
        equi_prog = self.ctx.program(
            vertex_shader=open(os.path.join(shader_dir, 'rect.vert'), 'r').read(),
            fragment_shader=open(os.path.join(shader_dir, 'mono.frag'), 'r').read()
        )

        # create VBO to represent vertex positions
        vert_equi_data = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0])
        vert_equi_vbo  = self.ctx.buffer(vert_equi_data.astype('f4').tobytes())

        # create VBO to represent instance data
        inst_equi_data = np.zeros(5*self.max_bars)
        self.inst_equi_vbo = self.ctx.buffer(inst_equi_data.astype('f4').tobytes())

        # create the layout of input data
        vao_equi_content = [
            (vert_equi_vbo, '2f', 'pos'),
            (self.inst_equi_vbo, '1f 1f 1f 1f 1f/i', 'x_min', 'x_max', 'y_min', 'y_max', 'color')
        ]

        # create vertex array object
        self.vao_equi = self.ctx.vertex_array(equi_prog, vao_equi_content)

    def setup_text_prog(self):
        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # texture display program
        text_prog = self.ctx.program(
            vertex_shader=open(os.path.join(shader_dir, 'rect.vert'), 'r').read(),
            fragment_shader=open(os.path.join(shader_dir, 'sphere.frag'), 'r').read()
        )

        # create VBO to represent vertex positions
        vert_text_data = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0])
        vert_text_vbo = self.ctx.buffer(vert_text_data.astype('f4').tobytes())

        # create VBO to represent instance data
        inst_text_data = np.array([-1.0, +1.0, -1.0, +1.0, 0.0])
        inst_text_vbo = self.ctx.buffer(inst_text_data.astype('f4').tobytes())

        # create the layout of input data
        vao_text_content = [
            (vert_text_vbo, '2f', 'pos'),
            (inst_text_vbo, '1f 1f 1f 1f 1f/i', 'x_min', 'x_max', 'y_min', 'y_max', 'color')
        ]

        # create vertex array object
        self.vao_text = self.ctx.vertex_array(text_prog, vao_text_content)

        # set the screen uniforms
        text_prog['screen_offset'].value = tuple(self.screen.offset)
        text_prog['screen_vector'].value = tuple(self.screen.vector)
        text_prog['screen_height'].value = self.screen.height

    def setup_texture(self):
        # create the texture
        texture = self.ctx.texture((self.text_width, self.text_height), 1)

        # create the framebuffer to render into this texture
        self.fbo = self.ctx.framebuffer(texture)

        # use the texture
        texture.use()

    def paint(self, bars, background_color):
        # create list of bars to render, which involves normalizing their angles and splitting
        # bars that cross the 2*pi boundary

        render_bars = []

        for bar in bars:
            render_bars.append(bar.normalized())
            if render_bars[-1].theta_max > (2*pi):
                render_bars.append(render_bars[-1].shift_theta(-2*pi))

        # write instance data (angular range and color of each bar), which entails scaling the theta and phi
        # values to the [-1, +1] NDC range

        inst_equi_data = []

        for bar in render_bars:
            inst_equi_data += [bar.theta_min/pi - 1.0,
                               bar.theta_max/pi - 1.0,
                               2*bar.phi_min/pi - 1.0,
                               2*bar.phi_max/pi - 1.0,
                               bar.color]

        self.inst_equi_vbo.write(np.array(inst_equi_data).astype('f4').tobytes())

        # write equirectangular data to texture
        self.fbo.use()
        self.fbo.clear(*background_color)

        if len(render_bars) > 0:
            self.vao_equi.render(mode=moderngl.TRIANGLE_STRIP, instances=len(render_bars))

        # display texture to screen
        self.ctx.screen.use()
        self.ctx.clear(*background_color)
        self.vao_text.render(mode=moderngl.TRIANGLE_STRIP, instances=1)
