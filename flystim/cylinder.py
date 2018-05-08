import pyglet.gl as gl
import numpy as np

from flystim import graphics
from flystim.reprandom import colored_noise

class CylinderStim:
    def __init__(self, radius=2.0, height=10.0, background=None):
        """
        Base class for cylindrical stimuli.  Not intended to be instantiated directly.
        :param radius: Radius of cylindrical bar placement with respect to the origin.
        :param height: Height of cylindrical bars, which extend from -height/2 to +height/2
        :param background: Background color used for stimuli as an (R, G, B) tuple, with each color between 0 and 1.
        """

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
        """
        Number of bars in the cylindrical stimulus.
        """

        return len(self.starts)

    def eval_at(self, t):
        """
        Evaluates the stimulus at a given time.
        :param t: Current time with respect to the start of the stimulus animation, in seconds.
        """

        pass

    def draw(self):
        """
        Draws the stimulus pattern.  Each bar in the stimulus has a start angle, stop angle, and monochrome color
        from 0 to 1.  This code draws each bar as a GL_QUAD with the appropriate color.
        """

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
        """
        Stimulus pattern in which bars rotate around the viewer.
        :param period: Period of the bar pattern, in degrees.
        :param duty_cycle: Duty cycle of each bar, which should be between 0 and 1.  A value of "0" means the bar has
        zero width, and a value of "1" means that it occupies the entire period.
        :param rate: Counter-clockwise rotation rate of the bars, in degrees per second.  Can be positive or negative.
        """

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
        """
        Stimulus pattern in which bars surrounding the viewer get wider or narrower.
        :param period: Period of the bars around the viewer.
        :param width: Starting angular width of each bar.
        :param rate: The rate at which each bar grows wider in the counter-clockwise direction.  Can be negative.
        """

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
        """
        Bars surrounding the viewer change brightness randomly.
        :param period: Period of the bars surrounding the viewer.
        :param vert_extent: Vertical extent of each bar, in degrees.  With respect to the equator of the viewer, the
        top of each bar is at +vert_extent (degrees) and the bottom is at -vert_extent (degrees)
        :param width: Width of each bar in degrees.
        :param gauss_mean: Mean brightness (from 0 to 1).
        :param gauss_std: Standard deviation of brightness.
        :param time_constant: Time constant of the autocorrelation of the random brightness assigned to each bar.
        :param random_seed: Seed used to generate psuedorandom data.  Two instances of this stimulus with the same
        seed should produce identical patterns.
        :param runtime: Maximum length of the stimulus (needed to precompute the noise pattern).  If the stimulus runs
        longer that this time, it will hold the value at runtime.
        :param pts_per_tau: Time resolution of the filtering code that implements the colored noise profile.  It is
        expressed as the number of time points per time_constant.  For example, if time_constant=20e-3 and
        pts_per_tau=10, the time resolution of the calculation is 2e-3.
        """

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
        """
        Stimulus in which one set of bars appears first, followed by a second set some time later.
        :param width: Width of the bars (same for the first and second set).
        :param period: Period of the bar pattern (same for the first and second set).
        :param offset: Offset in degrees of the bar pattern, which can be used to rotate the entire pattern
        around the viewer.
        :param first_active_bright: Boolean value.  If True, the first set of bars appear white when active.  If
        False, they will appear black when active.
        :param second_active_bright: Boolean value.  If True, the second set of bars appear white when active.  If
        False, they will appear black when active.
        :param first_active_time: Time in seconds when the first set of bars become active.
        :param second_active_time: Time in seconds when the second set of bars become active.
        """
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