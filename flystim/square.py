# ref: https://github.com/cprogrammer1994/ModernGL/blob/master/examples/julia_fractal.py

import os.path
import random
from time import time


import moderngl
import numpy as np

class SquareProgram:
    def __init__(self, screen):
        # save settings
        self.screen = screen

        # initialize settings
        self.color = 1.0
        self.square_history = []
        self.save_square_history = screen.save_square_history
        self.toggle = True
        self.toggle_prob = screen.square_toggle_prob
        self.last_toggle = time()
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

    def toggle_square(self):
        # probablistic toggling
        if random.random() < self.toggle_prob:
            elapsed = time() - self.last_toggle
            # NOTE: limit toggle rate to 120hz to stay well within nyquist limit
            #  (camera capture rate is 240hz)
            max_toggle_freq = 100
            if elapsed > (1 / (max_toggle_freq / 2)):
                self.color = 1.0 - self.color
                self.last_toggle = time()

    def paint(self):
        if self.draw:
            # write color
            self.prog['color'].value = self.color

            # render to screen
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

        # Save the square color at each call of paint
        if self.save_square_history:
            self.square_history.append(int(self.color))

        if self.toggle:
            self.toggle_square()
