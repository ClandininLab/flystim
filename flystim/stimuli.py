import random
import numpy as np
import moderngl

from math import pi, radians, ceil, cos, sin

from flystim.base import BaseProgram
from flystim.glsl import Uniform, Function, Variable, Texture
from flystim.trajectory import RectangleTrajectory, Trajectory
import flystim.distribution as distribution
from flystim import GlSphericalRect, GlCylinder

class ConstantBackground(BaseProgram):
    # keep as-is
    def __init__(self, screen):
        uniforms = [
            Uniform('background', float)
        ]

        calc_color = 'color = background;\n'

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

    def configure(self, background=0.0):
        """
        :param background
        """

        self.prog['background'].value = background

    def eval_at(self, t):
        pass

class ContrastReversingGrating(BaseProgram):
    # change to vertical bars with the cylinder itself rotating along 2 angles
    def __init__(self, screen):
        uniforms = [
            Uniform('contrast_scale', float),
            Uniform('mean', float),
            Uniform('k_theta', float),
            Uniform('k_phi', float),
            Uniform('contrast', float)
        ]

        grating = Function(name='rect_grating',
                           in_vars=[Variable('phase', float)],
                           out_type=float,
                           code='return (fract(phase/(2.0*M_PI)) <= 0.5) ? 1.0 : -1.0;')


        calc_color = ''
        calc_color += 'float spatial_contrast = {}(k_theta*theta + k_phi*phi);\n'.format(grating.name)
        calc_color += 'color = mean + spatial_contrast*contrast*contrast_scale*mean;\n'

        super().__init__(screen=screen, uniforms=uniforms, functions=[grating], calc_color=calc_color)

    def configure(self, spatial_period=10, temporal_frequency=1.0, contrast_scale=1.0, mean=0.5, angle=0.0, temporal_waveform='sine'):
        """
        Stationary periodic grating whose contrast is modulated as a function of time
        :param spatial_period: Spatial period of the grating, in degrees.
        :param temporal_frequency: temporal_frequency of the contrast modulation, in Hz
        :param mean: Mean intensity of grating (midpoint of wave). Should be between [0,0.5] to prevent clipping
        :param contrast_scale: multiplier on mean intensity to determine wave peak/trough
            wave peak = mean + contrast_scale * mean
            wave trough = mean - contrast_scale * mean
            *spatial and temporal contrast values [-1,1] multiply variations above and below the mean
        :param angle: Tilt angle (in degrees) of the grating.  0 degrees will align the grating with a line of
        longitude.
        """
        # save settings
        self.temporal_frequency = temporal_frequency
        self.temporal_waveform = temporal_waveform

        # compute wavevector
        self.k = 2*pi/radians(spatial_period)
        self.prog['k_theta'].value = self.k*cos(radians(angle))
        self.prog['k_phi'].value   = self.k*sin(radians(angle))

        # set color uniforms
        self.prog['contrast_scale'].value = contrast_scale #[0, 1] contrast, relative to mean
        self.prog['mean'].value = mean #[0,0.5], intensity

    def eval_at(self, t):
        if self.temporal_waveform == 'sine':
            self.prog['contrast'].value = sin(2 * pi * self.temporal_frequency * t) #lives on [-1, 1]
        elif self.temporal_waveform == 'square':
            self.prog['contrast'].value = np.sign(sin(2 * pi * self.temporal_frequency * t)) #element of [-1, 1]


class PeriodicGrating(BaseProgram):
    def __init__(self, screen, grating):
        uniforms = [
            Uniform('face_color', float),
            Uniform('background', float),
            Uniform('k_theta', float),
            Uniform('k_phi', float),
            Uniform('omega', float),
            Uniform('offset', float),
            Uniform('t', float)
        ]

        calc_color = ''
        calc_color += 'float intensity = {}(k_theta*theta + k_phi*phi - omega*t + offset);\n'.format(grating.name)
        calc_color += 'color = mix(background, face_color, intensity);\n'

        super().__init__(screen=screen, uniforms=uniforms, functions=[grating], calc_color=calc_color)

    def configure(self, period=20, rate=10, color=1.0, background=0.0, angle=45.0, offset=0.0):
        """
        Stimulus pattern in which a periodic grating moves as a wavefront
        :param period: Spatial period of the grating, in degrees.
        :param rate: Velocity of the grating movement, in degrees per second.  Can be positive or negative.
        :param color: Color shown at peak intensity.
        :param background: Color shown at minimum intensity.
        :param angle: Tilt angle (in degrees) of the grating.  0 degrees will align the grating with a line of
        longitude.
        """

        # save settings
        self.rate = radians(rate)
        self.offset = radians(offset)

        # compute wavevector
        self.k = 2*pi/radians(period)
        self.prog['k_theta'].value = self.k*cos(radians(angle))
        self.prog['k_phi'].value   = self.k*sin(radians(angle))

        # push omega and offset to graphics card
        self.push_changes()

        # set color uniforms
        self.prog['face_color'].value = color
        self.prog['background'].value = background

    def push_changes(self):
        self.prog['omega'].value = self.rate * self.k
        self.prog['offset'].value = self.offset

    def update_stim(self, rate, t):
        old_rate = self.rate
        new_rate = radians(rate)

        old_offset = self.offset
        new_offset = (new_rate - old_rate)*self.k*t + old_offset

        self.rate = new_rate
        self.offset = new_offset

        self.push_changes()

    def eval_at(self, t):
        self.prog['t'].value = t


class SineGrating(PeriodicGrating):
    # treated the same way as contrast reversing
    def __init__(self, screen):
        # define grating function
        grating = Function(name='sine_grating',
                           in_vars=[Variable('phase', float)],
                           out_type=float,
                           code='return 0.5*sin(phase) + 0.5;')

        # call super constructor
        super().__init__(screen=screen, grating=grating)


class RectGrating(PeriodicGrating):
    # treated the same way as contrast reversing
    def __init__(self, screen):
        # define grating function
        grating = Function(name='rect_grating',
                           in_vars=[Variable('phase', float)],
                           out_type=float,
                           uniforms=[Uniform('duty_cycle', float)],
                           code='return (fract(phase/(2.0*M_PI)) <= duty_cycle) ? 1.0 : 0.0;')

        # call super constructor
        super().__init__(screen=screen, grating=grating)


class ExpandingEdges(RectGrating):
    # treated the same way as contrast reversing
    def configure(self, init_width=2, expand_rate=10, period=15, rate=0, **kwargs):
        """
        Stimulus pattern in which bars surrounding the viewer get wider or narrower.
        :param width: Starting angular width of each bar.
        :param expand_rate: The rate at which each bar grows wider in the counter-clockwise direction.  Can be negative.
        :param period: Spatial period of the grating, in degrees.
        :param rate: Velocity of the grating movement, in degrees per second.  Typically left at zero for this stimulus.
        """

        # save settings
        self.init_width = init_width
        self.expand_rate = expand_rate
        self.period = period

        # call configuration method from parent class
        super().configure(period=period, rate=rate, **kwargs)

    def eval_at(self, t):
        # adjust duty cycle
        self.prog['duty_cycle'].value = (self.init_width + t*self.expand_rate)/self.period

        # call evaluation method of the parent class
        super().eval_at(t)


class MovingPatch(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=10, height=10, sphere_radius=1, color=[1, 1, 1, 1], theta=-180, phi=0):
        """
        Stimulus consisting of a patch that moves along an arbitrary trajectory.
        :param background: Background color (0.0 to 1.0)
        :param trajectory: RectangleTrajectory converted to dictionary (to_dict method)
        """
        self.width = width
        self.height = height
        self.sphere_radius = sphere_radius
        self.color = color
        self.theta = theta
        self.phi = phi

    def eval_at(self, t):
        if type(self.width) is dict:
            self.width = Trajectory.from_dict(self.width).eval_at(t)
        if type(self.height) is dict:
            self.height = Trajectory.from_dict(self.height).eval_at(t)
        if type(self.color) is dict:
            self.color = Trajectory.from_dict(self.color).eval_at(t)
        if type(self.theta) is dict:
            self.theta = Trajectory.from_dict(self.theta).eval_at(t)
        if type(self.phi) is dict:
            self.phi = Trajectory.from_dict(self.phi).eval_at(t)

        self.stim_object = GlSphericalRect(width=self.width,
                                           height=self.height,
                                           sphere_radius=self.sphere_radius,
                                           color=self.color).rotz(radians(self.theta)).roty(radians(self.phi))


class RotatingBars(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, period=20, rate=10, color=[1, 1, 1, 1], background=0.0, angle=45.0, offset=0.0, cylinder_radius=1):
        """

        """
        self.period = period
        self.rate = rate
        self.color = color
        self.background = background
        self.angle = angle
        self.offset = offset
        self.cylinder_radius = cylinder_radius

    def eval_at(self, t):
        self.stim_object = GlCylinder(cylinder_height=20.0,
                                      cylinder_radius=self.cylinder_radius,
                                      color=self.color,
                                      texture=True).rotz(radians(self.rate*t)).rotx(radians(self.angle))

        # make the texture image
        # TODO: integrate spatial period, background and offset into this grating
        dim = 512
        sf = 20/(2*np.pi)  # cycles per radian
        xx = np.linspace(0, 2*np.pi, dim)
        yy = 255*((0.5 + 0.5*(np.sin(sf*2*np.pi*xx))) > 0.5)
        img = np.tile(yy, (dim, 1)).astype(np.uint8)
        self.texture_image = img

class RandomBars(BaseProgram):
    # cylindrical mode
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
            Uniform('face_colors', float, max_face_colors),
            Uniform('red_gun', float),
            Uniform('green_gun', float),
            Uniform('blue_gun', float),
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

        rgb = '''
            red = red_gun;
            green = green_gun;
            blue = blue_gun;
            '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color, rgb=rgb)

    def configure(self, period=15, vert_extent=30, width=2, rand_min=0.0, rand_max=1.0, start_seed=0,
                  update_rate=60.0, background=0.5, theta_offset=None, rgb=(1.0,1.0,1.0)):
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
        if theta_offset is None:
            self.prog['theta_offset'].value = -radians(period)/2.0
        else:
            self.prog['theta_offset'].value = radians(theta_offset)
        self.prog['theta_duty'].value = width/period
        self.prog['background'].value = background

        self.prog['red_gun'].value = rgb[0]
        self.prog['green_gun'].value = rgb[1]
        self.prog['blue_gun'].value = rgb[2]

    def eval_at(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        random.seed(seed)

        # compute the list of random values
        rand_colors = [random.uniform(self.rand_min, self.rand_max) for _ in range(self.max_face_colors)]

        # write to GPU
        self.prog['face_colors'].value = rand_colors

class SequentialBars(BaseProgram):
    # consider removing...
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
    # render on a cylinder with the height of patches adjusted for equal solid angle.
    # cylinder type stimulus
    def __init__(self, screen, max_theta=256, max_phi=128):
        # initialize the random map
        self.max_theta = max_theta
        self.max_phi = max_phi

        uniforms = [
            Uniform('phi_period', float),
            Uniform('theta_period', float),
            Texture('grid_values')
        ]

        calc_color = '''
            if (theta < 0) {
                theta += 2*M_PI;
            }

            int theta_int = int(theta/theta_period);
            int phi_int = int(phi/phi_period);

            color = texelFetch(grid_values, ivec2(theta_int, phi_int), 0).r;
        '''

        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)

    def initialize(self, ctx):
        # ref: https://github.com/cprogrammer1994/ModernGL/blob/6b0f5851539da4170596f62456bac0c22024e754/examples/conways_game_of_life.py
        patches = np.zeros((self.max_phi, self.max_theta)).astype('f4')
        self.texture = ctx.texture((self.max_theta, self.max_phi), 1, patches.tobytes(), dtype='f4')
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.texture.swizzle = 'RRR1'
        self.texture.use()

        super().initialize(ctx)


class RandomGrid(GridStim):
    def make_config_options(self, *args, distribution_data=None, **kwargs):
        if distribution_data is None:
            distribution_data = {'name':'Uniform',
                                 'args':[0, 1],
                                 'kwargs':{}}

        noise_distribution = getattr(distribution,distribution_data['name'])(*distribution_data.get('args',[]), **distribution_data.get('kwargs',{}))

        return super().make_config_options(*args, noise_distribution=noise_distribution, **kwargs)

    def configure(self, theta_period=15, phi_period=15, start_seed=0, update_rate=60.0,
                  noise_distribution = None):
        """
        Patches surrounding the viewer change brightness randomly.
        :param theta_period: Longitude period of the checkerboard patches (degrees)
        :param phi_period: Latitude period of the checkerboard patches (degrees)
        :param start_seed: Starting seed for the random number generator
        :param update_rate: Rate at which color is updated
        :param distribution_data: dict of distribution type and args, see flystim.distribution method
        """

        # save settings
        self.start_seed = start_seed
        self.update_rate = update_rate

        # write program settings
        self.prog['phi_period'].value = radians(phi_period)
        self.prog['theta_period'].value = radians(theta_period)

        # get the noise distribution
        self.noise_distribution = noise_distribution

    def eval_at(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)

        face_colors = self.noise_distribution.get_random_values((self.max_phi, self.max_theta))

        # write to GPU
        self.texture.write(face_colors.astype('f4'))
        self.texture.use()

class Checkerboard(GridStim):
    # changing to cylinder style
    def configure(self, theta_period=2, phi_period=2):
        """
        Patches surrounding the viewer are arranged in a periodic checkerboard.
        :param theta_period: Longitude period of the checkerboard patches (degrees)
        :param phi_period: Latitude period of the checkerboard patches (degrees)
        """

        # write program settings
        self.prog['phi_period'].value = radians(phi_period)
        self.prog['theta_period'].value = radians(theta_period)

        # create the pattern
        # row = y (phi) coord
        # col = x (theta) coord
        face_colors  = np.zeros((self.max_phi, self.max_theta))
        face_colors[0::2, 0::2] = 1
        face_colors[1::2, 1::2] = 1

        # write the pattern
        self.texture.write(face_colors.astype('f4'))

    def eval_at(self, t):
        self.texture.use()

class ArbitraryGrid(BaseProgram):
    # changing to cylinder style
    def __init__(self, screen):
        uniforms = [
            Uniform('stixel_size', float),
            Uniform('min_y', float),
            Uniform('max_y', float),
            Uniform('min_x', float),
            Uniform('max_x', float),
            Uniform('background', float),
            Texture('grid_values')
        ]

        calc_color = '''
            if (theta < 0) {
                theta += 2*M_PI;
            }
            if (phi < 0) {
                phi += M_PI;
            }

            if ((min_y <= phi) && (phi <= max_y) && (min_x <= theta) && (theta <= max_x)) {

                    int theta_int = int((theta - min_x)/stixel_size);
                    int phi_int = int((phi - min_y)/stixel_size);

                    color = texelFetch(grid_values, ivec2(theta_int, phi_int), 0).r;
            } else {
                color = background;
            }


        '''
        super().__init__(screen=screen, uniforms=uniforms, calc_color=calc_color)


    def initialize(self, ctx):
        self.ctx = ctx
        super().initialize(self.ctx)

    def initTexture(self, num_phi, num_theta):
        # ref: https://github.com/cprogrammer1994/ModernGL/blob/6b0f5851539da4170596f62456bac0c22024e754/examples/conways_game_of_life.py
        patches = self.background * np.ones((num_phi, num_theta)).astype('f4')
        self.texture = self.ctx.texture((num_theta, num_phi), 1, patches.tobytes(), dtype='f4')
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.texture.swizzle = 'RRR1'
        self.texture.use()

    def configure(self, stixel_size = 10, num_theta = 20, num_phi = 20, t_dim = 100, update_rate = 30,
                  center_theta = 0, center_phi = 0, background = 0.5,
                  stimulus_code = None, encoding_scheme = 'ternary_dense'):
        """
        Patches surrounding the viewer are arranged in an arbitrary grid stimulus
        :param theta_period: Longitude period of the checkerboard patches (degrees)
        :param phi_period: Latitude period of the checkerboard patches (degrees)
        """
        self.stixel_size = stixel_size
        self.num_theta = num_theta
        self.num_phi = num_phi
        self.t_dim = t_dim
        self.update_rate = update_rate
        self.background = background

        self.stimulus_code = stimulus_code

        width_phi = self.num_phi * self.stixel_size
        width_theta = self.num_theta * self.stixel_size

        # write program settings
        self.prog['stixel_size'].value = radians(self.stixel_size)
        self.prog['min_y'].value = radians(center_phi - width_phi / 2)
        self.prog['max_y'].value = radians(center_phi + width_phi / 2)
        self.prog['min_x'].value = radians(center_theta - width_theta / 2)
        self.prog['max_x'].value = radians(center_theta + width_theta / 2)
        self.prog['background'].value = self.background

        # create the pattern
        # row = y (phi) coord
        # col = x (theta) coord
        if stimulus_code is None:
            self.stimulus_code = np.zeros((self.num_phi, self.num_theta, self.t_dim))

        if encoding_scheme == 'ternary_dense':
            self.xyt_stimulus = np.array(self.stimulus_code).reshape(self.num_phi, self.num_theta, self.t_dim)

        elif encoding_scheme == 'single_spot':
            row, col = self.getRowColumnFromLocation(self.stimulus_code, self.num_phi, self.num_theta)
            self.xyt_stimulus = self.background * np.ones((self.num_phi,self.num_theta, self.t_dim))
            for ff in range(self.xyt_stimulus.shape[2]):
                self.xyt_stimulus[col[ff], row[ff], ff] = 1

        # initialize texture
        self.initTexture(self.num_phi, self.num_theta)

    def getRowColumnFromLocation(self, location, y_dim, x_dim):
        row = np.mod(location, x_dim) - 1
        col = np.mod(location, y_dim) - 1
        return row, col

    def eval_at(self, t):
        if t > 0:
            t_pull = int(np.floor((t*self.update_rate)))
            face_colors = self.xyt_stimulus[:,:,np.min((t_pull, self.t_dim-1))].copy()

            # write to GPU
            self.texture.write(face_colors.astype('f4'))
            self.texture.use()
