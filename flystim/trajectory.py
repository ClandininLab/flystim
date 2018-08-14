from scipy.interpolate import interp1d

class Trajectory:
    def __init__(self, tv_pairs, kind='linear'):
        self.tv_pairs = tv_pairs
        self.kind = kind

        # define interpolation function
        # ref: https://stackoverflow.com/questions/2184955/test-if-a-variable-is-a-list-or-tuple
        if hasattr(tv_pairs, '__iter__'):
            times, values = zip(*tv_pairs)
            self.eval_at = interp1d(times, values, kind=self.kind, fill_value='extrapolate')
        else:
            self.eval_at = lambda t: self.tv_pairs

    def to_dict(self):
        return {'tv_pairs': self.tv_pairs, 'kind': self.kind}

    @staticmethod
    def from_dict(d):
        return Trajectory(tv_pairs=d['tv_pairs'], kind=d['kind'])

class RectangleTrajectory:
    def __init__(self, x=90, y=90, w=2, h=8, angle=0, color=1):
        # set defaults
        if not isinstance(x, Trajectory):
            x = Trajectory(x)
        if not isinstance(y, Trajectory):
            y = Trajectory(y)
        if not isinstance(w, Trajectory):
            w = Trajectory(w)
        if not isinstance(h, Trajectory):
            h = Trajectory(h)
        if not isinstance(angle, Trajectory):
            angle = Trajectory(angle)
        if not isinstance(color, Trajectory):
            color = Trajectory(color)

        # save members
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.angle = angle
        self.color = color

    def to_dict(self):
        return {'x': self.x.to_dict(), 'y': self.y.to_dict(), 'w': self.w.to_dict(), 'h': self.h.to_dict(),
                'angle': self.angle.to_dict(), 'color': self.color.to_dict()}

    @staticmethod
    def from_dict(d):
        return RectangleTrajectory(x=Trajectory.from_dict(d['x']), y=Trajectory.from_dict(d['y']),
                                   w=Trajectory.from_dict(d['w']), h=Trajectory.from_dict(d['h']),
                                   angle=Trajectory.from_dict(d['angle']), color=Trajectory.from_dict(d['color']))
