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
            :kind: interpolation type. See scipy.interpolate.interp1d for options.
            """
            times, values = zip(*kwargs['tv_pairs'])
            self.getValue = interp1d(times, values, kind=kwargs['kind'], fill_value='extrapolate', axis=0)

        elif kwargs['name'] == 'tv_pairs_bounded':
            """
            List of arbitrary time-value pairs. 
            Values are optionally bounded by a lower and upper bound, and wrap around if they exceed the bounds.

            :tv_pairs: list of time, value tuples. [(t0, v0), (t1, v1), ..., (tn, vn)]
            :kind: interpolation type. See scipy.interpolate.interp1d for options.
            :bounds: lower and upper bounds for the value. (lower, upper) or None for no bounds.
            """
            times, values = zip(*kwargs['tv_pairs'])
            values_interpolated = interp1d(times, values, kind=kwargs['kind'], fill_value='extrapolate', axis=0)
            
            if kwargs.get('bounds', None) is None:
                self.getValue = values_interpolated
            else:            
                lo = min(*kwargs['bounds'])
                hi = max(*kwargs['bounds'])
                bound_range = hi - lo
                self.getValue = lambda t: np.mod(values_interpolated(t) - lo, bound_range) + lo
            
        elif kwargs['name'] == 'Sinusoid':
            """
            Temporal sinusoid trajectory.

            :offset: Y offset
            :amplitude:
            :temporal_frequency: Hz
            """
            self.getValue = lambda t: kwargs['offset'] + kwargs['amplitude'] * np.sin(2*np.pi*kwargs['temporal_frequency']*t)

        elif kwargs['name'] == 'SquareWave':
            """
            Temporal squarewave trajectory.

            :offset: Y offset
            :amplitude:
            :temporal_frequency: Hz
            """
            self.getValue = lambda t: kwargs['offset'] + kwargs['amplitude'] * np.sign(np.sin(2*np.pi*kwargs['temporal_frequency']*t))

        elif kwargs['name'] == 'SinusoidInTimeWindow':
            """
            Temporal sinusoid trajectory, only shown during a time window, defined by stim_start and stim_end.
            Alpha is 0 when

            :offset: Y offset
            :amplitude:
            :temporal_frequency: Hz
            :stim_start:
            :stim_end:
            """
            self.getValue = lambda t: [0,0,0,0] if t < kwargs['stim_start'] or t >= kwargs['stim_end'] else kwargs['offset'] + kwargs['amplitude'] * np.sin(2*np.pi*kwargs['temporal_frequency']*t)

        elif kwargs['name'] == 'Loom':
            """
            Expanding loom trajectory.

            :rv_ratio: sec
            :stim_time: sec
            :start_size: deg., diameter of spot
            :end_size: deg., diameter of spot

            : returns RADIUS of spot for time t
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

        elif kwargs['name'] == 'Loom_Gabb':
            """
            Expanding loom trajectory defined by rv ratio and collision time
            See def'n in Gabbiani et al., 1999
            https://www.jneurosci.org/content/jneuro/19/3/1122.full.pdf

            :rv_ratio: sec. Ratio of object physical length to approach speed
            :end_radius: deg., maximum radius of spot
            :collision_time: sec., time at which object is 180 deg

            : returns radius of spot for time t
            """

            def get_loom_size(t):
                # note this is spot radius
                angular_size = np.rad2deg( np.arctan( kwargs['rv_ratio'] / (kwargs['collision_time'] - t) ) )
                # Cap the curve at end_size and have it just hang there
                if (angular_size > kwargs['end_radius']):
                    angular_size = kwargs['end_radius']

                # Freeze it at the max in case there is more stim time to go
                if t > kwargs['collision_time']:
                    angular_size = kwargs['end_radius']

                return angular_size
            self.getValue = get_loom_size
            
        elif kwargs['name'] == 'Loom2':
            """
            Expanding loom trajectory. Fixed loom expansion rate based on rv_ratio.

            :rv_ratio: sec
            :start_size: deg.
            :end_size: deg.
            """
            def get_loom_size(t):
                # calculate angular size at t
                d0 = kwargs['rv_ratio'] / np.tan(np.deg2rad(kwargs['start_size'] / 2))
                angular_size = 2 * np.rad2deg(np.arctan(kwargs['rv_ratio'] * (1 / (d0 - t))))
                # Cap the curve at end_size and have it just hang there
                if angular_size > kwargs['end_size'] or d0 <= t:
                    angular_size = kwargs['end_size']
                return angular_size / 2
            self.getValue = get_loom_size

        else:
            print('Unrecognized trajectory name. See flystim.trajectory')
