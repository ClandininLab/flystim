# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import moderngl
import numpy as np
import os.path

from math import pi

from flystim.stim_window import run_stim
from flystim.screen import Screen


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

        # initialize ModernGL variables
        self.prog = None
        self.vbo_vert = None
        self.vbo_inst = None
        self.vao = None

    def initialize(self, ctx):
        # find path to shader directory
        this_file_path = os.path.realpath(os.path.expanduser(__file__))
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(this_file_path)), 'shaders')

        # load vertex shader
        vertex_shader = open(os.path.join(shader_dir, 'bars.vert'), 'r').read()

        # load fragment shader
        fragment_shader = open(os.path.join(shader_dir, 'bars.frag'), 'r').read()

        # create OpenGL program
        self.prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # create position buffer to represent a single bar
        vert_data = np.array([0.0, -1.0, 1.0, -1.0, 0.0, +1.0, 1.0, +1.0])
        self.vbo_vert = ctx.buffer(vert_data.astype('f4').tobytes())

        # create instance buffer to represent the configuration of each bar
        inst_data = np.zeros(5*self.max_bars)
        self.vbo_inst = ctx.buffer(inst_data.astype('f4').tobytes())

        # create the layout of input data
        vao_content = [
            (self.vbo_vert, '2f', 'pos'),
            (self.vbo_inst, '1f 1f 1f 1f 1f/i', 'min_theta', 'max_theta', 'min_phi', 'max_phi', 'color')
        ]

        # create vertex array object
        self.vao = ctx.vertex_array(self.prog, vao_content)

        # write screen parameters
        self.prog['screen_offset'].value = tuple(self.screen.offset)
        self.prog['screen_vector'].value = tuple(self.screen.vector)
        self.prog['screen_height'].value = self.screen.height

    def paint(self, bars):
        # generate one instance for each bar that is at least partially visible on the screen
        inst_data = []
        inst_count = 0

        for bar in bars:
            overlap = self.screen.interval.intersect(bar.min_theta, bar.max_theta)

            if overlap is None:
                continue

            # update instance data
            inst_data += [overlap.start, overlap.end, bar.min_phi, bar.max_phi, bar.color]
            inst_count += 1

        if inst_count > 0:
            self.vbo_inst.write(np.array(inst_data).astype('f4').tobytes())
            self.vao.render(mode=moderngl.TRIANGLE_STRIP, instances=inst_count)


def main():
    screen = Screen()
    stim_gl = BarProgram(screen=screen)

    n = 20
    delta = 2 * pi / n
    stim_gl.bars = [Bar((k-0.25) * delta, (k + 0.25) * delta) for k in range(n)]

    run_stim(stim_gl, width=1280, height=720, title='Bar Stimulus')


if __name__ == "__main__":
    main()
