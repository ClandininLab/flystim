import numpy as np

from flystim.base import BaseProgram
from flystim.trajectory import Trajectory
import flystim.distribution as distribution
from flystim import GlSphericalRect, GlCylinder, GlCube, GlQuad, GlSphericalCirc


class ConstantBackground(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], center=[0,0,0], side_length=100):
        """
        :param color: [r,g,b,a]
        """

        self.color = color
        self.center = center
        self.side_length = side_length

        colors = {'+x': self.color, '-x': self.color,
                  '+y': self.color, '-y': self.color,
                  '+z': self.color, '-z': self.color}
        self.stim_object = GlCube(colors, center=self.center, side_length=self.side_length)

    def eval_at(self, t):
        pass


class Floor(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], z_level=0):
        """
        :param color: [r,g,b,a]
        """

        self.color = color

        v1 = (-1000, -1000, z_level)
        v2 = (1000, -1000, z_level)
        v3 = (1000, 1000, z_level)
        v4 = (-1000, 1000, z_level)
        color = self.color
        self.stim_object = GlQuad(v1, v2, v3, v4, color)

    def eval_at(self, t):
        pass


class MovingSpot(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, radius=10, sphere_radius=1, color=[1, 1, 1, 1], theta=-180, phi=0):
        """
        Stimulus consisting of a circular patch on the surface of a sphere

        :param radius: radius of circle in degrees
        :param sphere_radius: Radius of the sphere (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch
        :param phi: degrees, elevation of the center of the patch
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.radius = radius
        self.sphere_radius = sphere_radius
        self.color = color
        self.theta = theta
        self.phi = phi

    def eval_at(self, t):
        if type(self.radius) is dict:
            self.radius = Trajectory.from_dict(self.radius).eval_at(t)
        if type(self.color) is dict:
            self.color = Trajectory.from_dict(self.color).eval_at(t)
        if type(self.theta) is dict:
            self.theta = Trajectory.from_dict(self.theta).eval_at(t)
        if type(self.phi) is dict:
            self.phi = Trajectory.from_dict(self.phi).eval_at(t)

        self.stim_object = GlSphericalCirc(circle_radius=self.radius,
                                           sphere_radius=self.sphere_radius,
                                           color=self.color,
                                           n_steps=36).rotz(np.radians(self.theta)).roty(np.radians(self.phi))


class MovingPatch(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=10, height=10, sphere_radius=1, color=[1, 1, 1, 1], theta=-180, phi=0, angle=0):
        """
        Stimulus consisting of a rectangular patch on the surface of a sphere

        :param width: Width in degrees (azimuth)
        :param height: Height in degrees (elevation)
        :param sphere_radius: Radius of the sphere (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch
        :param phi: degrees, elevation of the center of the patch
        :param angle: degrees, roll. Or orientation of patch in spherical coordinates
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.width = width
        self.height = height
        self.sphere_radius = sphere_radius
        self.color = color
        self.theta = theta
        self.phi = phi
        self.angle = angle

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
        if type(self.angle) is dict:
            self.angle = Trajectory.from_dict(self.angle).eval_at(t)

        self.stim_object = GlSphericalRect(width=self.width,
                                           height=self.height,
                                           sphere_radius=self.sphere_radius,
                                           color=self.color).rotx(np.radians(-self.angle)).rotz(np.radians(self.theta)).roty(np.radians(self.phi))


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
        self.cylinder_height = cylinder_height
        self.profile = profile

    def updateTexture(self):
        # Only renders part of the cylinder if the period is not a divisor of 360
        n_cycles = np.floor(360/self.period)
        self.cylinder_angular_extent = n_cycles * self.period

        # make the texture image
        sf = 1/np.radians(self.period)  # spatial frequency
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
                                      texture=True).rotx(np.radians(self.angle))


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
                                      texture_shift=(shift_u, 0)).rotx(np.radians(self.angle))


class TexturedCylinder(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, color=[1, 1, 1, 1], angle=0.0, cylinder_radius=1, cylinder_height=10):
        """
        Parent class for a Cylinder with a texture painted on it

        :param color: [r,g,b,a] color of cylinder. Applied to entire texture, which is monochrome.
        :param angle: roll angle of cylinder
        :param cylinder_radius: meters
        :param cylinder_height: meters
        """
        self.color = color
        self.angle = angle
        self.cylinder_radius = cylinder_radius
        self.cylinder_height = cylinder_height

    def updateTexture(self):
        pass

    def eval_at(self, t):
        pass


class RandomBars(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, period=15, vert_extent=30, width=10, start_seed=0, update_rate=60.0,
                  background=0.5, theta_offset=None, distribution_data=None,
                  color=[1, 1, 1, 1], angle=0.0, cylinder_radius=1):

        # assuming fly is at (0,0,0), calculate cylinder height required to achieve vert_extent (degrees)
        # tan(vert_extent/2) = (cylinder_height/2) / cylinder_radius
        assert vert_extent < 180
        cylinder_height = 2 * cylinder_radius * np.tan(np.radians(vert_extent/2))

        super().configure(color=color, angle=angle, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height)
        # get the noise distribution
        if distribution_data is None:
            distribution_data = {'name': 'Uniform',
                                 'args': [0, 1],
                                 'kwargs': {}}
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args',[]), **distribution_data.get('kwargs',{}))

        self.period = period
        self.vert_extent = vert_extent
        self.width = width
        self.start_seed = start_seed
        self.update_rate = update_rate
        self.background = background
        self.theta_offset = theta_offset

        # Only renders part of the cylinder if the period is not a divisor of 360
        self.n_bars = int(np.floor(360/self.period))
        self.cylinder_angular_extent = self.n_bars * self.period  # degrees

    def eval_at(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)
        # get the random values
        bar_colors = self.noise_distribution.get_random_values(self.n_bars)

        # get the x-profile
        xx = np.mod(np.linspace(0, self.cylinder_angular_extent, 256)[:-1] + self.theta_offset, 360)
        profile = np.array([bar_colors[int(x/self.period)] for x in xx])
        duty_cycle = self.width/self.period
        inds = np.modf(xx/self.period)[0] > duty_cycle
        profile[inds] = self.background

        # make the texture
        img = np.expand_dims(255*profile, axis=0).astype(np.uint8)  # pass as x by 1, gets stretched out by shader
        self.texture_interpolation = 'NEAREST'
        self.texture_image = img

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotx(np.radians(self.angle))


class RandomGrid(TexturedCylinder):
    # TODO: correct patch height for elevation on cylinder to make all patches the same solid angle
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, patch_width=10, patch_height=10, start_seed=0, update_rate=60.0,
                  distribution_data=None, color=[1, 1, 1, 1], angle=0.0, cylinder_radius=1, cylinder_height=10):
        super().configure(color=color, angle=angle, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height)
        # get the noise distribution
        if distribution_data is None:
            distribution_data = {'name': 'Uniform',
                                 'args': [0, 1],
                                 'kwargs': {}}
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args',[]), **distribution_data.get('kwargs',{}))

        self.patch_width = patch_width
        self.patch_height = patch_height
        self.start_seed = start_seed
        self.update_rate = update_rate

        # Only renders part of the cylinder if the period is not a divisor of 360
        self.n_patches_width = int(np.floor(360/self.patch_width))
        self.cylinder_angular_extent = self.n_patches_width * self.patch_width
        self.n_patches_height = int(np.floor(180/self.patch_height))

    def eval_at(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)
        # get the random values
        face_colors = 255*self.noise_distribution.get_random_values((self.n_patches_height, self.n_patches_width))
        # make the texture
        img = np.reshape(face_colors, (self.n_patches_height, self.n_patches_width)).astype(np.uint8)
        self.texture_interpolation = 'NEAREST'
        self.texture_image = img

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotx(np.radians(self.angle))


class Checkerboard(TexturedCylinder):
    # TODO adjust patch height for elevation on cylinder
    def configure(self, patch_width=2, patch_height=2, vert_extent = 120,
                  color=[1, 1, 1, 1], angle=0.0, cylinder_radius=1):

        # assuming fly is at (0,0,0), calculate cylinder height required to achieve vert_extent (degrees)
        # tan(vert_extent/2) = (cylinder_height/2) / cylinder_radius
        assert vert_extent < 180
        cylinder_height = 2 * cylinder_radius * np.tan(np.radians(vert_extent/2))

        super().configure(color=color, angle=angle, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height)
        """
        Patches surrounding the viewer are arranged in a periodic checkerboard.
        :param patch_width: Horizontal angular extent of the checkerboard patches (degrees)
        :param patch_height: Vertical angular extent of the checkerboard patches (degrees)
        """

        self.patch_width = patch_width
        self.patch_height = patch_height

        # Only renders part of the cylinder if the period is not a divisor of 360
        self.n_patches_width = int(np.floor(360/self.patch_width))
        self.cylinder_angular_extent = self.n_patches_width * self.patch_width
        self.n_patches_height = int(np.floor(180/self.patch_height))

        # create the texture
        face_colors = np.zeros((self.n_patches_height, self.n_patches_width))
        face_colors[0::2, 0::2] = 1
        face_colors[1::2, 1::2] = 1

        # make and apply the texture
        img = (255*face_colors).astype(np.uint8)
        self.texture_interpolation = 'NEAREST'
        self.texture_image = img

    def eval_at(self, t):
        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotx(np.radians(self.angle))


class Tower(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, cylinder_radius=1, cylinder_height=10, cylinder_location=[0,0,0], color=[1, 1, 1, 1]):
        """

        """
        self.cylinder_radius = cylinder_radius
        self.cylinder_height = cylinder_height
        self.cylinder_location = cylinder_location
        self.color = color

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_location=self.cylinder_location,
                                      color=self.color,
                                      n_faces=4)

    def eval_at(self, t):
        pass
