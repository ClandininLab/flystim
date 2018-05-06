import numpy as np

from scipy.signal import lsim
from scipy.interpolate import interp1d

def colored_noise(loc, scale, tau, dt, tmax):
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