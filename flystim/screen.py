import numpy as np
import matplotlib.pyplot as plt

from math import sin, cos

from flystim.triangle import tri_draw

COLOR_LIST = ['b', 'g', 'r', 'c', 'm', 'y']

class Screen:
    """
    Class representing the configuration of a single screen used in the display of stimuli.
    Parameters such as screen coordinates and the ID # are represented.
    """

    def __init__(self, width=None, height=None, rotation=None, offset=None, server_number=None, id=None,
                 fullscreen=None, vsync=None, square_side=None, square_loc=None, name=None, tri_list=None):
        """
        :param width: width of the screen (meters)
        :param height: height of the screen (meters)
        :param rotation: rotation of the screen about the z axis (radians).  a value of zero corresponds to the screen
        width being aligned along the x axis.
        :param offset: position of the center of the screen (3-vector in meters).
        :param server_number: ID # of the X server
        :param id: ID # of the screen
        :param fullscreen: Boolean.  If True, display stimulus fullscreen (default).  Otherwise, display stimulus
        in a window.
        :param vsync: Boolean.  If True, lock the framerate to the redraw rate of the screen.
        :param square_side: Length of photodiode synchronization square (meters).
        :param square_loc: Location of photodiode synchronization square (one of 'll', 'lr', 'ul', 'ur')
        :param name: descriptive name to associate with this screen
        :param tri_list: list of triangular patches defining the screen geometry.  this is a list of 3-tuples
        representing each triangle.  each of these 3-tuples lists contains three 5-tuples, each of whose entries are
        (ndc-x, ndc-y, cartesian-x, cartesian-y, cartesian-z).  if the triangle list is not specified, then one
        is constructed automatically using rotation and offset.
        """

        # Set defaults for MacBook Pro (Retina, 15-inch, Mid 2015)

        if width is None:
            width = 0.332
        if height is None:
            height = 0.207
        if rotation is None:
            rotation = 0.0
        if offset is None:
            offset = (0.0, 0.3, 0.0)
        if server_number is None:
            server_number = 0
        if id is None:
            id = 0
        if fullscreen is None:
            fullscreen = True
        if vsync is None:
            vsync = True
        if square_side is None:
            square_side = 2e-2
        if square_loc is None:
            square_loc = 'll'
        if name is None:
            name = 'Screen' + str(id)

        # Construct a default triangle list if needed
        if tri_list is None:
            tri_list = self.compute_tri_list(width=width, height=height, offset=offset, rotation=rotation)

        # save the triangle list
        self.tri_list = tri_list

        # Save settings
        self.width = width
        self.height = height
        self.id = id
        self.server_number = server_number
        self.fullscreen = fullscreen
        self.vsync = vsync
        self.square_side = square_side
        self.square_loc = square_loc
        self.name = name

    @staticmethod
    def compute_tri_list(width, height, offset, rotation, ll_ndc=(-1, -1), ul_ndc=(-1, +1), ur_ndc=(+1, +1),
                         lr_ndc=(+1, -1)):
        def ndc2tup(ndc, x, y):
            cart_x = 0.5 * width  * cos(rotation) * x + offset[0]
            cart_y = 0.5 * width  * sin(rotation) * x + offset[1]
            cart_z = 0.5 * height                 * y + offset[2]

            return (ndc[0], ndc[1], cart_x, cart_y, cart_z)

        ll_tup = ndc2tup(ll_ndc, -1, -1)
        ul_tup = ndc2tup(ul_ndc, -1, +1)
        ur_tup = ndc2tup(ur_ndc, +1, +1)
        lr_tup = ndc2tup(lr_ndc, +1, -1)

        return [(lr_tup, ul_tup, ll_tup), (lr_tup, ur_tup, ul_tup)]

    def draw(self, ax):
        for tri in self.tri_list:
            # grab just the xyz coordinates of each point in the triangle
            p = [np.array(pt[-3:]) for pt in tri]

            # draw the triangle
            tri_draw(p[0], p[1], p[2], ax=ax, color=COLOR_LIST[self.id%len(COLOR_LIST)])

    def serialize(self):
        # get all variables needed to reconstruct the screen object
        vars = ['width', 'height', 'id', 'server_number', 'fullscreen', 'vsync', 'square_side', 'square_loc', 'name']
        data = {var: getattr(self, var) for var in vars}

        # special handling for tri_list since it could contain numpy values
        data['tri_list'] = []
        for tri in self.tri_list:
            data['tri_list'].append((
                    tuple(float(v) for v in tri[0]),
                    tuple(float(v) for v in tri[1]),
                    tuple(float(v) for v in tri[2])
            ))

        return data

    @staticmethod
    def deserialize(data):
        return Screen(**data)

def main():
    screen = Screen(offset=(0.0, +0.3, 0.0), rotation=0)

if __name__ == '__main__':
    main()
