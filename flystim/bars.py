# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import moderngl
import numpy as np
import os.path

from math import pi

class Bar:
    def __init__(self, min_theta=0, max_theta=0, min_phi=0, max_phi=pi, color=1.0):
        # save settings
        self.color = color
        self.min_phi = min_phi
        self.max_phi = max_phi
        self.min_theta = min_theta
        self.max_theta = max_theta


class BarProgram:
    def __init__(self, screen, max_bars=128):
        # save settings
        self.screen = screen
        self.max_bars = max_bars

    def initialize(self, ctx):
        # save ctx handle
        self.ctx = ctx

        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # equirectangular map generator
        self.equi_prog = self.ctx.program(
            vertex_shader=open(os.path.join(shader_dir, 'bars.vert'), 'r').read(),
            fragment_shader=open(os.path.join(shader_dir, 'generic.frag'), 'r').read()
        )

        # texture display program
        self.text_prog = self.ctx.program(
            vertex_shader=open(os.path.join(shader_dir, 'texture.vert'), 'r').read(),
            fragment_shader=open(os.path.join(shader_dir, 'texture.frag'), 'r').read()
        )

        # create position buffer to represent a single bar
        equi_vert_data = np.array([0.0, 0.0, -2*pi,
                                   1.0, 0.0, -2*pi,
                                   0.0, 1.0, -2*pi,
                                   1.0, 0.0, -2*pi,
                                   0.0, 1.0, -2*pi,
                                   1.0, 1.0, -2*pi,

                                   0.0, 0.0,  0*pi,
                                   1.0, 0.0,  0*pi,
                                   0.0, 1.0,  0*pi,
                                   1.0, 0.0,  0*pi,
                                   0.0, 1.0,  0*pi,
                                   1.0, 1.0,  0*pi,

                                   0.0, 0.0, +2*pi,
                                   1.0, 0.0, +2*pi,
                                   0.0, 1.0, +2*pi,
                                   1.0, 0.0, +2*pi,
                                   0.0, 1.0, +2*pi,
                                   1.0, 1.0, +2*pi])


        self.vbo_equi_vert = self.ctx.buffer(equi_vert_data.astype('f4').tobytes())

        # create instance buffer to represent the configuration of each bar
        equi_inst_data = np.zeros(5*self.max_bars)
        self.vbo_equi_inst = self.ctx.buffer(equi_inst_data.astype('f4').tobytes())

        # create the layout of input data
        vao_equi_content = [
            (self.vbo_equi_vert, '3f', 'pos'),
            (self.vbo_equi_inst, '1f 1f 1f 1f 1f/i',
             'bar_color', 'bar_phi_min', 'bar_phi_max', 'bar_theta_min', 'bar_theta_max')
        ]

        # create vertex array object
        self.vao_equi = self.ctx.vertex_array(self.equi_prog, vao_equi_content)

        # create position buffer to represent a single bar
        text_vert_data = np.array([-1.0, -1.0,
                                   +1.0, -1.0,
                                   -1.0, +1.0,
                                   +1.0, -1.0,
                                   -1.0, +1.0,
                                   +1.0, +1.0])

        self.vbo_text_vert = self.ctx.buffer(text_vert_data.astype('f4').tobytes())

        # create the layout of input data
        vao_text_content = [
            (self.vbo_text_vert, '2f', 'pos')
        ]

        # create vertex array object
        self.vao_text = self.ctx.vertex_array(self.text_prog, vao_text_content)

        # create the texture and framebuffer
        self.texture = self.ctx.texture(self.ctx.viewport[2:4], 1)
        self.fbo = self.ctx.framebuffer(self.texture)

        # write screen parameters
        self.equi_prog['screen_phi_min'].value = self.screen.phi_interval.start
        self.equi_prog['screen_phi_width'].value = self.screen.phi_interval.size()
        self.equi_prog['screen_theta_min'].value = self.screen.theta_interval.start
        self.equi_prog['screen_theta_width'].value = self.screen.theta_interval.size()

        self.text_prog['screen_offset'].value = tuple(self.screen.offset)
        self.text_prog['screen_vector'].value = tuple(self.screen.vector)
        self.text_prog['screen_height'].value = self.screen.height
        self.text_prog['screen_phi_min'].value = self.screen.phi_interval.start
        self.text_prog['screen_phi_width'].value = self.screen.phi_interval.size()
        self.text_prog['screen_theta_min'].value = self.screen.theta_interval.start
        self.text_prog['screen_theta_width'].value = self.screen.theta_interval.size()

    def paint(self, bars, background_color):
        # generate one instance for each bar that is at least partially visible on the screen
        inst_data = []
        inst_count = 0

        for bar in bars:
            min_theta = bar.min_theta % (2*pi)
            max_theta = min_theta + (bar.max_theta - bar.min_theta)

            # update instance data
            inst_data += [bar.color, bar.min_phi, bar.max_phi, min_theta, max_theta]
            inst_count += 1

        if inst_count > 0:
            # write equirectangular data to texture
            self.fbo.use()
            self.fbo.clear(*background_color)
            self.vbo_equi_inst.write(np.array(inst_data).astype('f4').tobytes())
            self.vao_equi.render(instances=inst_count)

            # display texture
            self.ctx.screen.use()
            self.ctx.clear(*background_color)
            self.texture.use()
            self.vao_text.render()
