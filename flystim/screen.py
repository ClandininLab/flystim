import numpy as np

from math import sin, cos

class Screen:
    """
    Class representing the configuration of a single screen used in the display of stimuli.
    Parameters such as screen coordinates and the ID # are represented.
    """

    def __init__(self, width=None, height=None, rotation=None, offset=None, id=None, fullscreen=None, vsync=None,
                 square_side=None, square_loc=None, name=None):
        """
        :param width: width of the screen (meters)
        :param height: height of the screen (meters)
        :param rotation: rotation of the screen about the z axis (radians).  a value of zero corresponds to the screen
        width being aligned along the x axis.
        :param offset: position of the center of the screen (3-vector in meters).
        :param id: ID # of the screen
        :param fullscreen: Boolean.  If True, display stimulus fullscreen (default).  Otherwise, display stimulus
        in a window.
        :param vsync: Boolean.  If True, lock the framerate to the redraw rate of the screen.
        :param square_side: Length of photodiode synchronization square (meters).
        :param square_loc: Location of photodiode synchronization square (one of 'll', 'lr', 'ul', 'ur')
        :param name: descriptive name to associate with this screen
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

        # Save settings

        self.width = width
        self.height = height
        self.rotation = rotation
        self.offset = np.array(offset, dtype=float)
        self.id = id
        self.fullscreen = fullscreen
        self.vsync = vsync
        self.square_side = square_side
        self.square_loc = square_loc
        self.name = name

        #######################
        # derived values
        #######################

        # compute the vector pointing along the width of the screen
        self.vector = np.array([0.5*self.width*cos(self.rotation),
                                0.5*self.width*sin(self.rotation)])

def main():
    screen = Screen(offset=(0.0, +0.3, 0.0), rotation=0)

if __name__ == '__main__':
    main()