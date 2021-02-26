from scipy.interpolate import interp1d
import numpy as np


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

        elif self.kwargs['name'] == 'Loom':
            """
            :rv_ratio: sec
            :stim_time: sec
            :start_size: deg.
            :end_size: deg.
            """
            # calculate angular size at t
            angular_size = 2 * np.rad2deg(np.arctan(self.kwargs['rv_ratio'] * (1 / (self.kwargs['stim_time'] - t))))

            # shift curve vertically so it starts at start_size. Calc t=0 size of trajector
            min_size = 2 * np.rad2deg(np.arctan(self.kwargs['rv_ratio'] * (1 / (self.kwargs['stim_time'] - 0))))
            size_adjust = min_size - self.kwargs['start_size']
            angular_size = angular_size - size_adjust

            # Cap the curve at end_size and have it just hang there
            if (angular_size > self.kwargs['end_size']):
                angular_size = self.kwargs['end_size']

            # divide by  2 to get spot radius
            val = angular_size / 2

        else:
            print('Unrecognized trajectory name. See flystim.trajectory')

        return val
