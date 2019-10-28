import numpy as np
from math import radians
from .util import get_rgba, rotx, roty, rotz, translate, scale

class GlVertices:
    def __init__(self, vertices=None, colors=None, tex_coords=None):
        self.vertices = vertices
        self.colors = colors
        self.tex_coords = tex_coords

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

        # add tex_coords
        if self.tex_coords is None:
            self.tex_coords = obj.tex_coords
        else:
            self.tex_coords = np.concatenate((self.tex_coords, obj.tex_coords), axis=1)

    def rotx(self, th):
        return GlVertices(vertices=rotx(self.vertices, th), colors=self.colors, tex_coords=self.tex_coords)

    def roty(self, th):
        return GlVertices(vertices=roty(self.vertices, th), colors=self.colors, tex_coords=self.tex_coords)

    def rotz(self, th):
        return GlVertices(vertices=rotz(self.vertices, th), colors=self.colors, tex_coords=self.tex_coords)

    def scale(self, amt):
        return GlVertices(vertices=scale(self.vertices, amt), colors=self.colors, tex_coords=self.tex_coords)

    def translate(self, amt):
        return GlVertices(vertices=translate(self.vertices, amt), colors=self.colors, tex_coords=self.tex_coords)

    @property
    def data(self):
        if self.tex_coords is not None:
            data = np.concatenate((self.vertices, self.colors, self.tex_coords), axis=0)
        else:
            data = np.concatenate((self.vertices, self.colors), axis=0)
        return data.flatten(order='F')

class GlTri(GlVertices):
    def __init__(self, v1, v2, v3, color, tc1=None, tc2=None, tc3=None, texture=None):
        vertices = np.concatenate((v1, v2, v3)).reshape((3, 3), order='F')
        colors = np.concatenate((color, color, color)).reshape((4, 3), order='F')
        if tc1 is not None:
            tex_coords = np.concatenate((tc1, tc2, tc3)).reshape((2, 3), order='F')
        else:
            tex_coords = None
        super().__init__(vertices=vertices, colors=colors, tex_coords=tex_coords)

class GlQuad(GlVertices):
    def __init__(self, v1, v2, v3, v4, color, tc1=None, tc2=None, tc3=None, tc4=None, texture=None):
        super().__init__()
        self.add(GlTri(v1, v2, v3, color, tc1, tc2, tc3))
        self.add(GlTri(v1, v3, v4, color, tc1, tc3, tc4))


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
                 sphere_radius=None,  # meters
                 color=None,  # (r,g,b,a) or single value for monochrome, alpha = 1
                 n_steps_x=None,
                 n_steps_y=None):
        super().__init__()
        if width is None:
            width = 20
        if height is None:
            height = 20
        if sphere_radius is None:
            sphere_radius = 1
        if color is None:
            color = [1, 1, 1, 1]
        if type(color) is not list:
            if type(color) is tuple:
                color = list(color)
            else:
                color = [color, color, color, 1]
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
                v1 = self.sphericalToCartesian((sphere_radius, theta, phi))
                v2 = self.sphericalToCartesian((sphere_radius, theta, phi + d_phi))
                v3 = self.sphericalToCartesian((sphere_radius, theta + d_theta, phi))
                v4 = self.sphericalToCartesian((sphere_radius, theta + d_theta, phi + d_phi))
                self.add(GlTri(v1, v2, v4, color))
                self.add(GlTri(v1, v3, v4, color))


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
                 color=None,  # (r,g,b,a) or single value for monochrome, alpha = 1
                 n_steps=None):
        super().__init__()
        if circle_radius is None:
            circle_radius = 10
        if sphere_radius is None:
            sphere_radius = 1
        if color is None:
            color = [1, 1, 1, 1]
        if type(color) is not list:
            if type(color) is tuple:
                color = list(color)
            else:
                color = [color, color, color, 1]
        if n_steps is None:
            n_steps = 36

        v_center = self.sphericalToCartesian((sphere_radius, 0, np.pi/2))

        angles = np.linspace(0, 2*np.pi, n_steps+1)
        for wedge in range(n_steps):
            # render circle at the equator (phi=pi/2) so it's not near the poles
            v1 = self.sphericalToCartesian((sphere_radius,
                                            radians(circle_radius)*np.cos(angles[wedge]),
                                            np.pi/2 + radians(circle_radius)*np.sin(angles[wedge])))
            v2 = self.sphericalToCartesian((sphere_radius,
                                            radians(circle_radius)*np.cos(angles[wedge+1]),
                                            np.pi/2 + radians(circle_radius)*np.sin(angles[wedge+1])))

            self.add(GlTri(v1, v2, v_center, color))

    def sphericalToCartesian(self, spherical_coords):
        r, theta, phi = spherical_coords
        cartesian_coords = (r * np.sin(phi) * np.cos(theta),
                            r * np.sin(phi) * np.sin(theta),
                            r * np.cos(phi))
        return cartesian_coords

class GlCylinder(GlVertices):
    def __init__(self,
                 cylinder_height=None,  # meters
                 cylinder_radius=None,  # meters
                 cylinder_location=None, # (x,y,z) meters
                 color=None,  # (r,g,b,a) or single value for monochrome, alpha = 1
                 n_faces=None,
                 texture=False):
        super().__init__()
        if cylinder_height is None:
            cylinder_height = 10
        if cylinder_radius is None:
            cylinder_radius = 1
        if cylinder_location is None:
            cylinder_location = (0, 0, 0) # (0,0,0) is center of cylinder (r = 0 and z = height/2)
        if color is None:
            color = [1, 1, 1, 1]
        if type(color) is not list:
            if type(color) is tuple:
                color = list(color)
            else:
                color = [color, color, color, 1]
        if n_faces is None:
            n_faces = 64

        d_theta = 2*np.pi / n_faces
        for face in range(n_faces):
            v1 = self.cylindricalToCartesian((cylinder_radius, face*d_theta, cylinder_height/2))
            v2 = self.cylindricalToCartesian((cylinder_radius, face*d_theta, -cylinder_height/2))
            v3 = self.cylindricalToCartesian((cylinder_radius, (face+1)*d_theta, -cylinder_height/2))
            v4 = self.cylindricalToCartesian((cylinder_radius, (face+1)*d_theta, cylinder_height/2))

            if texture:
                self.add(GlQuad(v1, v2, v3, v4, color,
                                tc1=(face/n_faces, 1),
                                tc2=(face/n_faces, 0),
                                tc3=((face+1)/n_faces, 0),
                                tc4=((face+1)/n_faces, 1)).translate(cylinder_location))
            else:
                self.add(GlQuad(v1, v2, v3, v4, color).translate(cylinder_location))

    def cylindricalToCartesian(self, cylindrical_coords):
        r, theta, z = cylindrical_coords
        cartesian_coords = (r * np.cos(theta),
                            r * np.sin(theta),
                            z)
        return cartesian_coords
