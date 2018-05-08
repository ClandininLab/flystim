import numpy as np

class Screen:
    def __init__(self, id=0, pa=None, pb=None, pc=None, fullscreen=True):
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

    # vr, vu, vn vectors are with reference to the following article:
    # http://csc.lsu.edu/~kooima/articles/genperspective/

    @property
    def vr(self):
        vr = self.pb - self.pa
        vr /= np.linalg.norm(vr)
        return vr

    @property
    def width(self):
        width = np.linalg.norm(self.pb - self.pa)
        return width

    @property
    def vu(self):
        vu = self.pc - self.pa
        vu /= np.linalg.norm(vu)
        return vu

    @property
    def height(self):
        height = np.linalg.norm(self.pc - self.pa)
        return height

    @property
    def vn(self):
        vn = np.cross(self.vr, self.vu)
        vn /= np.linalg.norm(vn)
        return vn