import random
import numpy as np

from math import pi, radians, ceil
from scipy.interpolate import interp1d

from flystim.base import BaseProgram
from flystim.glsl import Uniform

class SineGrating(BaseProgram):
    def __init__(self, screen):
        uniforms = [
            Uniform('min_color', float),
            Uniform('max_color', float),
            Uniform('num_period', int),
            Uniform('offset', float)
        ]

        calc_color = '''
            color = 0.5*(max_color-min_color)*sin(num_period*(theta-offset)) + 0.5*(min_color+max_color);
        '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

    def configure(self, period=20, rate=10, min_color=0.0, max_color=1.0):
        """
        Stimulus pattern in which bars rotate around the viewer.
        :param period: Period of the bar pattern, in degrees.
        :param rate: Counter-clockwise rotation rate of the bars, in degrees per second.  Can be positive or negative.
        :param min_color: Minimum color to be displayed
        :param max_color: Minimum color to be displayed
        """

        # save settings
        self.rate = rate

        # set uniforms
        self.prog['min_color'].value = min_color
        self.prog['max_color'].value = max_color
        self.prog['num_period'].value = 360//period

    def eval_at(self, t):
        self.prog['offset'].value = t*radians(self.rate)

class PeriodicBars(BaseProgram):
    def __init__(self, screen):
        uniforms = [
            Uniform('theta_offset', float),
            Uniform('theta_period', float),
            Uniform('theta_duty', float),
            Uniform('face_color', float),
            Uniform('background', float)
        ]

        calc_color = '''
            float theta_fract = fract((theta - theta_offset)/theta_period);
            if (theta_fract <= theta_duty) {
                color = face_color;
            } else {
                color = background;
            }
        '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

class RotatingBars(PeriodicBars):
    def configure(self, period=20, duty_cycle=0.5, rate=10, color=1.0, background=0.0):
        """
        Stimulus pattern in which bars rotate around the viewer.
        :param period: Period of the bar pattern, in degrees.
        :param duty_cycle: Duty cycle of each bar, which should be between 0 and 1.  A value of "0" means the bar has
        zero width, and a value of "1" means that it occupies the entire period.
        :param rate: Counter-clockwise rotation rate of the bars, in degrees per second.  Can be positive or negative.
        :param color: Monochromatic bar color (0.0 is black, 1.0 is white)
        :param background: Monochromatic background color (0.0 is black, 1.0 is white)
        """

        # save settings
        self.rate = rate

        # set uniforms
        self.prog['theta_period'].value = radians(period)
        self.prog['theta_duty'].value = duty_cycle
        self.prog['face_color'].value = color
        self.prog['background'].value = background

    def eval_at(self, t):
        self.prog['theta_offset'].value = t*radians(self.rate)

class MovingPatch(BaseProgram):
    def __init__(self, screen):
        uniforms = [
            Uniform('theta_center', float),
            Uniform('phi_center', float),
            Uniform('theta_width', float),
            Uniform('phi_width', float),
            Uniform('face_color', float),
            Uniform('background', float)
        ]

        # reference for modular arithmetic: https://fgiesen.wordpress.com/2015/09/24/intervals-in-modular-arithmetic/

        calc_color = '''
            // original longitude / latitude coordinates of this pixel 
            float t1 = theta;
            float p1 = phi;
            
            // equivalent representation of the pixel coordinates
            float t2 = theta + M_PI;
            float p2 = -phi;
            
            // minimum longitude / latitude coordinates of the patch
            float min_t = theta_center - theta_width/2.0;
            float min_p = phi_center - phi_width/2.0;
                   
            // check if either representation of the pixel coordinates lies inside the patch        
            if (((mod(t1 - min_t, 2*M_PI) <= theta_width)  && 
                 (mod(p1 - min_p, 2*M_PI) <= phi_width)) ||
                ((mod(t2 - min_t, 2*M_PI) <= theta_width)  && 
                 (mod(p2 - min_p, 2*M_PI) <= phi_width))) {
                color = face_color;
            } else {
                color = background;
            }
        '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

    def configure(self, theta_width=5, phi_width=5, color=1.0, background=0.0, trajectory=None, method='linear'):
        """
        Stimulus consisting of a patch that moves along an arbitrary trajectory.
        :param theta_width: Longitude width of the patch (degrees)
        :param phi_width: Latitude width of the patch (degrees)
        :param color: Color of the patch (0.0 to 1.0)
        :param background: Background color (0.0 to 1.0)
        :param trajectory: List of 3-tuples (time, longitude, latitude) to specify the waypoints of the patch
        trajectory.  Longitude and latitude are specified in degrees.
        :param method: Interpolation method used to compute patch position at times in between waypoints.  Allowed
        values are those accepted by scipy.interpolate.interp1d (‘linear’, ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’,
        ‘cubic’, ‘previous’, ‘next’)
        """

        # create interpolators for longitude and latitude
        times, lons, lats = zip(*trajectory)
        self.lon_interp = interp1d(times, np.radians(lons), kind=method, fill_value='extrapolate')
        self.lat_interp = interp1d(times, np.radians(lats), kind=method, fill_value='extrapolate')

        # set uniforms
        self.prog['theta_width'].value = radians(theta_width)
        self.prog['phi_width'].value = radians(phi_width)
        self.prog['face_color'].value = color
        self.prog['background'].value = background

    def eval_at(self, t):
        self.prog['theta_center'].value = self.lon_interp(t)
        self.prog['phi_center'].value   = self.lat_interp(t)

class ExpandingEdges(PeriodicBars):
    def configure(self, period=15, width=2, rate=10, color=1.0, background=0.0):
        """
        Stimulus pattern in which bars surrounding the viewer get wider or narrower.
        :param period: Period of the bars around the viewer.
        :param width: Starting angular width of each bar.
        :param rate: The rate at which each bar grows wider in the counter-clockwise direction.  Can be negative.
        :param background: Monochromatic background color (0.0 is black, 1.0 is white)
        """

        # save settings
        self.rate = rate
        self.width = width
        self.period = period

        # set uniforms
        self.prog['theta_period'].value = radians(period)
        self.prog['theta_offset'].value = 0.0
        self.prog['face_color'].value = color
        self.prog['background'].value = background

    def eval_at(self, t):
        self.prog['theta_duty'].value = (self.width + t*self.rate)/self.period

class RandomBars(BaseProgram):
    def __init__(self, screen, max_face_colors=64):
        self.max_face_colors = max_face_colors

        uniforms = [
            Uniform('phi_min', float),
            Uniform('phi_max', float),
            Uniform('theta_min', float),
            Uniform('theta_max', float),
            Uniform('theta_period', float),
            Uniform('theta_offset', float),
            Uniform('theta_duty', float),
            Uniform('background', float),
            Uniform('face_colors', float, max_face_colors)
        ]

        calc_color = '''
            float theta_rel = theta - theta_offset;
            if ((phi_min <= phi) && (phi <= phi_max) && (fract(theta_rel/theta_period) <= theta_duty)){
                if (theta_rel < 0) {
                    theta_rel += 2*M_PI;
                }
                color = face_colors[int(theta_rel/theta_period)];
            } else {
                color = background;
            }
        '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

    def configure(self, period=15, vert_extent=30, width=2, rand_min=0.0, rand_max=1.0, start_seed=0,
                  update_rate=60.0, background=0.5):
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
        :param background: Monochromatic background color (0.0 is black, 1.0 is white)
        """

        # save settings
        self.rand_min = rand_min
        self.rand_max = rand_max
        self.start_seed = start_seed
        self.update_rate = update_rate

        # create the bars
        self.prog['phi_min'].value = pi/2-radians(vert_extent)
        self.prog['phi_max'].value = pi/2+radians(vert_extent)
        self.prog['theta_period'].value = radians(period)
        self.prog['theta_offset'].value = -radians(period)/2.0
        self.prog['theta_duty'].value = width/period
        self.prog['background'].value = background

    def eval_at(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        random.seed(seed)

        # compute the list of random values
        rand_colors = [random.uniform(self.rand_min, self.rand_max) for _ in range(self.max_face_colors)]

        # write to GPU
        self.prog['face_colors'].value = rand_colors

class SequentialBars(BaseProgram):
    def __init__(self, screen):
        uniforms = [
            Uniform('theta_offset', float),
            Uniform('theta_period', float),
            Uniform('thresh_first', float),
            Uniform('thresh_second', float),
            Uniform('color_first', float),
            Uniform('color_second', float),
            Uniform('background', float),
            Uniform('enable_first', bool),
            Uniform('enable_second', bool)
        ]

        calc_color = '''
            float theta_fract = fract((theta - theta_offset)/theta_period);
            if (enable_first && (theta_fract <= thresh_first)) {
                color = color_first;
            } else if (enable_second && (thresh_first < theta_fract) && (theta_fract <= thresh_second)) {
                color = color_second;
            } else {
                color = background;
            }
        '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

    def configure(self, width=5, period=20, offset=0, first_active_bright=True, second_active_bright=True,
                 first_active_time=1, second_active_time=2, background=0.5):
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
        :param background: Monochromatic background color (0.0 is black, 1.0 is white)
        """

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
        self.prog['background'].value = background

    def eval_at(self, t):
        self.prog['enable_first'].value = (t >= self.first_active_time)
        self.prog['enable_second'].value = (t >= self.second_active_time)

class GridStim(BaseProgram):
    def __init__(self, screen, max_face_colors=512):
        self.max_face_colors = max_face_colors

        uniforms = [
            Uniform('num_theta', int),
            Uniform('phi_period', float),
            Uniform('theta_period', float),
            Uniform('face_colors', float, max_face_colors)
        ]

        calc_color = '''
            if (theta < 0) {
                theta += 2*M_PI;
            } 
            
            int theta_int = int(theta/theta_period);
            int phi_int = int(phi/phi_period);
            
            color = face_colors[theta_int + num_theta*phi_int]; 
        '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

class RandomGrid(GridStim):
    def configure(self, theta_period=15, phi_period=15, rand_min=0.0, rand_max=1.0, start_seed=0,
                  update_rate=60.0):
        """
        Patches surrounding the viewer change brightness randomly.
        :param theta_period: Longitude period of the checkerboard patches (degrees)
        :param phi_period: Latitude period of the checkerboard patches (degrees)
        :param rand_min: Minimum output of random number generator
        :param rand_max: Maximum output of random number generator
        :param start_seed: Starting seed for the random number generator
        :param update_rate: Rate at which color is updated
        """

        # save settings
        self.rand_min = rand_min
        self.rand_max = rand_max
        self.start_seed = start_seed
        self.update_rate = update_rate

        # write program settings
        self.prog['num_theta'].value = 360 // theta_period
        self.prog['phi_period'].value = radians(phi_period)
        self.prog['theta_period'].value = radians(theta_period)

    def eval_at(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        random.seed(seed)

        # compute random values
        rand_values = [random.uniform(self.rand_min, self.rand_max) for _ in range(self.max_face_colors)]

        # write to GPU
        self.prog['face_colors'].value = rand_values

class Checkerboard(GridStim):
    def configure(self, theta_period=15, phi_period=15):
        """
        Patches surrounding the viewer are arranged in a periodic checkerboard.
        :param theta_period: Longitude period of the checkerboard patches (degrees)
        :param phi_period: Latitude period of the checkerboard patches (degrees)
        """

        # calculate number of bars
        num_theta = 360 // theta_period
        num_phi = 180 // phi_period
        num_faces = num_theta * num_phi
        assert num_faces <= self.max_face_colors

        # write program settings
        self.prog['num_theta'].value = num_theta
        self.prog['phi_period'].value = radians(phi_period)
        self.prog['theta_period'].value = radians(theta_period)

        # create the pattern
        face_colors  = ([0.0, 1.0] * int(ceil(num_theta/2)))[:num_theta]
        face_colors += ([1.0, 0.0] * int(ceil(num_theta/2)))[:num_theta]
        face_colors *= int(ceil(num_phi/2))
        face_colors  = face_colors[:num_faces]
        face_colors += [0.0]*(self.max_face_colors - num_faces)

        # write the pattern
        self.prog['face_colors'].value = face_colors
