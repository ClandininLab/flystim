import numpy as np

from math import pi, radians

from flystim.base import BaseProgram

class SineGrating(BaseProgram):
    def __init__(self, screen):
        uniform_declarations = '''
        uniform float a_coeff;
        uniform float b_coeff;
        uniform float c_coeff;
        uniform float d_coeff;
        '''

        color_program = '''
        float color = a_coeff * sin(b_coeff * (theta - c_coeff)) + d_coeff;
        out_color = vec4(color, color, color, 1.0);
        '''

        super().__init__(screen=screen, uniform_declarations=uniform_declarations, color_program=color_program)

    def configure(self, period=20, rate=10, background_color=None):
        """
        Stimulus pattern in which bars rotate around the viewer.
        :param period: Period of the bar pattern, in degrees.
        :param rate: Counter-clockwise rotation rate of the bars, in degrees per second.  Can be positive or negative.
        """

        # set background color
        if background_color is None:
            background_color = (0.0, 0.0, 0.0)
        self.background_color = background_color

        # save settings
        self.rate = rate

        # set uniforms
        self.prog['a_coeff'].value = 0.5
        self.prog['b_coeff'].value = 360.0/period
        self.prog['d_coeff'].value = 0.5

    def eval_at(self, t):
        self.prog['c_coeff'].value = t*radians(self.rate)

class PeriodicBars(BaseProgram):
    def __init__(self, screen):
        uniform_declarations = '''
        uniform float theta_offset;
        uniform float theta_period;
        uniform float theta_duty;
        uniform float face_color;
        '''

        color_program = '''
        float theta_fract = fract((theta - theta_offset)/theta_period);
        if (theta_fract <= theta_duty) {
            out_color = vec4(face_color, face_color, face_color, 1.0);
        } else {
            discard;
        }
        '''

        super().__init__(screen=screen, uniform_declarations=uniform_declarations, color_program=color_program)

class RotatingBars(PeriodicBars):
    def configure(self, period=20, duty_cycle=0.5, rate=10, color=1.0, background_color=None):
        """
        Stimulus pattern in which bars rotate around the viewer.
        :param period: Period of the bar pattern, in degrees.
        :param duty_cycle: Duty cycle of each bar, which should be between 0 and 1.  A value of "0" means the bar has
        zero width, and a value of "1" means that it occupies the entire period.
        :param rate: Counter-clockwise rotation rate of the bars, in degrees per second.  Can be positive or negative.
        """

        # set background color
        if background_color is None:
            background_color = (0.0, 0.0, 0.0)
        self.background_color = background_color

        # save settings
        self.rate = rate

        # set uniforms
        self.prog['theta_period'].value = radians(period)
        self.prog['theta_duty'].value = duty_cycle
        self.prog['face_color'].value = color

    def eval_at(self, t):
        self.prog['theta_offset'].value = t*radians(self.rate)

class ExpandingEdges(PeriodicBars):
    def configure(self, period=15, width=2, rate=10, color=1.0, background_color=None):
        """
        Stimulus pattern in which bars surrounding the viewer get wider or narrower.
        :param period: Period of the bars around the viewer.
        :param width: Starting angular width of each bar.
        :param rate: The rate at which each bar grows wider in the counter-clockwise direction.  Can be negative.
        """

        # set background color
        if background_color is None:
            background_color = (0.0, 0.0, 0.0)
        self.background_color = background_color

        # save settings
        self.rate = rate
        self.width = width
        self.period = period

        # set uniforms
        self.prog['theta_period'].value = radians(period)
        self.prog['theta_offset'].value = 0.0
        self.prog['face_color'].value = color

    def eval_at(self, t):
        self.prog['theta_duty'].value = (self.width + t*self.rate)/self.period

class GaussianNoise(BaseProgram):
    def __init__(self, screen, max_face_colors=128):
        self.max_face_colors = max_face_colors

        uniform_declarations = '#define MAX_FACE_COLORS {}\n'.format(self.max_face_colors)
        uniform_declarations += '''
        #define M_TWO_PI 6.2831853072
        
        uniform float phi_min;
        uniform float phi_max;
        uniform float theta_period;
        uniform float theta_offset;
        uniform float theta_duty;
        uniform float face_colors[MAX_FACE_COLORS];
        '''

        color_program = '''
        float face_color;
        float theta_rel = theta - theta_offset;
        if ((phi_min <= phi) && (phi <= phi_max) && (fract(theta_rel/theta_period) <= theta_duty)){
            if (theta_rel < 0) {
                theta_rel += M_TWO_PI;
            }
            face_color = face_colors[int(theta_rel/theta_period)];
            out_color = vec4(face_color, face_color, face_color, 1.0);
        } else {
            discard;
        }
        '''

        super().__init__(screen=screen, uniform_declarations=uniform_declarations, color_program=color_program)

    def configure(self, period=15, vert_extent=30, width=2, rand_min=0.0, rand_max=1.0, start_seed=0,
                  update_rate=60.0, background_color=None):
        """
        Bars surrounding the viewer change brightness randomly.
        :param period: Period of the bars surrounding the viewer.
        :param vert_extent: Vertical extent of each bar, in degrees.  With respect to the equator of the viewer, the
        top of each bar is at +vert_extent (degrees) and the bottom is at -vert_extent (degrees)
        :param width: Width of each bar in degrees.
        :param rand_min: Minimum output of random number generator
        :param rand_max: Maximum output of random number generator
        :param start_seed: Starting seed for the random number generator
        :param update_rate: Rate at which color is updated
        """

        # set background color
        if background_color is None:
            background_color = (0.5, 0.5, 0.5)
        self.background_color = background_color

        # save settings
        self.rand_min = rand_min
        self.rand_max = rand_max
        self.start_seed = start_seed
        self.update_rate = update_rate

        # calculate number of bars
        self.num_bars = 360//period
        self.padding  = np.zeros(self.max_face_colors - self.num_bars)

        # create the bars
        self.prog['phi_min'].value = pi/2-radians(vert_extent)
        self.prog['phi_max'].value = pi/2+radians(vert_extent)
        self.prog['theta_period'].value = radians(period)
        self.prog['theta_offset'].value = -radians(period)/2.0
        self.prog['theta_duty'].value = width/period

    def eval_at(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)

        # compute colors
        face_colors = np.random.uniform(self.rand_min, self.rand_max, self.num_bars)

        # write to GPU
        self.prog['face_colors'].value = list(np.concatenate((face_colors, self.padding)))

class SequentialBars(BaseProgram):
    def __init__(self, screen):
        uniform_declarations = '''
        uniform float theta_offset;
        uniform float theta_period;
        uniform float thresh_first;
        uniform float thresh_second;
        uniform float color_first;
        uniform float color_second;
        uniform bool  enable_first;
        uniform bool  enable_second;
        '''

        color_program = '''
        float theta_fract = fract((theta - theta_offset)/theta_period);
        if (enable_first && (theta_fract <= thresh_first)) {
            out_color = vec4(color_first, color_first, color_first, 1.0);
        } else if (enable_second && (thresh_first < theta_fract) && (theta_fract <= thresh_second)) {
            out_color = vec4(color_second, color_second, color_second, 1.0);
        } else {
            discard;
        }
        '''

        super().__init__(screen=screen, uniform_declarations=uniform_declarations, color_program=color_program)

    def configure(self, width=5, period=20, offset=0, first_active_bright=True, second_active_bright=True,
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

        # set background color
        if background_color is None:
            background_color = (0.5, 0.5, 0.5)
        self.background_color = background_color

        # save settings
        self.first_active_time  = first_active_time
        self.second_active_time = second_active_time

        # configure program
        self.prog['theta_offset'].value  = offset
        self.prog['theta_period'].value  = radians(period)
        self.prog['thresh_first'].value  = 1.0*width/period
        self.prog['thresh_second'].value = 2.0*width/period
        self.prog['color_first'].value = 1.0 if first_active_bright else 0.0
        self.prog['color_second'].value = 1.0 if second_active_time else 0.0

    def eval_at(self, t):
        self.prog['enable_first'].value = (t >= self.first_active_time)
        self.prog['enable_second'].value = (t >= self.second_active_time)