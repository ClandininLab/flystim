import numpy as np
from math import radians
from .util import get_rgba, rotx, roty, rotz, translate, scale

class GlVertices:
    def __init__(self, vertices=None, colors=None):
        self.vertices = vertices
        self.colors = colors

    def add(self, obj):
        # add vertices
        if self.vertices is None:
            self.vertices = obj.vertices
        else:
            self.vertices = np.concatenate((self.vertices, obj.vertices), axis=1)

        # add colors
        if self.colors is None:
            self.colors = obj.colors
        else:
            self.colors = np.concatenate((self.colors, obj.colors), axis=1)

    def rotx(self, th):
        return GlVertices(vertices=rotx(self.vertices, th), colors=self.colors)

    def roty(self, th):
        return GlVertices(vertices=roty(self.vertices, th), colors=self.colors)

    def rotz(self, th):
        return GlVertices(vertices=rotz(self.vertices, th), colors=self.colors)

    def scale(self, amt):
        return GlVertices(vertices=scale(self.vertices, amt), colors=self.colors)

    def translate(self, amt):
        return GlVertices(vertices=translate(self.vertices, amt), colors=self.colors)

    @property
    def data(self):
        data = np.concatenate((self.vertices, self.colors), axis=0)
        return data.flatten(order='F')

class GlTri(GlVertices):
    def __init__(self, v1, v2, v3, color):
        vertices = np.concatenate((v1, v2, v3)).reshape((3, 3), order='F')
        colors = np.concatenate((color, color, color)).reshape((4, 3), order='F')
        super().__init__(vertices=vertices, colors=colors)

class GlQuad(GlVertices):
    def __init__(self, v1, v2, v3, v4, color):
        super().__init__()
        self.add(GlTri(v1, v2, v3, color))
        self.add(GlTri(v1, v3, v4, color))


class GlCube(GlVertices):
    def __init__(self, colors=None, def_alpha=1.0):
        # call the super constructor
        super().__init__()

        # set defaults
        if colors is None:
            colors = {}
        if '+x' not in colors:
            colors['+x'] = 'blue'
        if '-x' not in colors:
            colors['-x'] = 'green'
        if '+y' not in colors:
            colors['+y'] = 'red'
        if '-y' not in colors:
            colors['-y'] = 'cyan'
        if '+z' not in colors:
            colors['+z'] = 'yellow'
        if '-z' not in colors:
            colors['-z'] = 'magenta'

        # convert colors to RGBA
        colors = {key: get_rgba(val, def_alpha=def_alpha) for key, val in colors.items()}

        # shorten name for side length for readability
        s = 0.5

        # add all of the faces
        self.add(GlQuad((+s, -s, -s), (+s, +s, -s), (+s, +s, +s), (+s, -s, +s), colors['+x']))
        self.add(GlQuad((-s, -s, -s), (-s, +s, -s), (-s, +s, +s), (-s, -s, +s), colors['-x']))
        self.add(GlQuad((+s, +s, -s), (-s, +s, -s), (-s, +s, +s), (+s, +s, +s), colors['+y']))
        self.add(GlQuad((+s, -s, -s), (-s, -s, -s), (-s, -s, +s), (+s, -s, +s), colors['-y']))
        self.add(GlQuad((+s, -s, +s), (+s, +s, +s), (-s, +s, +s), (-s, -s, +s), colors['+z']))
        self.add(GlQuad((+s, -s, -s), (+s, +s, -s), (-s, +s, -s), (-s, -s, -s), colors['-z']))


class GlSphericalRect(GlVertices):
    def __init__(self,
                 width=None,  # degrees, theta
                 height=None,  # degrees, phi
                 radius=None,  # meters
                 color=None,  # (r,g,b,a)
                 center=None,  # degrees, (theta, phi)
                 n_steps_x=None,
                 n_steps_y=None):
        super().__init__()
        if width is None:
            width = 20
        if height is None:
            height = 20
        if radius is None:
            radius = 1
        if color is None:
            color = (1, 1, 1, 1)
        if center is None:
            center = (0, 0)
        if n_steps_x is None:
            n_steps_x = 6
        if n_steps_y is None:
            n_steps_y = 6

        d_theta = (1/n_steps_x) * radians(width)
        d_phi = (1/n_steps_y) * radians(height)
        for rr in range(n_steps_y):
            for cc in range(n_steps_x):
                # render patch at the equator (phi=pi/2) so it's not near the poles
                theta = radians(width) * (-1/2 + (cc/n_steps_x))
                phi = np.pi/2 + radians(height) * (-1/2 + (rr/n_steps_y))
                v1 = self.sphericalToCartesian((radius, theta, phi))
                v2 = self.sphericalToCartesian((radius, theta, phi + d_phi))
                v3 = self.sphericalToCartesian((radius, theta + d_theta, phi))
                v4 = self.sphericalToCartesian((radius, theta + d_theta, phi + d_phi))
                self.add(GlTri(v1, v2, v4, color).rotz(radians(center[0])).roty(radians(center[1])))
                self.add(GlTri(v1, v3, v4, color).rotz(radians(center[0])).roty(radians(center[1])))

    def sphericalToCartesian(self, spherical_coords):
        r, theta, phi = spherical_coords
        cartesian_coords = (r * np.sin(phi) * np.cos(theta),
                            r * np.sin(phi) * np.sin(theta),
                            r * np.cos(phi))
        return cartesian_coords


class GlSphericalCirc(GlVertices):
    def __init__(self,
                 circle_radius=None,  # degrees in spherical coordinates
                 sphere_radius=None,  # meters
                 color=None,  # (r,g,b,a)
                 center=None,  # degrees, (theta, phi)
                 n_steps=None):
        super().__init__()
        if circle_radius is None:
            circle_radius = 20
        if sphere_radius is None:
            sphere_radius = 1
        if color is None:
            color = (1, 1, 1, 1)
        if center is None:
            center = (0, 0)
        if n_steps is None:
            n_steps = 36

        v_center = self.sphericalToCartesian((sphere_radius, 0, np.pi/2))

        angles = np.linspace(0, 2*np.pi, n_steps+1)
        for wedge in range(n_steps):
            v1 = self.sphericalToCartesian((sphere_radius,
                                            radians(circle_radius)*np.cos(angles[wedge]),
                                            np.pi/2 + radians(circle_radius)*np.sin(angles[wedge])))
            v2 = self.sphericalToCartesian((sphere_radius,
                                            radians(circle_radius)*np.cos(angles[wedge+1]),
                                            np.pi/2 + radians(circle_radius)*np.sin(angles[wedge+1])))

            self.add(GlTri(v1, v2, v_center, color).rotz(radians(center[0])).roty(radians(center[1])))

    def sphericalToCartesian(self, spherical_coords):
        r, theta, phi = spherical_coords
        cartesian_coords = (r * np.sin(phi) * np.cos(theta),
                            r * np.sin(phi) * np.sin(theta),
                            r * np.cos(phi))
        return cartesian_coords
