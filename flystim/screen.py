import numpy as np

class Screen:
    def __init__(self, id, pa, pb, pc):
        # initialize input variables
        self._pa = None
        self._pb = None
        self._pc = None

        # initialize output variables
        self._vr = None
        self._vu = None
        self._vn = None
        self._width = None
        self._height = None

        # initialize state
        self.stale = True

        # save settings
        self.id = id
        self.pa = pa
        self.pb = pb
        self.pc = pc

    def refresh(self):
        # ref: http://csc.lsu.edu/~kooima/articles/genperspective/

        # unit vector along width
        vr = self.pb - self.pa
        width = np.linalg.norm(vr)
        vr /= width

        # unit vector along height
        vu = self.pc - self.pa
        height = np.linalg.norm(vu)
        vu /= height

        # unit vector normal to screen
        vn = np.cross(vr, vu)
        vn /= np.linalg.norm(vn)

        # set output properties
        self._vr = vr
        self._vu = vu
        self._vn = vn
        self._width = width
        self._height = height

        # set state
        self.stale = False

    ####################################
    # input properties
    ####################################

    @property
    def pa(self):
        return self._pa

    @pa.setter
    def pa(self, val):
        self._pa = np.array(val, dtype=float)
        self.stale = True

    @property
    def pb(self):
        return self._pb

    @pb.setter
    def pb(self, val):
        self._pb = np.array(val, dtype=float)
        self.stale = True

    @property
    def pc(self):
        return self._pc

    @pc.setter
    def pc(self, val):
        self._pc = np.array(val, dtype=float)
        self.stale = True

    ####################################
    # output properties
    ####################################

    @property
    def vr(self):
        if self.stale:
            self.refresh()

        return self._vr

    @property
    def vu(self):
        if self.stale:
            self.refresh()

        return self._vu

    @property
    def vn(self):
        if self.stale:
            self.refresh()

        return self._vn

    @property
    def width(self):
        if self.stale:
            self.refresh()

        return self._width

    @property
    def height(self):
        if self.stale:
            self.refresh()

        return self._height
