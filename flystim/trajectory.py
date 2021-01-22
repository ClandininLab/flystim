from scipy.interpolate import interp1d
import numpy as np

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
        return {'tv_pairs': self.tv_pairs, 'kind': self.kind, 'traj_class': 'Trajectory'}

    @staticmethod
    def from_dict(d):
        return Trajectory(tv_pairs=d['tv_pairs'], kind=d['kind'])

class SinusoidalTrajectory:
    def __init__(self, v_0=0, amplitude=1, period=1, phase_offset=0):
        self.v_0 = v_0
        self.amplitude = amplitude
        self.period = period
        self.phase_offset = phase_offset

        self.eval_at = lambda t: self.amplitude * np.sin(2*np.pi/period * t + self.phase_offset) + self.v_0

    def to_dict(self):
        return {'v_0': self.v_0, 'amplitude': self.amplitude, 'period': self.period,
                'phase_offset': self.phase_offset, 'traj_class': 'SinusoidalTrajectory'}

    @staticmethod
    def from_dict(d):
        return SinusoidalTrajectory(v_0=d['v_0'], amplitude=d['amplitude'],
                                    period=d['period'], phase_offset=d['phase_offset'])


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

def get_traj_class(traj_class_name):
    if traj_class_name == "Trajectory":
        return Trajectory
    elif traj_class_name == "SinusoidalTrajectory":
        return SinusoidalTrajectory

class RectangleAnyTrajectory:
    '''
    Same as RectangleTrajectory but more flexible to permit use of Trajectory or SinusoidalTrajectory for each component.
    '''
    def __init__(self, x=90, y=90, w=2, h=8, angle=0, color=1):
        # set defaults
        if not (isinstance(x, Trajectory) or isinstance(x, SinusoidalTrajectory)):
            x = Trajectory(x)
        if not (isinstance(y, Trajectory) or isinstance(y, SinusoidalTrajectory)):
            y = Trajectory(y)
        if not (isinstance(w, Trajectory) or isinstance(w, SinusoidalTrajectory)):
            w = Trajectory(w)
        if not (isinstance(h, Trajectory) or isinstance(h, SinusoidalTrajectory)):
            h = Trajectory(h)
        if not (isinstance(angle, Trajectory) or isinstance(angle, SinusoidalTrajectory)):
            angle = Trajectory(angle)
        if not (isinstance(color, Trajectory) or isinstance(color, SinusoidalTrajectory)):
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
        return RectangleTrajectory(x=get_traj_class(d['x']['traj_class']).from_dict(d['x']),
                                   y=get_traj_class(d['y']['traj_class']).from_dict(d['y']),
                                   w=get_traj_class(d['w']['traj_class']).from_dict(d['w']),
                                   h=get_traj_class(d['h']['traj_class']).from_dict(d['h']),
                                   angle=get_traj_class(d['angle']['traj_class']).from_dict(d['angle']),
                                   color=get_traj_class(d['color']['traj_class']).from_dict(d['color']))
