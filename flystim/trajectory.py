"""
Class + functions for making parameter trajectories for flystim stims.

Generally access this class using make_as_trajectory and return_for_time_t
"""
from scipy.interpolate import interp1d
import numpy as np


def make_as_trajectory(parameter):
    """Return parameter as Trajectory object if it is a dictionary."""
    if type(parameter) is dict: # trajectory-specifying dict
        return Trajectory(parameter)
    else: # not specified as a dict, just return the original param
        return parameter


def return_for_time_t(parameter, t):
    """Return param value at time t, if it is a Trajectory object."""
    if type(parameter) is Trajectory:
        return parameter.getValue(t)
    else: # not specified as a trajectory dict., just return the original param value
        return parameter


class Trajectory:
    """Trajectory class."""

    def __init__(self, kwargs):
        """
        Trajectory class. Can be used to specify parameter values as functions of time.

        Based on trajectory name, defines a getValue(t)

        :kwargs: dict of param/value pairs for this trajectory type, see individual ifs below...
            One key should always be 'name':
                :name: trajectory type. Currently supported: tv_pairs, Sinusoid, Loom.
        """
        if kwargs['name'] == 'tv_pairs':
            """
            List of arbitrary time-value pairs.

            :tv_pairs: list of time, value tuples. [(t0, v0), (t1, v1), ..., (tn, vn)]
            """
            times, values = zip(*kwargs['tv_pairs'])
            self.getValue = interp1d(times, values, kind=kwargs['kind'], fill_value='extrapolate')
        elif kwargs['name'] == 'Sinusoid':
            """
            Temporal sinusoid trajectory.

            :offset: Y offset
            :amplitude:
            :temporal_frequency: Hz
            """
            self.getValue = lambda t: kwargs['offset'] + kwargs['amplitude'] * np.sin(2*np.pi*kwargs['temporal_frequency']*t)

        elif kwargs['name'] == 'SinusoidWithDelay':
            """
            Temporal sinusoid trajectory, with a specified delay at the beginning. During the beginning, return delay value.

            :offset: Y offset
            :amplitude:
            :temporal_frequency: Hz
            :delay: seconds
            :delay_value:
            """
            self.getValue = lambda t: kwargs['delay_value'] if t < kwargs['delay'] else kwargs['offset'] + kwargs['amplitude'] * np.sin(2*np.pi*kwargs['temporal_frequency']*t)

        elif kwargs['name'] == 'Loom':
            """
            Expanding loom trajectory.

            :rv_ratio: sec
            :stim_time: sec
            :start_size: deg.
            :end_size: deg.
            """
            def get_loom_size(t):
                # calculate angular size at t
                angular_size = 2 * np.rad2deg(np.arctan(kwargs['rv_ratio'] * (1 / (kwargs['stim_time'] - t))))

                # shift curve vertically so it starts at start_size. Calc t=0 size of trajector
                min_size = 2 * np.rad2deg(np.arctan(kwargs['rv_ratio'] * (1 / (kwargs['stim_time'] - 0))))
                size_adjust = min_size - kwargs['start_size']
                angular_size = angular_size - size_adjust

                # Cap the curve at end_size and have it just hang there
                if (angular_size > kwargs['end_size']):
                    angular_size = kwargs['end_size']

                # divide by  2 to get spot radius
                return angular_size / 2
            self.getValue = get_loom_size

        else:
            print('Unrecognized trajectory name. See flystim.trajectory')
