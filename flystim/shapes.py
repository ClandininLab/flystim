import numpy as np
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
            colors['+z'] = 'magenta'
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
