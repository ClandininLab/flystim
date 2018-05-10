import numpy as np

# Note: definitions of vr, vu, vn vectors come from the following article
# http://csc.lsu.edu/~kooima/articles/genperspective/

class Screen:
    """
    Class representing the configuration of a single screen used in the display of stimuli.
    Parameters such as screen coordinates and the ID # are represented.
    """

    def __init__(self, id=0, pa=None, pb=None, pc=None, fullscreen=True, vsync=True):
        """
        :param id: ID # of the screen
        :param pa: 3D coordinates of the bottom left corner of the screen (numpy array with floating point data type)
        :param pb: 3D coordinates of the bottom right corner of the screen (numpy array with floating point data type)
        :param pc: 3D coordinates of the upper left corner of the screen (numpy array with floating point data type)
        :param fullscreen: Boolean.  If True, display stimulus fullscreen (default).  Otherwise, display stimulus
        in a window.
        """

        # Save settings
        # Defaults are for MacBook Pro (Retina, 15-inch, Mid 2015)

        # Screen ID
        self.id = id

        # Bottom left corner
        if pa is None:
            pa = np.array([-0.166, -0.1035, -0.3], dtype=float)
        self.pa = pa

        # Bottom right corner
        if pb is None:
            pb = np.array([+0.166, -0.1035, -0.3], dtype=float)
        self.pb = pb

        # Upper left corner
        if pc is None:
            pc = np.array([-0.166, +0.1035, -0.3], dtype=float)
        self.pc = pc

        # Fullscreen indicator
        self.fullscreen = fullscreen

        # VSYNC indicator
        self.vsync = vsync

    @property
    def vr(self):
        """
        Unit vector pointing from bottom left corner to bottom right corner
        """

        vr = self.pb - self.pa
        vr /= np.linalg.norm(vr)
        return vr

    @property
    def width(self):
        """
        Screen width, in meters.
        """

        width = np.linalg.norm(self.pb - self.pa)
        return width

    @property
    def vu(self):
        """
        Unit vector pointing from the bottom left corner to the upper left corner.
        """

        vu = self.pc - self.pa
        vu /= np.linalg.norm(vu)
        return vu

    @property
    def height(self):
        """
        Screen height, in meters.
        """

        height = np.linalg.norm(self.pc - self.pa)
        return height

    @property
    def vn(self):
        """
        Unit normal vector pointing out of the screen.
        """

        vn = np.cross(self.vr, self.vu)
        vn /= np.linalg.norm(vn)
        return vn
