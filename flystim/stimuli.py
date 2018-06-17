import numpy as np

from math import pi, radians

from flystim.bars import Bar
from flystim.sine import SineOpts
from flystim.reprandom import colored_noise

class SineGrating:
    def __init__(self, program, period=20, rate=10, background_color=None):
        """
        Stimulus pattern in which bars rotate around the viewer.
        :param period: Period of the bar pattern, in degrees.
        :param rate: Counter-clockwise rotation rate of the bars, in degrees per second.  Can be positive or negative.
        """

        # save settings
        self.program = program
        self.rate = rate

        # set background color
        if background_color is None:
            background_color = (0.0, 0.0, 0.0)

        self.background_color = background_color

        # compute parameters
        self.a_coeff = 0.5
        self.b_coeff = 360/period
        self.d_coeff = 0.5

    def paint_at(self, t):
        c_coeff = t*radians(self.rate)
        sine_opts = SineOpts(self.a_coeff, self.b_coeff, c_coeff, self.d_coeff)

        self.program.paint(sine_opts, self.background_color)

class RotatingBars:
    def __init__(self, program, period=20, duty_cycle=0.5, rate=10, color=1.0, background_color=None):
        """
        Stimulus pattern in which bars rotate around the viewer.
        :param period: Period of the bar pattern, in degrees.
        :param duty_cycle: Duty cycle of each bar, which should be between 0 and 1.  A value of "0" means the bar has
        zero width, and a value of "1" means that it occupies the entire period.
        :param rate: Counter-clockwise rotation rate of the bars, in degrees per second.  Can be positive or negative.
        """

        # save settings
        self.program = program
        self.rate = rate
        self.color = color

        # set background color
        if background_color is None:
            background_color = (0.0, 0.0, 0.0)

        self.background_color = background_color

        # compute parameters
        self.init_starts = np.radians(np.arange(0, 360, period, dtype='float'))
        self.init_stops = self.init_starts + duty_cycle*(self.init_starts[1]-self.init_starts[0])

    def paint_at(self, t):
        change = t*radians(self.rate)
        bars = [Bar(change+start, change+stop, color=self.color)
                for start, stop in zip(self.init_starts, self.init_stops)]

        self.program.paint(bars, self.background_color)

class ExpandingEdges:
    def __init__(self, program, period=15, width=2, rate=10, color=1.0, background_color=None):
        """
        Stimulus pattern in which bars surrounding the viewer get wider or narrower.
        :param period: Period of the bars around the viewer.
        :param width: Starting angular width of each bar.
        :param rate: The rate at which each bar grows wider in the counter-clockwise direction.  Can be negative.
        """

        # save settings
        self.program = program
        self.rate = rate
        self.color = color

        # set background color
        if background_color is None:
            background_color = (0.0, 0.0, 0.0)

        self.background_color = background_color

        # compute parameters
        self.starts = np.radians(np.arange(0, 360, period, dtype='float'))
        self.init_stops = self.starts + radians(width)

    def paint_at(self, t):
        change = t*radians(self.rate)
        bars = [Bar(start, change + stop, color=self.color)
                for start, stop in zip(self.starts, self.init_stops)]

        self.program.paint(bars, self.background_color)

class GaussianNoise:
    def __init__(self, program, period=15, vert_extent=30, width=2, gauss_mean=0.5, gauss_std=0.5, time_constant=20e-3,
                 random_seed=0, runtime=3, pts_per_tau=10, background_color=None):
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

        # save settings
        self.program = program

        # set background color
        if background_color is None:
            background_color = (0.5, 0.5, 0.5)

        self.background_color = background_color

        # create starting angles
        starts = np.radians(np.arange(0, 360, period, dtype='float'))
        starts = starts[1:] - period / 2

        # create the stopping angles
        stops = starts + radians(width)

        # create the bars
        self.bars = [Bar(theta_min=start,
                         theta_max=stop,
                         phi_min=pi/2-radians(vert_extent),
                         phi_max=pi/2+radians(vert_extent))
                     for start, stop in zip(starts, stops)]

        # make pseudo-random generators
        np.random.seed(random_seed)
        self.random_funcs = [colored_noise(loc   = gauss_mean,
                                           scale = gauss_std,
                                           tau   = time_constant,
                                           dt    = time_constant / pts_per_tau,
                                           tmax  = runtime)
                             for _ in range(len(self.bars))]

    def paint_at(self, t):
        unclipped = np.array([random_func(t) for random_func in self.random_funcs])
        colors = np.clip(unclipped, 0.0, 1.0)

        for color, bar in zip(colors, self.bars):
            bar.color = color

        self.program.paint(self.bars, self.background_color)

class SequentialBars:
    def __init__(self, program, width=5, period=20, offset=0, first_active_bright=True, second_active_bright=True,
                 first_active_time=1, second_active_time=2, background_color=None):
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

        # save settings
        self.program = program
        self.first_active_bright = first_active_bright
        self.second_active_bright = second_active_bright
        self.first_active_time = first_active_time
        self.second_active_time = second_active_time

        # set background color
        if background_color is None:
            background_color = (0.5, 0.5, 0.5)

        self.background_color = background_color

        # create starting points (two bars per period, each with given width)
        starts = np.radians(np.arange(0, 360, period, dtype='float'))
        starts = np.repeat(starts, 2)
        starts[1::2] += radians(width)

        # add offset to starting point
        starts += radians(offset)

        # create stopping points
        stops = starts + radians(width)

        # create the bars
        self.bars = [Bar(start, stop) for start, stop in zip(starts, stops)]

    def paint_at(self, t):
        if t < self.first_active_time:
            for bar in self.bars:
                bar.color = 0.5
        elif t < self.second_active_time:
            for bar in self.bars[0::2]:
                bar.color = 1 if self.first_active_bright else 0
            for bar in self.bars[1::2]:
                bar.color = 0.5
        else:
            for bar in self.bars[0::2]:
                bar.color = 1 if self.first_active_bright else 0
            for bar in self.bars[1::2]:
                bar.color = 1 if self.second_active_bright else 0

        self.program.paint(self.bars, self.background_color)