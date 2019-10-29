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


class MovingPatch(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=10, height=10, sphere_radius=1, color=[1, 1, 1, 1], theta=-180, phi=0):
        """
        Stimulus consisting of a rectangular patch on the surface of a sphere

        :param width: Width in degrees (azimuth)
        :param height: Height in degrees (elevation)
        :param sphere_radius: Radius of the sphere (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch
        :param phi: degrees, elevation of the center of the patch
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
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


class CylindricalGrating(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, period=20, color=[1, 1, 1, 1], mean=0.5, contrast=1.0, angle=0.0, offset=0.0, cylinder_radius=1, cylinder_height=10, profile='sine'):
        """
        Grating texture painted on a cylinder

        :param period: spatial period, degrees
        :param color: [r,g,b,a] color of cylinder. Applied to entire texture, which is monochrome.
        :param mean: mean intensity of grating
        :param contrast: contrast of grating (Weber)
        :param angle: roll angle of cylinder, determines direction of motion
        :param offset: phase offse, degrees
        :param cylinder_radius: meters
        :param cylinder_height: meters
        :param profile: 'sine' or 'square'; spatial profile of grating
        *Any of these params except cylinder_radius, cylinder_height and profile can be passed as a trajectory dict to vary as a function of time
        """
        self.period = period
        self.color = color
        self.mean = mean
        self.contrast = contrast
        self.angle = angle
        self.offset = offset
        self.cylinder_radius = cylinder_radius
        self.profile = profile

    def updateTexture(self):
        # Only renders part of the cylinder if the period is not a divisor of 360
        n_cycles = np.floor(360/self.period)
        self.cylinder_angular_extent = n_cycles * self.period

        # make the texture image
        sf = 1/radians(self.period)  # spatial frequency
        xx = np.linspace(0, np.radians(self.cylinder_angular_extent), 256)

        if self.profile == 'sine':
            self.texture_interpolation = 'LML'
            yy = np.sin(np.radians(self.offset) + sf*2*np.pi*xx)  # [-1, 1]
        elif self.profile == 'square':
            self.texture_interpolation = 'NEAREST'
            yy = np.sin(np.radians(self.offset) + sf*2*np.pi*xx)
            yy[yy >= 0] = 1
            yy[yy < 0] = -1

        yy = 255*(self.mean + self.contrast*self.mean*yy)  # shift/scale from [-1,1] to mean and contrast and scale to [0,255] for uint8
        img = np.expand_dims(yy, axis=0).astype(np.uint8)  # pass as x by 1, gets stretched out by shader
        self.texture_image = img

    def eval_at(self, t):
        need_to_update_texture = False
        if type(self.period) is dict:
            self.period = Trajectory.from_dict(self.period).eval_at(t)
            need_to_update_texture = True
        if type(self.mean) is dict:
            self.mean = Trajectory.from_dict(self.mean).eval_at(t)
            need_to_update_texture = True
        if type(self.contrast) is dict:
            self.contrast = Trajectory.from_dict(self.contrast).eval_at(t)
            need_to_update_texture = True
        if type(self.offset) is dict:
            self.offset = Trajectory.from_dict(self.offset).eval_at(t)
            need_to_update_texture = True

        if type(self.angle) is dict:
            self.angle = Trajectory.from_dict(self.angle).eval_at(t)
        if type(self.color) is dict:
            self.color = Trajectory.from_dict(self.color).eval_at(t)

        if need_to_update_texture:
            self.updateTexture()

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotx(radians(self.angle))


class RotatingGrating(CylindricalGrating):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, period=20, rate=10, color=[1, 1, 1, 1], mean=0.5, contrast=1.0, angle=0.0, offset=0.0, cylinder_radius=1, cylinder_height=10, profile='sine'):
        """
        Subclass of CylindricalGrating that rotates the grating along the varying axis of the grating
        Note that the rotation effect is achieved by translating the texture on a semi-cylinder. This
        allows for arbitrary spatial periods to be achieved with no discontinuities in the grating

        :param rate: rotation rate, degrees/sec
        """
        super().configure(period=period, color=color, mean=mean, contrast=contrast, angle=angle, offset=offset, cylinder_radius=cylinder_radius, profile=profile)
        self.rate = rate
        self.updateTexture()

    def eval_at(self, t):
        shift_u = t*self.rate/self.cylinder_angular_extent
        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True,
                                      texture_shift=(shift_u, 0)).rotx(radians(self.angle))


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
