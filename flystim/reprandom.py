import numpy as np

from scipy.signal import lsim
from scipy.interpolate import interp1d

def colored_noise(loc, scale, tau, dt, tmax):
    """
    Given colored noise process parameters, return a function that can be evaluated at any time to
    yield the process output.
    :param loc: Mean of the input white noise process.
    :param scale: Standard deviation of the input white noise process.
    :param tau: Time constant of the system filtering the white noise.
    :param dt: Time resolution used in calculating the effect of filtering the white noise.
    :param tmax: Maximum time at which output values are calculated.
    :return: A function that can be evaluated at any time to yield the output of the colored noise processed.  It is
    deterministic; the same value will be returned given the same time.
    """

    # generate white noise input
    t_in = np.arange(0, tmax+dt, dt)
    v_in = np.random.normal(loc=loc, scale=scale, size=t_in.size)

    # sanity check: make sure that tmax is included in the time range
    assert tmax <= t_in[-1]

    # color noise according to system dynamics
    # the initial value is set equal to the mean
    # of the distribution
    sys = (-1/tau, 1/tau, 1, 0)
    [t_out, v_out, _] = lsim(sys, U=v_in, T=t_in, X0=loc)

    # create interpolator to evaluate system output at arbitrary times,
    # with the endpoints are used as fill values
    color_func = interp1d(x=t_out, y=v_out, fill_value=(v_out[0], v_out[-1]), bounds_error=False)

    # return the function
    return color_func