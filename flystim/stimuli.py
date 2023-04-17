"""
Stimulus classes.

Each class is is derived from flystim.base.BaseProgram, which handles the GL context and shader programs

"""

import numpy as np
from numpy.random import default_rng
import os
import array
from flystim.base import BaseProgram
from flystim.trajectory import make_as_trajectory, return_for_time_t
import flystim.distribution as distribution
from flystim.shapes import GlSphericalRect, GlSphericalEllipse, GlCylindricalWithPhiRect, GlCylindricalWithPhiEllipse, GlCylinder, GlCube, GlQuad, GlSphericalCirc, GlVertices, GlSphericalPoints, GlSphericalTexturedRect, GlPointCollection, GlCylindricalPoints
from flystim import util, image
import time  # for debugging and benchmarking
import copy


class ConstantBackground(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], center=[0, 0, 0], side_length=100):
        """
        Big skybox to simulate a constant background behind stimuli.

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

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        pass


class Floor(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], z_level=-0.1, side_length=5):
        """
        Infinite floor.

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

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        pass

class MovingEllipse(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=20, height=10, sphere_radius=1, color=[1, 1, 1, 1], theta=0, phi=0, angle=0):
        """
        Stimulus consisting of a circular patch on the surface of a sphere. Patch is circular in spherical coordinates.

        :param width: width of ellipse in degrees
        :param height: height of ellipse in degrees
        :param sphere_radius: Radius of the sphere (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        :param angle: degrees orientation of patch (roll rotation around x axis)
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.sphere_radius = sphere_radius

        self.width = make_as_trajectory(width)
        self.height = make_as_trajectory(height)
        self.color = make_as_trajectory(color)
        self.theta = make_as_trajectory(theta)
        self.phi = make_as_trajectory(phi)
        self.angle = make_as_trajectory(angle)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        width = return_for_time_t(self.width, t)
        height = return_for_time_t(self.height, t)
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)
        color = return_for_time_t(self.color, t)
        # TODO: is there a way to make this object once in configure then update with radius in eval_at?
        self.stim_object = GlSphericalEllipse(width=width, 
                                              height=height,
                                              sphere_radius=self.sphere_radius,
                                              color=color,
                                              n_steps=36).rotate(np.radians(theta), np.radians(phi), np.radians(angle))

class MovingEllipseOnCylinder(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=20, height=10, cylinder_radius=1, color=[1, 1, 1, 1], theta=0, phi=0, angle=0):
        """
        Stimulus consisting of a circular patch on the surface of a sphere. Patch is circular in spherical coordinates.

        :param width: width of ellipse in degrees
        :param height: height of ellipse in degrees
        :param cylinder_radius: Radius of the cylinder (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        :param angle: degrees orientation of patch (roll rotation around x axis)
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.cylinder_radius = cylinder_radius

        self.width = make_as_trajectory(width)
        self.height = make_as_trajectory(height)
        self.color = make_as_trajectory(color)
        self.theta = make_as_trajectory(theta)
        self.phi = make_as_trajectory(phi)
        self.angle = make_as_trajectory(angle)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        width = return_for_time_t(self.width, t)
        height = return_for_time_t(self.height, t)
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)
        color = return_for_time_t(self.color, t)
        # TODO: is there a way to make this object once in configure then update with radius in eval_at?
        self.stim_object = GlCylindricalWithPhiEllipse(width=width, 
                                              height=height,
                                              cylinder_radius=self.cylinder_radius,
                                              color=color,
                                              n_steps=36).rotate(np.radians(theta), np.radians(phi), np.radians(angle))

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
        self.sphere_radius = sphere_radius

        self.radius = make_as_trajectory(radius)
        self.color = make_as_trajectory(color)
        self.theta = make_as_trajectory(theta)
        self.phi = make_as_trajectory(phi)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        radius = return_for_time_t(self.radius, t)
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        color = return_for_time_t(self.color, t)
        # TODO: is there a way to make this object once in configure then update with radius in eval_at?
        self.stim_object = GlSphericalCirc(circle_radius=radius,
                                           sphere_radius=self.sphere_radius,
                                           color=color,
                                           n_steps=36).rotate(np.radians(theta), np.radians(phi), 0)


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
        self.width = make_as_trajectory(width)
        self.height = make_as_trajectory(height)
        self.sphere_radius = sphere_radius
        self.color = make_as_trajectory(color)
        self.theta = make_as_trajectory(theta)
        self.phi = make_as_trajectory(phi)
        self.angle = make_as_trajectory(angle)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
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


class UniformWhiteNoise(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=10, height=10, sphere_radius=1, distribution_data=None,
                  theta=0, phi=0, angle=0, update_rate=60.0, start_seed=0):
        """
        Stimulus consisting of a rectangular patch on the surface of a sphere. Patch is rectangular in spherical coordinates.

        :param width: Width in degrees (azimuth)
        :param height: Height in degrees (elevation)
        :param sphere_radius: Radius of the sphere (meters)
        :param distribution_data: dict. containing name and args/kwargs for random distribution (see flystim.distribution)
        :param update_rate: Hz, update rate of bar intensity
        :param start_seed: seed with which to start rng at the beginning of the stimulus presentation
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        :param angle: degrees orientation of patch (roll rotation around x axis)
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.width = width
        self.height = height
        self.sphere_radius = sphere_radius
        self.theta = theta
        self.phi = phi
        self.angle = angle
        self.update_rate = update_rate
        self.start_seed = start_seed

        # get the noise distribution
        if distribution_data is None:
            distribution_data = {'name': 'Uniform',
                                 'args': [0, 1],
                                 'kwargs': {}}
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args', []), **distribution_data.get('kwargs', {}))

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)

        color = self.noise_distribution.get_random_values(1)
        color = [color, color, color, 1]
        # TODO: is there a way to make this object once in configure then update with width/height in eval_at?
        self.stim_object = GlSphericalRect(width=self.width,
                                           height=self.height,
                                           sphere_radius=self.sphere_radius,
                                           color=color).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))

class MovingPatchOnCylinder(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, width=10, height=10, cylinder_radius=1, color=[1, 1, 1, 1], theta=0, phi=0, angle=0):
        """
        Stimulus consisting of a rectangular patch on the surface of a cylinder. Patch is rectangular in cylindrical coordinates.

        :param width: Width in degrees (azimuth)
        :param height: Height in degrees (elevation)
        :param cylinder_radius: Radius of the cylinder (meters)
        :param color: [r,g,b,a] or mono. Color of the patch
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        :param angle: degrees orientation of patch (roll rotation around x axis)
        *Any of these params can be passed as a trajectory dict to vary these as a function of time elapsed
        """
        self.width = make_as_trajectory(width)
        self.height = make_as_trajectory(height)
        self.cylinder_radius = cylinder_radius
        self.color = make_as_trajectory(color)
        self.theta = make_as_trajectory(theta)
        self.phi = make_as_trajectory(phi)
        self.angle = make_as_trajectory(angle)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        width = return_for_time_t(self.width, t)
        height = return_for_time_t(self.height, t)
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)
        color = return_for_time_t(self.color, t)
        # TODO: is there a way to make this object once in configure then update with width/height in eval_at?
        self.stim_object = GlCylindricalWithPhiRect(width=width,
                                           height=height,
                                           cylinder_radius=self.cylinder_radius,
                                           color=color).rotate(np.radians(theta), np.radians(phi), np.radians(angle))


class TexturedSphericalPatch(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, width=10, height=10, sphere_radius=1, color=[1, 1, 1, 1], theta=0, phi=0, angle=0, n_steps_x=12, n_steps_y=12):
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

        self.stim_object = GlSphericalTexturedRect(width=self.width,
                                                   height=self.height,
                                                   sphere_radius=self.sphere_radius,
                                                   color=self.color, n_steps_x=n_steps_x, n_steps_y=n_steps_y, texture=True).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))

    def updateTexture(self):
        # overwrite in subclass
        pass

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        # overwrite in subclass
        pass


class RandomGridOnSphericalPatch(TexturedSphericalPatch):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, patch_width=5, patch_height=5, distribution_data=None, update_rate=60.0, start_seed=0,
                  width=30, height=30, sphere_radius=1, color=[1, 1, 1, 1], theta=0, phi=0, angle=0, rgb_texture=False, n_steps_x=12, n_steps_y=12):
        """
        Random square grid pattern painted on a spherical patch.

        :param patch width: Azimuth extent (degrees) of each patch
        :param patch height: Elevation extent (degrees) of each patch
        :param distribution_data: dict. containing name and args/kwargs for random distribution (see flystim.distribution)
        :param update_rate: Hz, update rate of bar intensity
        :param start_seed: seed with which to start rng at the beginning of the stimulus presentation

        :other params: see TexturedSphericalPatch
        """
        self.rgb_texture = rgb_texture

        super().configure(width=width, height=height, sphere_radius=sphere_radius, color=color, theta=theta, phi=phi, angle=angle, n_steps_x=n_steps_x, n_steps_y=n_steps_y)

        # get the noise distribution
        if distribution_data is None:
            distribution_data = {'name': 'Uniform',
                                 'args': [0, 1],
                                 'kwargs': {}}
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args', []), **distribution_data.get('kwargs', {}))

        self.patch_width = patch_width
        self.patch_height = patch_height
        self.start_seed = start_seed
        self.update_rate = update_rate

        self.n_patches_width = int(np.floor(width/self.patch_width))
        self.n_patches_height = int(np.floor(height/self.patch_height))

        if self.rgb_texture:
            img = np.zeros((self.n_patches_height, self.n_patches_width, 3)).astype(np.uint8)
        else:
            img = np.zeros((self.n_patches_height, self.n_patches_width)).astype(np.uint8)
        self.add_texture_gl(img, texture_interpolation='NEAREST')

    def updateTexture(self, t):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)

        # get the random values
        if self.rgb_texture:  # shape = (x, y, 3)
            face_colors = 255*self.noise_distribution.get_random_values((self.n_patches_height, self.n_patches_width, 3))
            img = np.reshape(face_colors, (self.n_patches_height, self.n_patches_width, 3)).astype(np.uint8)
        else:  # shape = (x, y) monochromatic
            face_colors = 255*self.noise_distribution.get_random_values((self.n_patches_height, self.n_patches_width))
            img = np.reshape(face_colors, (self.n_patches_height, self.n_patches_width)).astype(np.uint8)

        # TEST CHECKERBOARD
        # x = np.zeros((self.n_patches_height, self.n_patches_width), dtype=int)
        # x[1::2, ::2] = 255
        # x[::2, 1::2] = 255
        # img = x.astype(np.uint8)

        self.update_texture_gl(img)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        self.updateTexture(t)


class TexturedCylinder(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, color=[1, 1, 1, 1], cylinder_radius=1, cylinder_location=(0,0,0), cylinder_height=10, theta=0, phi=0, angle=0.0):
        """
        Parent class for a Cylinder with a texture painted on it. Fly is at (0, 0, 0).

        :param color: [r,g,b,a] color of cylinder. Applied to entire texture, which is monochrome.
        :param cylinder_radius: meters
        :param cylinder_height: meters
        :param theta: degrees, azimuth of the center of the patch (yaw rotation around z axis)
        :param phi: degrees, elevation of the center of the patch (pitch rotation around y axis)
        :param angle: degrees orientation of patch (roll rotation around x axis)
        """
        self.color = color
        self.cylinder_radius = cylinder_radius
        self.cylinder_location = cylinder_location
        self.cylinder_height = cylinder_height
        self.theta = make_as_trajectory(theta)
        self.phi = make_as_trajectory(phi)
        self.angle = make_as_trajectory(angle)

    def updateTexture(self):
        # overwrite in subclass
        pass

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        # overwrite in subclass
        pass


class CylindricalGrating(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, period=20, mean=0.5, contrast=1.0, offset=0.0, profile='sine',
                  color=[1, 1, 1, 1], cylinder_radius=1, cylinder_location=(0,0,0), cylinder_height=10, theta=0, phi=0, angle=0.0):
        """
        Grating texture painted on a cylinder.

        :param period: spatial period, degrees
        :param mean: mean intensity of grating texture
        :param contrast: Weber contrast of grating texture
        :param offset: phase offset of grating texture, degrees
        :param profile: 'sine' or 'square'; spatial profile of grating texture

        :params color, cylinder_radius, cylinder_height, theta, phi, angle: see parent class
        *Any of these params except cylinder_radius, cylinder_height and profile can be passed as a trajectory dict to vary as a function of time
        """
        super().configure(color=color, cylinder_radius=cylinder_radius, cylinder_location=cylinder_location, cylinder_height=cylinder_height, theta=theta, phi=phi, angle=angle)

        self.period = period
        self.mean = mean
        self.contrast = contrast
        self.offset = offset
        self.profile = profile
        self.period = period

        # Only renders part of the cylinder if the period is not a divisor of 360
        n_cycles = np.floor(360/self.period)
        self.cylinder_angular_extent = n_cycles * self.period

        t = 0
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=[1, 1, 1, 1],
                                      texture=True).rotate(np.radians(theta), np.radians(phi), np.radians(angle))

        self.mean = make_as_trajectory(mean)
        self.contrast = make_as_trajectory(contrast)
        self.offset = make_as_trajectory(offset)

        img = np.zeros((1, 512)).astype(np.uint8)
        if self.profile == 'sine':
            self.add_texture_gl(img, texture_interpolation='LINEAR')
        elif self.profile == 'square':
            self.add_texture_gl(img, texture_interpolation='NEAREST')

        self.updateTexture(return_for_time_t(self.mean, 0), return_for_time_t(self.contrast, 0), return_for_time_t(self.offset, 0))

    def updateTexture(self, mean, contrast, offset):
        # make the texture image
        sf = 1/np.radians(self.period)  # spatial frequency
        xx = np.linspace(0, np.radians(self.cylinder_angular_extent), 512)

        if self.profile == 'sine':
            yy = np.sin(np.radians(offset) + sf*2*np.pi*xx)  # [-1, 1]
        elif self.profile == 'square':
            yy = np.sin(np.radians(offset) + sf*2*np.pi*xx)
            yy[yy >= 0] = 1
            yy[yy < 0] = -1

        yy = 255*(mean + contrast*mean*yy)  # shift/scale from [-1,1] to mean and contrast and scale to [0,255] for uint8
        img = np.expand_dims(yy, axis=0).astype(np.uint8)  # pass as x by 1, gets stretched out by shader
        self.update_texture_gl(img)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        mean = return_for_time_t(self.mean, t)
        contrast = return_for_time_t(self.contrast, t)
        offset = return_for_time_t(self.offset, t)

        self.updateTexture(mean, contrast, offset)


class RotatingGrating(CylindricalGrating):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, rate=10, hold_duration=0, period=20, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                  color=[1, 1, 1, 1], alpha_by_face=None, cylinder_radius=1, cylinder_location=(0,0,0), cylinder_height=10, theta=0, phi=0, angle=0):
        """
        Subclass of CylindricalGrating that rotates the grating along the varying axis of the grating.

        Note that the rotation effect is achieved by translating the texture on a semi-cylinder. This
        allows for arbitrary spatial periods to be achieved with no discontinuities in the grating

        :param rate: rotation rate, degrees/sec
        :param hold_duration: duration for which the initial image is held (seconds)
        :other params: see CylindricalGrating, TexturedCylinder
        """
        super().configure(period=period, mean=mean, contrast=contrast, offset=offset, profile=profile,
                          color=color, cylinder_radius=cylinder_radius, cylinder_location=cylinder_location, cylinder_height=cylinder_height, theta=theta, phi=phi, angle=angle)
        self.rate = make_as_trajectory(rate)
        self.hold_duration = hold_duration
        self.alpha_by_face = alpha_by_face
        if self.alpha_by_face is None:
            self.n_faces = 32
        else:
            self.n_faces = len(self.alpha_by_face)
        self.updateTexture(mean=mean, contrast=contrast, offset=offset)

        self.stim_object_template = GlCylinder(cylinder_height=self.cylinder_height,
                                               cylinder_radius=self.cylinder_radius,
                                               cylinder_location=self.cylinder_location,
                                               cylinder_angular_extent=self.cylinder_angular_extent,
                                               color=self.color,
                                               alpha_by_face=self.alpha_by_face,
                                               n_faces=self.n_faces,
                                               texture=True)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)
        rate = return_for_time_t(self.rate, t)

        shift_u = max(t - self.hold_duration, 0) * rate/self.cylinder_angular_extent
        self.stim_object = copy.copy(self.stim_object_template).shiftTexture((shift_u, 0)).rotate(np.radians(theta), np.radians(phi), np.radians(angle))


class ExpandingEdges(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, rate=60, period=20, vert_extent=80, theta_offset=0,
                  expander_color = 0.0, opposite_color = 1.0, width_0=2, n_theta_pixels=360, hold_duration=0.550,
                  color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.0, cylinder_location=(0, 0, 0)):
        """
        Periodic bars of randomized intensity painted on the inside of a cylinder.

        :param rate: rotation rate of the expanding bars, degrees/sec
        :param period: spatial period (degrees)
        :param width_0: width (degrees) of each expanding bar at the beginning
        :param vert_extent: vertical extent (degrees) of bars
        :param theta_offset: phase offset of periodic bar pattern (degrees)
        :param expander_color: color of the expanding edge [0, 1]
        :param opposite_color: color of the diminishing edge [0, 1]
        :param n_theta_pixels: number of pixels in theta for the image painted onto the cylinder
        :param hold_duration: duration for which the initial image is held (seconds)
        :other params: see TexturedCylinder
        """
        # assuming fly is at (0,0,0), calculate cylinder height required to achieve vert_extent (degrees)
        # tan(vert_extent/2) = (cylinder_height/2) / cylinder_radius
        assert vert_extent < 180
        cylinder_height = 2 * cylinder_radius * np.tan(np.radians(vert_extent/2))
        super().configure(color=color, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height, theta=theta, phi=phi, angle=angle)

        self.rate = rate
        self.period = period
        self.vert_extent = vert_extent
        self.theta_offset = theta_offset
        self.cylinder_location = cylinder_location

        self.expander_color = expander_color
        self.opposite_color = opposite_color
        self.width_0 = width_0 #degrees
        self.n_x = int(n_theta_pixels) # number of theta pixels in img (approximate, as the number of pixels in each subimage is floored)
        self.hold_duration = hold_duration #seconds

        self.n_subimg = int(np.floor(360/self.period)) # number of subimages to be repeated
        self.n_x_subimg = int(np.floor(self.n_x / self.n_subimg)) # number of theta pixels in each subimg
        self.rate_abs = np.abs(rate)

        self.subimg_mask = np.empty(self.n_x_subimg, dtype=bool)
        self.subimg = np.empty((1,self.n_x_subimg), dtype=np.uint8)

        img = np.zeros((1, int(self.n_x))).astype(np.uint8)
        self.add_texture_gl(img, texture_interpolation='NEAREST')

        # Only renders part of the cylinder if the period is not a divisor of 360
        self.cylinder_angular_extent = self.n_subimg * self.period  # degrees

        self.stim_object_template = GlCylinder(cylinder_height=self.cylinder_height,
                                               cylinder_radius=self.cylinder_radius,
                                               cylinder_angular_extent=self.cylinder_angular_extent,
                                               color=self.color,
                                               cylinder_location=self.cylinder_location,
                                               texture=True)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        theta = return_for_time_t(self.theta, t)
        phi = return_for_time_t(self.phi, t)
        angle = return_for_time_t(self.angle, t)

        self.stim_object = copy.copy(self.stim_object_template).rotate(np.radians(theta), np.radians(phi), np.radians(angle))

        # Construct one subimg

        fill_to_degrees = self.width_0 + self.rate_abs * max(t - self.hold_duration, 0)
        fill_to_proportion = min(fill_to_degrees/self.period, 1)
        fill_to_subimg_x = int(np.round(fill_to_proportion * self.n_x_subimg))

        self.subimg_mask[:fill_to_subimg_x] = True
        self.subimg_mask[fill_to_subimg_x:] = False
        if np.sign(self.rate) > 0:
            self.subimg_mask = np.flip(self.subimg_mask)

        self.subimg[:,self.subimg_mask] = np.uint8(self.expander_color * 255)
        self.subimg[:,~self.subimg_mask] = np.uint8(self.opposite_color * 255)
        img = np.tile(self.subimg, self.n_subimg)

        # theta_offset
        theta_offset_degs = self.period * (self.theta_offset / 360)
        img = np.roll(img, int(np.round(theta_offset_degs * self.n_x / 360)), axis=1)

        self.update_texture_gl(img)



class RandomBars(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, period=20, width=5, vert_extent=80, theta_offset=0, background=0.5,
                  distribution_data=None, update_rate=60.0, start_seed=0,
                  color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.0, cylinder_location=(0, 0, 0)):
        """
        Periodic bars of randomized intensity painted on the inside of a cylinder.

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
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args', []), **distribution_data.get('kwargs', {}))

        self.period = period
        self.width = width
        self.vert_extent = vert_extent
        self.theta_offset = theta_offset
        self.background = background
        self.update_rate = update_rate
        self.start_seed = start_seed
        self.cylinder_location = cylinder_location

        img = np.zeros((1, 255)).astype(np.uint8)
        self.add_texture_gl(img, texture_interpolation='NEAREST')

        # Only renders part of the cylinder if the period is not a divisor of 360
        self.n_bars = int(np.floor(360/self.period))
        self.cylinder_angular_extent = self.n_bars * self.period  # degrees

        self.stim_object_template = GlCylinder(cylinder_height=self.cylinder_height,
                                               cylinder_radius=self.cylinder_radius,
                                               cylinder_angular_extent=self.cylinder_angular_extent,
                                               color=self.color,
                                               cylinder_location=self.cylinder_location,
                                               texture=True)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
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
        self.update_texture_gl(img)


class RandomGrid(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, patch_width=10, patch_height=10, cylinder_vertical_extent=160, cylinder_angular_extent=360,
                  distribution_data=None, update_rate=60.0, start_seed=0,
                  color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.0, rgb_texture=False):
        """
        Random square grid pattern painted on the inside of a cylinder.

        :param patch width: Azimuth extent (degrees) of each patch
        :param patch height: Elevation extent (degrees) of each patch
        :param cylinder_vertical_extent: Elevation extent of the entire cylinder (degrees)
        :param cylinder_angular_extent: Azimuth extent of the cylinder `texture` (degrees)
        :param distribution_data: dict. containing name and args/kwargs for random distribution (see flystim.distribution)
        :param update_rate: Hz, update rate of bar intensity
        :param start_seed: seed with which to start rng at the beginning of the stimulus presentation

        :other params: see TexturedCylinder
        """
        self.rgb_texture = rgb_texture

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
        self.noise_distribution = getattr(distribution, distribution_data['name'])(*distribution_data.get('args', []), **distribution_data.get('kwargs', {}))

        self.patch_width = patch_width
        self.patch_height = patch_height
        self.start_seed = start_seed
        self.update_rate = update_rate

        if self.rgb_texture:
            img = np.zeros((self.n_patches_height, self.n_patches_width, 3)).astype(np.uint8)
        else:
            img = np.zeros((self.n_patches_height, self.n_patches_width)).astype(np.uint8)

        self.add_texture_gl(img, texture_interpolation='NEAREST')

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        # set the seed
        seed = int(round(self.start_seed + t*self.update_rate))
        np.random.seed(seed)

        # get the random values
        if self.rgb_texture:  # shape = (x, y, 3)
            face_colors = 255*self.noise_distribution.get_random_values((self.n_patches_height, self.n_patches_width, 3))
            img = np.reshape(face_colors, (self.n_patches_height, self.n_patches_width, 3)).astype(np.uint8)
        else:  # shape = (x, y) monochromatic
            face_colors = 255*self.noise_distribution.get_random_values((self.n_patches_height, self.n_patches_width))
            img = np.reshape(face_colors, (self.n_patches_height, self.n_patches_width)).astype(np.uint8)
        # make the texture
        self.update_texture_gl(img)


class Checkerboard(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, patch_width=4, patch_height=4, cylinder_vertical_extent=160, cylinder_angular_extent=360,
                  color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.0):
        """
        Periodic checkerboard pattern painted on the inside of a cylinder.

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
        self.add_texture_gl(img, texture_interpolation='NEAREST')

        self.stim_object = GlCylinder(cylinder_height=self.cylinder_height,
                                      cylinder_radius=self.cylinder_radius,
                                      cylinder_angular_extent=self.cylinder_angular_extent,
                                      color=self.color,
                                      texture=True).rotate(np.radians(self.theta), np.radians(self.phi), np.radians(self.angle))

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        pass


class Tower(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[1, 0, 0, 1], cylinder_radius=0.5, cylinder_height=0.5, cylinder_location=[+5, 0, 0], n_faces=16):
        """
        Cylindrical tower object in arbitrary x, y, z coords.

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

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        pass


class TexturedGround(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen)
        self.use_texture = True

    def configure(self, color=[0.5, 0.5, 0.5, 1.0], z_level=-0.1, side_length=5, rand_seed=0):
        """
        Infinite textured ground.

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

        self.stim_object = GlQuad(v1, v2, v3, v4, self.color,
                                  tc1=(0, 0), tc2=(1, 0), tc3=(1, 1), tc4=(0, 1),
                                  texture_shift=(0, 0), use_texture=True)

        # create the texture
        np.random.seed(self.rand_seed)
        face_colors = np.random.uniform(size=(128, 128))

        # make and apply the texture
        img = (255*face_colors).astype(np.uint8)
        self.add_texture_gl(img, texture_interpolation='LINEAR')

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        pass


class HorizonCylinder(TexturedCylinder):
    def __init__(self, screen):
        super().__init__(screen=screen)

    def configure(self, color=[1, 1, 1, 1], cylinder_radius=5, cylinder_height=5, cylinder_pitch=0, cylinder_yaw=0,
                  theta=0,
                  image_name=None, filter_name=None, filter_kwargs={}):

        super().configure(color=color, cylinder_radius=cylinder_radius, cylinder_height=cylinder_height, theta=theta, phi=0, angle=0.0)
        self.cylinder_pitch = cylinder_pitch
        self.cylinder_yaw = cylinder_yaw
        if image_name is not None:
            t0 = time.time()
            image_object = image.Image(image_name)
            if filter_name is not None:  # use filtered image
                if filter_name == 'whiten':
                    texture_img = image_object.whiten_image()
                else:
                    texture_img = image_object.filter_image(filter_name, filter_kwargs)
            else:  # use original image
                texture_img = image_object.load_image()

            print('LOADED TEXTURE IMAGE FROM {}. \n SHAPE={}, FILTER={} ({:.2f} sec)'.format(image_object.image_path,
                                                                                             texture_img.shape,
                                                                                             filter_name,
                                                                                             time.time()-t0))

        else:
            # use a dummy texture
            np.random.seed(0)
            face_colors = np.random.uniform(size=(128, 128))
            texture_img = (255*face_colors).astype(np.uint8)

            print('USING DUMMY TEXTURE. SHAPE = {}'.format(texture_img.shape))

        self.add_texture_gl(texture_img, texture_interpolation='LINEAR')

        self.stim_template = GlCylinder(cylinder_height=self.cylinder_height,
                                        cylinder_radius=self.cylinder_radius,
                                        cylinder_location=(0, 0, 0),
                                        color=self.color,
                                        texture=True).rotz(np.radians(180))
    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        theta = return_for_time_t(self.theta, t)
        cyl_position = fly_position.copy()  # cylinder moves with the fly, so fly is always in the center
        self.stim_object = copy.copy(self.stim_template).translate(cyl_position).rotz(np.radians(theta)).roty(np.radians(self.cylinder_yaw)).rotx(np.radians(self.cylinder_pitch))


class Forest(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=1000)

    def configure(self, color=[1, 1, 1, 1], cylinder_radius=0.5, cylinder_height=0.5, n_faces=16, cylinder_locations=[[+5, 0, 0]]):
        """
        Collection of tower objects created with a single shader program.

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
                              cylinder_location=[0, 0, 0],
                              color=self.color,
                              n_faces=self.n_faces)

        for tree_loc in self.cylinder_locations:
            new_cyl = copy.copy(cylinder).translate(tree_loc)
            self.stim_object.add(new_cyl)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        pass


class MovingDotField(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=10000)
        self.draw_mode = 'POINTS'

    def configure(self, n_points=20, point_size=20, sphere_radius=1, color=[1, 1, 1, 1],
                  speed=40, signal_direction=0, coherence=1.0, random_seed=0, sphere_pitch=0):
        """
        Collection of moving points. Tunable coherence.

        Note that points are all the same size, so no area correction is made for perspective
        """
        self.n_points = n_points
        self.point_size = point_size
        self.sphere_radius = sphere_radius
        self.color = color
        self.speed = speed  # Deg/sec
        self.signal_direction = signal_direction  # In theta/phi plane. [0, 360] degrees
        self.coherence = coherence  # [0-1]
        self.random_seed = random_seed
        self.sphere_pitch = sphere_pitch  # Degrees. Pitch to the entire sphere on which dots move. Shifts signal direction axes

        self.stim_object = GlVertices()

        self.stim_object_template = GlSphericalPoints(sphere_radius=self.sphere_radius,
                                                      color=self.color,
                                                      theta=[0],
                                                      phi=[0])

        # Set random seed
        rng = default_rng(self.random_seed)

        self.starting_theta = rng.uniform(0, 2*np.pi, self.n_points)
        self.starting_phi = rng.uniform(-np.pi/2, +np.pi/2, self.n_points)

        # Make velocity vectors for each point
        self.velocity_vectors = []
        is_signal = rng.choice([False, True], self.n_points, p=[1-self.coherence, self.coherence])
        for pt in range(self.n_points):
            if is_signal[pt]:
                dir = self.signal_direction
            else:
                dir = rng.uniform(0, 360)

            vec = self.speed*np.array([np.cos(np.deg2rad(dir)), np.sin(np.deg2rad(dir))])
            self.velocity_vectors.append(vec)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        sphere_pitch_rad = np.radians(self.sphere_pitch)

        self.stim_object = GlVertices()
        for pt in range(self.n_points):
            d_xy = self.velocity_vectors[pt] * t  # Change in (theta, phi) position, in degrees
            new_theta = self.starting_theta[pt] + np.radians(d_xy[0])
            # Bounce phi back from pi to 0. Shift by pi/2 because of offset in where point is rendered in flystim.shapes
            new_phi = (self.starting_phi[pt] + np.radians(d_xy[1])) % np.pi - np.pi/2
            self.stim_object.add(copy.copy(self.stim_object_template).rotate(new_theta,  # yaw
                                                                             new_phi,  # pitch
                                                                             0).rotate(0, sphere_pitch_rad, 0))


class MovingDotField_Cylindrical(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=10000)
        self.draw_mode = 'POINTS'

    def configure(self, n_points=20, point_size=20, cylinder_radius=1, color=[1, 1, 1, 1],
                  speed=40, signal_direction=0, coherence=1.0, random_seed=0, cylinder_pitch=0, phi_limits=[0, 180]):
        """
        Collection of moving points that move on a rotating cylinder. Tunable coherence.

        Note that points are all the same size, so no area correction is made for perspective
        """
        self.n_points = n_points
        self.point_size = point_size
        self.cylinder_radius = cylinder_radius
        self.color = color
        self.speed = speed  # Deg/sec
        self.signal_direction = signal_direction  # In theta/phi plane. [0, 360] degrees
        self.coherence = coherence  # [0-1]
        self.random_seed = random_seed
        # Pitch to the entire cylinder on which dots move. Shifts signal direction axes
        # Note this pitch happens after the phi limits, so ultimate phi limits are changed by pitch
        self.cylinder_pitch = cylinder_pitch  # Degrees.
        self.phi_limits = phi_limits  # [lower, upper], degrees. Default = entire elevation range (0, 180)

        self.stim_object = GlVertices()

        # Set random seed
        rng = default_rng(self.random_seed)
        self.starting_theta = rng.uniform(0, 360, self.n_points)  # degrees
        self.starting_phi = rng.uniform(self.phi_limits[0], self.phi_limits[1], self.n_points)  # degrees

        self.stim_object_list = []
        self.dir_list = []
        is_signal = rng.choice([False, True], self.n_points, p=[1-self.coherence, self.coherence])
        for pt in range(self.n_points):
            if is_signal[pt]:
                self.dir_list.append(np.radians(self.signal_direction))
            else:
                self.dir_list.append(np.radians(rng.uniform(0, 360)))

            self.stim_object_list.append(GlCylindricalPoints(cylinder_radius=self.cylinder_radius,
                                                             color=self.color,
                                                             theta=[self.starting_theta[pt]],
                                                             phi=[self.starting_phi[pt]]))

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        cyl_pitch = np.radians(self.cylinder_pitch)
        dtheta = np.radians(self.speed * t)
        self.stim_object = GlVertices()
        for pt in range(self.n_points):
            self.stim_object.add(self.stim_object_list[pt].rotz(dtheta).roty(self.dir_list[pt]).rotx(cyl_pitch))

class UniformMovingDotField_Cylindrical(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=10000)
        self.draw_mode = 'POINTS'

    def configure(self, n_points=20, point_size=20, cylinder_radius=1, color=[1, 1, 1, 1],
                  speed=40, direction=0, random_seed=0, cylinder_pitch=0, phi_limits=[0, 180]):
        """
        Collection of moving points that move on a rotating cylinder. Tunable coherence.

        Note that points are all the same size, so no area correction is made for perspective
        """
        self.n_points = n_points
        self.point_size = point_size
        self.cylinder_radius = cylinder_radius
        self.color = color
        self.speed = speed  # Deg/sec
        self.direction = direction  # In theta/phi plane. [0, 360] degrees
        self.random_seed = random_seed
        # Pitch to the entire cylinder on which dots move. Shifts direction axes
        # Note this pitch happens after the phi limits, so ultimate phi limits are changed by pitch
        self.cylinder_pitch = cylinder_pitch  # Degrees.
        self.phi_limits = phi_limits  # [lower, upper], degrees. Default = entire elevation range (0, 180)

        self.stim_object = GlVertices()

        # Set random seed
        rng = default_rng(self.random_seed)
        self.starting_theta = rng.uniform(0, 360, self.n_points)  # degrees
        self.starting_phi = rng.uniform(self.phi_limits[0], self.phi_limits[1], self.n_points)  # degrees

        self.stim_object_list = []
        self.direction_rad = np.radians(self.direction)
        self.stim_object_template = GlCylindricalPoints(cylinder_radius=self.cylinder_radius,
                                                        color=self.color,
                                                        theta=self.starting_theta,
                                                        phi=self.starting_phi)


    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        cyl_pitch = np.radians(self.cylinder_pitch)
        dtheta = np.radians(self.speed * t)
        self.stim_object = copy.copy(self.stim_object_template).rotz(dtheta).roty(self.direction_rad).rotx(cyl_pitch)

class ProgressiveStarfield(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=10000)
        self.draw_mode = 'POINTS'

    def configure(self, point_size=20, color=[1, 1, 1, 1],
                  point_locations=[[+5, 0, 0]],
                  y_offset=0):
        """

        Note that points are all the same size, so no area correction is made for perspective
        """
        self.point_size = point_size
        self.color = color
        self.point_locations = point_locations  # list of (x, y, z) meters for each dot
        self.y_offset = make_as_trajectory(y_offset)  # Can pass Y offset as trajectory to specify approach

        self.stim_template = GlPointCollection(locations=self.point_locations,
                                               color=self.color)

        self.stim_object = copy.copy(self.stim_template)

    def eval_at(self, t, fly_position=[0, 0, 0], fly_heading=[0, 0]):
        y_position = return_for_time_t(self.y_offset, t)
        self.stim_object = copy.copy(self.stim_template).translate([0, y_position, 0])




# %%
