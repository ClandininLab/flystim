import numpy as np

class Projection:
    def __init__(self, screen, pe=None, n=1e-2, f=100):
        # initialize input variables
        self._screen = None
        self._pe = None
        self._n = None
        self._f = None

        # initialize output variable
        self._mat = None

        # initialize state
        self.stale = True

        # set defaults
        if pe is None:
            pe = [0, 0, 0]

        # save settings
        self.screen = screen
        self.n = n
        self.f = f
        self.pe = pe

    def refresh(self):
        # ref: http://csc.lsu.edu/~kooima/articles/genperspective/

        # Determine frustum extents
        va = self.screen.pa - self.pe
        vb = self.screen.pb - self.pe
        vc = self.screen.pc - self.pe

        # Determine distance to screen
        d = -np.dot(self.screen.vn, va)

        # Compute screen coordinates
        l = np.dot(self.screen.vr, va) * self.n / d
        r = np.dot(self.screen.vr, vb) * self.n / d
        b = np.dot(self.screen.vu, va) * self.n / d
        t = np.dot(self.screen.vu, vc) * self.n / d

        # Projection matrix
        P = np.array([
            [(2.0 * self.n) / (r - l), 0, (r + l) / (r - l), 0],
            [0, (2.0 * self.n) / (t - b), (t + b) / (t - b), 0],
            [0, 0, -(self.f + self.n) / (self.f - self.n), -(2.0 * self.f * self.n) / (self.f - self.n)],
            [0, 0, -1, 0]], dtype=float)

        # Rotation matrix
        M = np.zeros((4,4), dtype=float)
        M[:3, 0] = self.screen.vr
        M[:3, 1] = self.screen.vu
        M[:3, 2] = self.screen.vn
        M[ 3, 3] = 1

        # Translation matrix
        T = np.eye(4, dtype=float)
        T[:3, 3] = -self.pe

        # Set output property
        self._mat = np.dot(np.dot(P, M.T), T)

        # Set state
        self.stale = False

    ####################################
    # input properties
    ####################################

    @property
    def screen(self):
        return self._screen

    @screen.setter
    def screen(self, val):
        self._screen = val
        self.stale = True

    @property
    def pe(self):
        return self._pe

    @pe.setter
    def pe(self, val):
        self._pe = np.array(val, dtype=float)
        self.stale = True

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, val):
        self._n = val
        self.stale = True

    @property
    def f(self):
        return self._f

    @f.setter
    def f(self, val):
        self._f = val
        self.stale = True

    ####################################
    # output properties
    ####################################

    @property
    def mat(self):
        if self.stale:
            self.refresh()

        return self._mat
