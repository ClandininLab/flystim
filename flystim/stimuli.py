import numpy as np
import os
import array
from flystim.base import BaseProgram
from flystim.trajectory import Trajectory
import flystim.distribution as distribution
from flystim import GlSphericalRect, GlCylinder, GlCube, GlQuad, GlSphericalCirc, GlVertices, GlSphericalPoints
import time # for debugging and benchmarking
import copy

class ConstantBackground(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], center=[0,0,0], side_length=100):
        """
        Big skybox to simulate a constant background behind stimuli
        :param color: [r,g,b,a]
        :param center: [x,y,z]
        :param side_length: meters, side length of cube
        """

        self.color = color
        self.center = center
        self.side_length = side_length

        colors = {'+x': self.color, '-x': self.color,
                  '+y': self.color, '-y': self.color,
                  '+z': self.color, '-z': self.color}
        self.stim_object = GlCube(colors, center=self.center, side_length=self.side_length)

    def eval_at(self, t, fly_position=[0, 0, 0]):
        pass


class Floor(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], z_level=-0.1, side_length=5):
        """
        Infinite floor
        :param color: [r,g,b,a]
        :param z_level: meters, level at which the floor is on the z axis (-z is below the fly)
        :param side_length: meters
        """

        self.color = color

        v1 = (-side_length, -side_length, z_level)
        v2 = (side_length, -side_length, z_level)
        v3 = (side_length, side_length, z_level)
        v4 = (-side_length, side_length, z_level)
        color = self.color
        self.stim_object = GlQuad(v1, v2, v3, v4, color)

    def eval_at(self, t, fly_position=[0, 0, 0]):
        pass


class MovingSpot(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, radius=10, sphere_radius=1, color=[1, 1, 1, 1], theta=0, phi=0):
        """
        Stimulus consisting of a circular patch on the surface of a sphere. Patch is circular in spherical coordinates.

        :param radius: radius of circle in degrees
        :param sphere_radius: Radius of the sphere (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.radius = radius
        self.sphere_radius = sphere_radius
        self.color = color
        self.theta = theta
        self.phi = phi

    def eval_at(self, t, fly_position=[0, 0, 0]):
        radius = return_for_time_t(self.radius, t)
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        color = return_for_time_t(self.color, t)
        # TODO: is there a way to make this object once in configure then update with radius in eval_at?
        self.stim_object = GlSphericalCirc(circle_radius=radius,
                                           sphere_radius=self.sphere_radius,
                                           color=color,
                                           n_steps=36).rotate(np.radians(theta), np.radians(phi), 0 )



class MovingPatch(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=10, height=10, sphere_radius=1, color=[1, 1, 1, 1], theta=0, phi=0, angle=0):
        """
        Stimulus consisting of a rectangular patch on the surface of a sphere. Patch is rectangular in spherical coordinates.

        :param width: Width in degrees (azimuth)
        :param height: Height in degrees (elevation)
        :param sphere_radius: Radius of the sphere (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        :param angle: degrees orientation of patch (roll rotation around x axis)
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.width = width
        self.height = height
        self.sphere_radius = sphere_radius
        self.color = color
        self.theta = theta
        self.phi = phi
        self.angle = angle

    def eval_at(self, t, fly_position=[0, 0, 0]):
        width = return_for_time_t(self.width, t)
        height = return_for_time_t(self.height, t)
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)
        color = return_for_time_t(self.color, t)
        # TODO: is there a way to make this object once in configure then update with width/height in eval_at?
        self.stim_object = GlSphericalRect(width=width,
                                           height=height,
                                           sphere_radius=self.sphere_radius,
                                           color=color).rotate(np.radians(theta), np.radians(phi), np.radians(angle))


class TexturedCylinder(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, color=[1, 1, 1, 1], cylinder_radius=1, cylinder_height=10, theta=0, phi=0, angle=0.0):
        """
        Parent class for a Cylinder with a texture painted on it. Designed for stimuli where the fly is
        at (0, 0, 0)

        :param color: [r,g,b,a] color of cylinder. Applied to entire texture, which is monochrome.
        :param cylinder_radius: meters
        :param cylinder_height: meters
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        :param angle: degrees orientation of patch (roll rotation around x axis)
        """
        self.color = color
        self.cylinder_radius = cylinder_radius
        self.cylinder_height = cylinder_height
        self.theta = theta
        self.phi = phi
        self.angle = angle

    def updateTexture(self):
        # overwrite in subclass
        pass

    def eval_at(self, t, fly_position=[0, 0, 0]):
        # overwrite in subclass
        pass


class CylindricalGrating(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, period=20, mean=0.5, contrast=1.0, offset=0.0, profile='sine',
                  color=[1, 1, 1, 1], cylinder_radius=1, cylinder_height=10, theta=0, phi=0, angle=0.0):
        """
        Grating texture painted on a cylinder

        :param period: spatial period, degrees
        :param mean: mean intensity of grating texture
        :param contrast: Weber contrast of grating texture
        :param offset: phase offset of grating texture, degrees
        :param profile: 'sine' or 'square'; spatial profile of grating texture

        :params color, cylinder_radius, cylinder_height, theta, phi, angle: see parent class
        *Any of these params except cylinder_radius, cylinder_height and profile can be passed as a trajectory dict to vary as a function of time
        """
        super().configure(color=color, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height, theta=theta, phi=phi, angle=angle)

        self.period = period
        self.mean = mean
        self.contrast = contrast
        self.offset = offset
        self.profile = profile
        self.period = period

        # Only renders part of the cylinder if the period is not a divisor of 360
        n_cycles = np.floor(360/self.period)
        self.cylinder_angular_extent = n_cycles * self.period

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=[1, 1, 1, 1],
                                      texture=True).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))

        if np.any([type(x) == dict for x in [mean, contrast, offset]]):
            pass
        else:
            self.updateTexture(self.mean, self.contrast, self.offset)

    def updateTexture(self, mean, contrast, offset):
        # make the texture image
        sf = 1/np.radians(self.period)  # spatial frequency
        xx = np.linspace(0, np.radians(self.cylinder_angular_extent), 512)

        if self.profile == 'sine':
            self.texture_interpolation = 'LML'
            yy = np.sin(np.radians(offset) + sf*2*np.pi*xx)  # [-1, 1]
        elif self.profile == 'square':
            self.texture_interpolation = 'NEAREST'
            yy = np.sin(np.radians(offset) + sf*2*np.pi*xx)
            yy[yy >= 0] = 1
            yy[yy < 0] = -1

        yy = 255*(mean + contrast*mean*yy)  # shift/scale from [-1,1] to mean and contrast and scale to [0,255] for uint8
        img = np.expand_dims(yy, axis=0).astype(np.uint8)  # pass as x by 1, gets stretched out by shader
        self.texture_image = img

    def eval_at(self, t, fly_position=[0, 0, 0]):
        need_to_update_texture = False
        if type(self.mean) is dict:
            mean = Trajectory.from_dict(self.mean).eval_at(t)
            need_to_update_texture = True
        else:
            mean = self.mean

        if type(self.contrast) is dict:
            contrast = Trajectory.from_dict(self.contrast).eval_at(t)
            need_to_update_texture = True
        else:
            contrast = self.contrast

        if type(self.offset) is dict:
            offset = Trajectory.from_dict(self.offset).eval_at(t)
            need_to_update_texture = True
        else:
            offset = self.offset

        if need_to_update_texture:
            self.updateTexture(mean, contrast, offset)

class RotatingGrating(CylindricalGrating):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, rate=10, period=20, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                  color=[1, 1, 1, 1], cylinder_radius=1, cylinder_height=10, theta=0, phi=0, angle=0):
        """
        Subclass of CylindricalGrating that rotates the grating along the varying axis of the grating
        Note that the rotation effect is achieved by translating the texture on a semi-cylinder. This
        allows for arbitrary spatial periods to be achieved with no discontinuities in the grating

        :param rate: rotation rate, degrees/sec
        :other params: see CylindricalGrating, TexturedCylinder
        """
        super().configure(period=period, mean=mean, contrast=contrast, offset=offset, profile=profile,
                          color=color, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height, theta=theta, phi=phi, angle=angle)
        self.rate = rate
        self.updateTexture(mean=mean, contrast=contrast, offset=offset)

        self.stim_object_template = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True)

    def eval_at(self, t, fly_position=[0, 0, 0]):
        shift_u = t*self.rate/self.cylinder_angular_extent
        self.stim_object = copy.copy(self.stim_object_template).shiftTexture((shift_u, 0)).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))


class RandomBars(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, period=20, width=5, vert_extent=80, theta_offset=0, background=0.5,
                  distribution_data=None, update_rate=60.0, start_seed=0,
                  color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.0, cylinder_location=(0, 0, 0)):
        """
        Periodic bars of randomized intensity painted on the inside of a cylinder
        :param period: spatial period (degrees) of bar locations
        :param width: width (degrees) of each bar
        :param vert_extent: vertical extent (degrees) of bars
        :param theta_offset: offset of periodic bar pattern (degrees)
        :param background: intensity (mono) of texture background, where no bars appear
        :param distribution_data: dict. containing name and args/kwargs for random distribution (see flystim.distribution)
        :param update_rate: Hz, update rate of bar intensity
        :param start_seed: seed with which to start rng at the beginning of the stimulus presentation

        :other params: see TexturedCylinder
        """
        # assuming fly is at (0,0,0), calculate cylinder height required to achieve vert_extent (degrees)
        # tan(vert_extent/2) = (cylinder_height/2) / cylinder_radius
        assert vert_extent < 180
        cylinder_height = 2 * cylinder_radius * np.tan(np.radians(vert_extent/2))
        super().configure(color=color, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height, theta=theta, phi=phi, angle=angle)

        # get the noise distribution
        if distribution_data is None:
            distribution_data = {'name': 'Uniform',
                                 'args': [0, 1],
                                 'kwargs': {}}
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args',[]), **distribution_data.get('kwargs',{}))

        self.period = period
        self.width = width
        self.vert_extent = vert_extent
        self.theta_offset = theta_offset
        self.background = background
        self.update_rate = update_rate
        self.start_seed = start_seed
        self.cylinder_location = cylinder_location

        # Only renders part of the cylinder if the period is not a divisor of 360
        self.n_bars = int(np.floor(360/self.period))
        self.cylinder_angular_extent = self.n_bars * self.period  # degrees

        self.stim_object_template = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      cylinder_location=self.cylinder_location,
                                      texture=True)

    def eval_at(self, t, fly_position=[0, 0, 0]):
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)

        self.stim_object = copy.copy(self.stim_object_template).rotate(np.radians(theta), np.radians(phi), np.radians(angle))

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



class RandomGrid(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.cylindrical_height_correction = False

    def configure(self, patch_width=10, patch_height=10, cylinder_vertical_extent=160, cylinder_angular_extent=360,
                  distribution_data=None, update_rate=60.0, start_seed=0,
                  color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.0):
        """
        Random square grid pattern painted on the inside of a cylinder

        :param patch width: Azimuth extent (degrees) of each patch
        :param patch height: Elevation extent (degrees) of each patch
        :param cylinder_vertical_extent: Elevation extent of the entire cylinder (degrees)
        :param cylinder_angular_extent: Azimuth extent of the cylinder texture (degrees)
        :param distribution_data: dict. containing name and args/kwargs for random distribution (see flystim.distribution)
        :param update_rate: Hz, update rate of bar intensity
        :param start_seed: seed with which to start rng at the beginning of the stimulus presentation

        :other params: see TexturedCylinder
        """

        # Only renders part of the cylinder if the period is not a divisor of cylinder_angular_extent
        self.n_patches_width = int(np.floor(cylinder_angular_extent/patch_width))
        self.cylinder_angular_extent = self.n_patches_width * patch_width

        # assuming fly is at (0,0,0), calculate cylinder height required to achieve (approx.) vert_extent (degrees)
        # actual vert. extent is based on floor-nearest integer number of patch heights
        assert cylinder_vertical_extent < 180
        self.n_patches_height = int(np.floor(cylinder_vertical_extent/patch_height))
        patch_height_m = cylinder_radius * np.tan(np.radians(patch_height))  # in meters
        cylinder_height = self.n_patches_height * patch_height_m

        super().configure(color=color, angle=angle, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height, theta=theta, phi=phi)

        # get the noise distribution
        if distribution_data is None:
            distribution_data = {'name': 'Uniform',
                                 'args': [0, 1],
                                 'kwargs': {}}
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args', []), **distribution_data.get('kwargs',{}))

        self.patch_width = patch_width
        self.patch_height = patch_height
        self.start_seed = start_seed
        self.update_rate = update_rate

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))

    def eval_at(self, t, fly_position=[0, 0, 0]):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)
        # get the random values
        face_colors = 255*self.noise_distribution.get_random_values((self.n_patches_height, self.n_patches_width))
        # make the texture
        img = np.reshape(face_colors, (self.n_patches_height, self.n_patches_width)).astype(np.uint8)
        self.texture_interpolation = 'NEAREST'
        self.texture_image = img


class Checkerboard(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.cylindrical_height_correction = False

    def configure(self, patch_width=4, patch_height=4, cylinder_vertical_extent=160, cylinder_angular_extent=360,
                  color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.0):
        """
        Periodic checkerboard pattern painted on the inside of a cylinder

        :param patch width: Azimuth extent (degrees) of each patch
        :param patch height: Elevation extent (degrees) of each patch
        :param cylinder_vertical_extent: Elevation extent of the entire cylinder (degrees)
        :param cylinder_angular_extent: Azimuth extent of the cylinder texture (degrees)

        :other params: see TexturedCylinder
        """

        # Only renders part of the cylinder if the period is not a divisor of cylinder_angular_extent
        self.n_patches_width = int(np.floor(cylinder_angular_extent/patch_width))
        self.cylinder_angular_extent = self.n_patches_width * patch_width

        # assuming fly is at (0,0,0), calculate cylinder height required to achieve (approx.) vert_extent (degrees)
        # actual vert. extent is based on floor-nearest integer number of patch heights
        assert cylinder_vertical_extent < 180
        self.n_patches_height = int(np.floor(cylinder_vertical_extent/patch_height))
        patch_height_m = cylinder_radius * np.tan(np.radians(patch_height))  # in meters
        cylinder_height = self.n_patches_height * patch_height_m


        super().configure(color=color, angle=angle, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height)

        self.patch_width = patch_width
        self.patch_height = patch_height

        # Only renders part of the cylinder if the period is not a divisor of 360
        self.n_patches_width = int(np.floor(360/self.patch_width))
        self.cylinder_angular_extent = self.n_patches_width * self.patch_width
        self.patch_height_m = self.cylinder_radius * np.tan(np.radians(self.patch_height))  # in meters
        self.n_patches_height = int(np.floor(self.cylinder_height/self.patch_height_m))

        # create the texture
        face_colors = np.zeros((self.n_patches_height, self.n_patches_width))
        face_colors[0::2, 0::2] = 1
        face_colors[1::2, 1::2] = 1

        # make and apply the texture
        img = (255*face_colors).astype(np.uint8)
        self.texture_interpolation = 'NEAREST'
        self.texture_image = img

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))

    def eval_at(self, t, fly_position=[0, 0, 0]):
        pass


class Tower(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[1, 0, 0, 1], cylinder_radius=0.5, cylinder_height=0.5, cylinder_location=[+5, 0, 0], n_faces=16):
        """
        Cylindrical tower object in arbitrary x, y, z coords
        :param color: [r,g,b,a] color of cylinder. Applied to entire texture, which is monochrome
        :param cylinder_radius: meters
        :param cylinder_height: meters
        :param cylinder_location: [x, y, z] location of the center of the cylinder, meters
        :param n_faces: number of quad faces to make the cylinder out of

        """
        self.color = color
        self.cylinder_radius = cylinder_radius
        self.cylinder_height = cylinder_height
        self.cylinder_location = cylinder_location
        self.n_faces = n_faces

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_location=self.cylinder_location,
                                      color=self.color,
                                      n_faces=self.n_faces)

    def eval_at(self, t, fly_position=[0, 0, 0]):
        pass

class TexturedGround(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], z_level=-0.1, side_length=5, rand_seed=0):
        """
        Infinite textured ground
        :param color: [r,g,b,a]
        :param z_level: meters, level at which the floor is on the z axis (-z is below the fly)
        :param side_length: meters
        """

        self.color = color
        self.rand_seed = rand_seed

        v1 = (-side_length, -side_length, z_level)
        v2 = (side_length, -side_length, z_level)
        v3 = (side_length, side_length, z_level)
        v4 = (-side_length, side_length, z_level)

        self.stim_object = GlQuad(v1, v2, v3, v4,  self.color,
                                  tc1=(0, 0), tc2=(1, 0), tc3=(1, 1), tc4=(0, 1),
                                  texture_shift=(0, 0), use_texture=True)

        # create the texture
        np.random.seed(self.rand_seed)
        face_colors = np.random.uniform(size=(128,128))

        # make and apply the texture
        img = (255*face_colors).astype(np.uint8)
        self.texture_interpolation = 'LINEAR'
        self.texture_image = img

    def eval_at(self, t, fly_position=[0, 0, 0]):
        pass


class HorizonCylinder(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[1, 1, 1, 1], cylinder_radius=5, cylinder_height=5, image_path=None):
        super().configure(color=color, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height, theta=0, phi=0, angle=0.0)

        if image_path is None:
            load_image = False
        elif os.path.isfile(image_path):
            load_image = True
        else:
            load_image = False

        if load_image:
            with open(image_path, 'rb') as handle:
               s = handle.read()
            arr = array.array('H', s)
            arr.byteswap()
            img = np.array(arr, dtype='uint16').reshape(1024, 1536)
            img = np.uint8(255*(img / np.max(img)))
            img = img[:,:1024]

        else:
            # use a dummy texture
            np.random.seed(0)
            face_colors = np.random.uniform(size=(128,128))
            img = (255*face_colors).astype(np.uint8)

        self.texture_interpolation = 'LINEAR'
        self.texture_image = img

        self.stim_template = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_location=(0, 0, 0),
                                      color=self.color,
                                      texture=True).rotz(np.radians(180))

    def eval_at(self, t, fly_position=[0, 0, 0]):
        cyl_position = fly_position.copy()
        self.stim_object = copy.copy(self.stim_template).translate(cyl_position)

class Forest(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=1000)

    def configure(self, color=[1, 1, 1, 1], cylinder_radius=0.5, cylinder_height=0.5, n_faces=16, cylinder_locations=[[+5, 0, 0]]):
        """
        Collection of tower objects created with a single shader program
        """
        self.color = color
        self.cylinder_radius = cylinder_radius
        self.cylinder_height = cylinder_height
        self.cylinder_locations = cylinder_locations
        self.n_faces = n_faces

        self.stim_object = GlVertices()

        # This step is slow. Make template once then use .translate() on copies to make cylinders
        cylinder = GlCylinder(cylinder_height=self.cylinder_height,
                                        cylinder_radius=self.cylinder_radius,
                                        cylinder_location=[0,0,0],
                                        color=self.color,
                                        n_faces=self.n_faces)

        for tree_loc in self.cylinder_locations:
            new_cyl = copy.copy(cylinder).translate(tree_loc)
            self.stim_object.add(new_cyl)

    def eval_at(self, t, fly_position=[0, 0, 0]):
        pass


class CoherentMotionDotField(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=10000)
        self.draw_mode = 'POINTS'

    def configure(self, point_size=20, sphere_radius=1, color=[1, 1, 1, 1], theta_locations=[0], phi_locations=[0], theta_trajectory=0, phi_trajectory=0):
        """
        Collection of moving points created with a single shader
        Each point can have a distinct offset (center), and all move with a single coherent motion trajectory along a sphere
        Note that points are all the same size, so no area correction is made for perspective
        """
        self.point_size = point_size
        self.sphere_radius = sphere_radius
        self.color = color
        self.theta_locations = theta_locations
        self.phi_locations = phi_locations
        self.theta_trajectory = theta_trajectory
        self.phi_trajectory = phi_trajectory

        self.stim_object_template = GlSphericalPoints(sphere_radius=self.sphere_radius,
                                             color=self.color,
                                             theta=self.theta_locations,
                                             phi=self.phi_locations)

    def eval_at(self, t, fly_position=[0, 0, 0]):
        if type(self.theta_trajectory) is dict:
            theta = Trajectory.from_dict(self.theta_trajectory).eval_at(t)
        else:
            theta = self.theta_trajectory
        if type(self.phi_trajectory) is dict:
            phi = Trajectory.from_dict(self.phi_trajectory).eval_at(t)
        else:
            phi = self.phi_trajectory

        self.stim_object = copy.copy(self.stim_object_template).rotate(np.radians(theta), np.radians(phi), 0)



def return_for_time_t(parameter, t):
    if type(parameter) is dict:
        return Trajectory.from_dict(parameter).eval_at(t)
    else:
        return parameter
