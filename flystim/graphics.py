import pyglet

class Item:
    def __init__(self, gl_type, dims):
        # save settings
        self.gl_type = gl_type
        self.dims = dims

        # set up vertex data
        self.vertex_data = []
        self.vertex_format = 'v{:d}f'.format(self.dims)

        # set up color data
        self.color_data = []
        self.color_format = 'c3f'

    def draw(self):
        if self.num_vertices > 0:
            pyglet.graphics.draw(self.num_vertices,
                                 self.gl_type,
                                 (self.vertex_format, self.vertex_data),
                                 (self.color_format, self.color_data))

    @property
    def num_vertices(self):
        return len(self.vertex_data) // self.dims

class Item2D(Item):
    def __init__(self, gl_type):
        super().__init__(gl_type=gl_type, dims=2)

class Item3D(Item):
    def __init__(self, gl_type):
        super().__init__(gl_type=gl_type, dims=3)