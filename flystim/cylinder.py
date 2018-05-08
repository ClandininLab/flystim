import pyglet.gl as gl
import numpy as np

from flystim import graphics
from flystim.reprandom import colored_noise

class CylinderStim:
    def __init__(self, radius=2.0, height=10.0, background=None):
        # initialize settings
        if background is None:
            background = (0.0, 0.0, 0.0)

        # save settings
        self.radius = radius
        self.height = height
        self.background = background

        # initialize arrays
        self.starts = None
        self.stops = None
        self.colors = None

    @property
    def num_bars(self):
        return len(self.starts)

    def eval_at(self, t):
        pass

    def draw(self):
        # x coordinates
        x_start = -self.radius*np.sin(self.starts)
        x_stop  = -self.radius*np.sin(self.stops)

        # y coordinates
        y_top = +self.height/2
        y_bot = -self.height/2

        # z coordinates
        z_start = -self.radius*np.cos(self.starts)
        z_stop  = -self.radius*np.cos(self.stops)

        # build graphics object
        item = graphics.Item3D(gl.GL_QUADS)

        # fill vertex data
        item.vertex_data = np.zeros(12*self.num_bars, dtype=float)

        # lower left corners
        item.vertex_data[0::12] = x_stop
        item.vertex_data[1::12] = y_bot
        item.vertex_data[2::12] = z_stop

        # lower right corners
        item.vertex_data[3::12] = x_start
        item.vertex_data[4::12] = y_bot
        item.vertex_data[5::12] = z_start

        # upper right corners
        item.vertex_data[6::12] = x_start
        item.vertex_data[7::12] = y_top
        item.vertex_data[8::12] = z_start

        # upper left corners
        item.vertex_data[9::12] = x_stop
        item.vertex_data[10::12] = y_top
        item.vertex_data[11::12] = z_stop

        # fill color data (RGB * 4 vertices = 12 values per quad)
        item.color_data = np.repeat(self.colors, 12)

        # draw graphics
        item.draw()

class RotatingBars(CylinderStim):
    def __init__(self, period=20, duty_cycle=0.5, rate=10, **kwargs):
        # set background to black if not set already
        if 'background' not in kwargs:
            kwargs['background'] = (0.0, 0.0, 0.0)

        # call super constructor
        super().__init__(**kwargs)

        # save settings
        self.period = period
        self.duty_cycle = duty_cycle
        self.rate = rate

        # setup
        self.init_starts = np.radians(np.arange(0, 360, period, dtype='float'))
        self.init_stops = self.init_starts + self.duty_cycle*(self.init_starts[1]-self.init_starts[0])
        self.colors = np.ones(len(self.init_starts), dtype=float)

    def eval_at(self, t):
        change = t*np.radians(self.rate)
        self.starts = change + self.init_starts
        self.stops = change + self.init_stops

class ExpandingEdges(CylinderStim):
    def __init__(self, period=15, width=2, rate=10, **kwargs):
        # set background to black if not set already
        if 'background' not in kwargs:
            kwargs['background'] = (0.0, 0.0, 0.0)

        # super constructor
        super().__init__(**kwargs)

        # save settings
        self.period = period
        self.width = width
        self.rate = rate

        # setup
        self.starts = np.radians(np.arange(0, 360, period, dtype='float'))
        self.init_stops = self.starts + np.radians(self.width)
        self.colors = np.ones(len(self.starts), dtype=float)

    def eval_at(self, t):
        change = t*np.radians(self.rate)
        self.stops = change + self.init_stops

class GaussianNoise(CylinderStim):
    def __init__(self, period=15, vert_extent=30, width=2, gauss_mean=0.5, gauss_std=0.5, time_constant=20e-3,
                 random_seed=0, runtime=3, pts_per_tau=10, **kwargs):
        # set background to gray if not set already
        if 'background' not in kwargs:
            kwargs['background'] = (0.5, 0.5, 0.5)

        # super constructor
        super().__init__(**kwargs)

        # save settings
        self.period = period
        self.vert_extent = vert_extent
        self.width = width
        self.runtime = runtime

        # settings related to noise generator...
        self.gauss_mean = gauss_mean
        self.gauss_std = gauss_std
        self.time_constant = time_constant
        self.random_seed = random_seed
        self.pts_per_tau = pts_per_tau

        # set height based on vert_extent, as long as the user did not explicitly set height as a kwarg
        if 'height' not in kwargs:
            self.height = self.radius * np.sin(np.radians(vert_extent))

        # create starting angles
        self.starts = np.radians(np.arange(0, 360, period, dtype='float'))

        # throw out the first one and rotate all backwards by half a period
        self.starts = self.starts[1:] - self.period/2

        # create the stopping angles
        self.stops = self.starts + np.radians(self.width)

        # make pseudo-random generators
        np.random.seed(self.random_seed)
        self.random_funcs = [colored_noise(loc   = self.gauss_mean,
                                           scale = self.gauss_std,
                                           tau   = self.time_constant,
                                           dt    = self.time_constant / self.pts_per_tau,
                                           tmax  = self.runtime)
                             for _ in range(self.num_bars)]

    def eval_at(self, t):
        unclipped = np.array([random_func(t) for random_func in self.random_funcs])
        self.colors = np.clip(unclipped, 0.0, 1.0)

class SequentialBars(CylinderStim):
    def __init__(self, width=5, period=20, offset=0, first_active_bright=True, second_active_bright=True,
                 first_active_time=1, second_active_time=2, **kwargs):
        # set background if not set already
        if 'background' not in kwargs:
            kwargs['background'] = (0.5, 0.5, 0.5)

        # super constructor
        super().__init__(**kwargs)

        # save settings
        self.width = width
        self.period = period
        self.offset = offset
        self.first_active_bright = first_active_bright
        self.second_active_bright = second_active_bright
        self.first_active_time = first_active_time
        self.second_active_time = second_active_time

        # create starting points (two bars per period, each with given width)
        self.starts = np.radians(np.arange(0, 360, period, dtype='float'))
        self.starts = np.repeat(self.starts, 2)
        self.starts[1::2] += np.radians(width)

        # add offset to starting point
        self.starts += np.radians(offset)

        # create stopping points
        self.stops = self.starts + np.radians(self.width)

        # initialize color array
        self.colors = np.zeros(self.num_bars, dtype=float)

    def eval_at(self, t):
        if t < self.first_active_time:
            self.colors[0::2] = 0.5
            self.colors[1::2] = 0.5
        elif t < self.second_active_time:
            self.colors[0::2] = 1 if self.first_active_bright else 0
            self.colors[1::2] = 0.5
        else:
            self.colors[0::2] = 1 if self.first_active_bright else 0
            self.colors[1::2] = 1 if self.second_active_bright else 0