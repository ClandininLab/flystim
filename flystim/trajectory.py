from scipy.interpolate import interp1d
import numpy as np


# class Trajectory:
#     def __init__(self, tv_pairs, kind='linear'):
#         self.tv_pairs = tv_pairs
#         self.kind = kind
#
#         # define interpolation function
#         # ref: https://stackoverflow.com/questions/2184955/test-if-a-variable-is-a-list-or-tuple
#         if hasattr(self.tv_pairs, '__iter__'):
            # times, values = zip(*self.tv_pairs)
            # self.eval_at = interp1d(times, values, kind=self.kind, fill_value='extrapolate')
#         else:
#             self.eval_at = lambda t: self.tv_pairs
#
#     def to_dict(self):
#         return {'tv_pairs': self.tv_pairs, 'kind': self.kind}
#
#     @staticmethod
#     def from_dict(d):
#         return Trajectory(tv_pairs=d['tv_pairs'], kind=d['kind'])


class Trajectory:
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def getValue(self, t):
        if self.kwargs['name'] == 'tv_pairs':
            """
            """
            times, values = zip(*self.kwargs['tv_pairs'])
            eval_at = interp1d(times, values, kind=self.kwargs['kind'], fill_value='extrapolate')
            val = eval_at(t)

        elif self.kwargs['name'] == 'Sinusoid':
            """
            """
            val = self.kwargs['offset'] + self.kwargs['amplitude'] * np.sin(2*np.pi*self.kwargs['temporal_frequency']*t)

        else:
            print('Unrecognized trajectory name. See flystim.trajectory')

        return val
