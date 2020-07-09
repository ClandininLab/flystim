from math import sin, cos
from numbers import Number
import numpy as np

def listify(x, type_):
    if isinstance(x, (list, tuple)):
        return x

    if isinstance(x, type_):
        return [x]

    raise ValueError('Unknown input type: {}'.format(type(x)))

def normalize(vec):
    return vec / np.linalg.norm(vec)

# rotation matrix reference:
# https://en.wikipedia.org/wiki/Rotation_matrix

def rotx(pts, th):
    return rotx_mat(th).dot(pts)

def rotx_mat(th):
    return np.array([[1,       0,         0],
                     [0, +cos(th), -sin(th)],
                     [0, +sin(th), +cos(th)]], dtype=float)

def roty(pts, th):
    return roty_mat(th).dot(pts)

def roty_mat(th):
    return np.array([[+cos(th), 0, +sin(th)],
                     [0,        1,        0],
                     [-sin(th), 0, +cos(th)]], dtype=float)

def rotz(pts, th):
    return rotz_mat(th).dot(pts)

def rotz_mat(th):
    return np.array([[+cos(th), -sin(th), 0],
                     [+sin(th), +cos(th), 0],
                     [       0,        0, 1]], dtype=float)

def scale(pts, amt):
    return np.multiply(amt, pts)

def translate(pts, amt):
    # convert point(s) and translate amount to numpy arrays
    pts = np.array(pts, dtype=float)
    amt = np.array(amt, dtype=float)

    # add offset in a manner that depends on whether the input is 1D or 2D
    if len(pts.shape) == 1:
        return pts + amt
    elif len(pts.shape) == 2:
        return pts + amt[:, np.newaxis]

def get_rgba(val, def_alpha=1):
    # interpret string as RGB
    if isinstance(val, str):
        if val.lower() == 'red':
            val = (1, 0, 0)
        elif val.lower() == 'green':
            val = (0, 1, 0)
        elif val.lower() == 'blue':
            val = (0, 0, 1)
        elif val.lower() == 'yellow':
            val = (1, 1, 0)
        elif val.lower() == 'magenta':
            val = (1, 0, 1)
        elif val.lower() == 'cyan':
            val = (0, 1, 1)
        elif val.lower() == 'white':
            val = (1, 1, 1)
        elif val.lower() == 'black':
            val = (0, 0, 0)
        else:
            raise ValueError(f'Unknown color: {val}')

    # if a single number is given treat as monochrome
    if isinstance(val, Number):
        return (val, val, val, def_alpha)

    # otherwise if three numbers are given add the default alpha
    if len(val) == 3:
        return (val[0], val[1], val[2], def_alpha)
    elif len(val) == 4:
        return val
    else:
        raise ValueError(f'Cannot use value with length {len(val)}.')

# TODO: precisely when are flystim measurements taken? right before the frame is rendered?
def latency_report(flystim_timestamps, flystim_sync, fictrac_timestamps, fictrac_sync):
    """ Latency analysis report

    NOTE: this method was written to analyze timestamp logs as recorded. In particular, flystim_timestamps has units of
    seconds but fictrac_timestamps has units of milliseconds!!

    Args:
      flystim_timestamps: list of timestamps when sync square was updated - (n_fs, )
        units: seconds
      flystim_sync: list of sync square states, as recorded by flystim - (n_fs, )
      fictrac_timestamps: list of timestamps when fictrac captured a frame - (n_ft, )
        units: milliseconds
      fictrac_sync: list of sync square states, as captured by fictrac - (n_ft, )

    """
    assert len(flystim_timestamps) == len(flystim_sync)
    assert len(fictrac_timestamps) == len(fictrac_sync)

    flystim_timestamps = np.asarray(flystim_timestamps)
    flystim_sync = np.asarray(flystim_sync)
    # milliseconds -> seconds
    fictrac_timestamps = np.asarray(fictrac_timestamps) / 1000
    fictrac_sync = np.asarray(fictrac_sync)

    # TODO: why are non-zero values recorded
    # truncate non-zero values
    fs_mask = flystim_timestamps.astype(bool)
    flystim_timestamps = flystim_timestamps[fs_mask]
    flystim_sync = flystim_sync[fs_mask]

    ft_mask = fictrac_timestamps.astype(bool)
    fictrac_timestamps = fictrac_timestamps[ft_mask]
    fictrac_sync = fictrac_sync[ft_mask]

    template = "{:^20} | {:^16.4f} | {:^16.4f}"
    table_width = 60

    print("{:^20} | {:^16} | {:^16}".format("statistic", "flystim", "fictrac"))
    print("=" * table_width)

    print(
        template.format(
            "mean fps",
            1 / np.mean(np.diff(flystim_timestamps)),
            1 / np.mean(np.diff(fictrac_timestamps))
        )
    )
    print('-' * table_width)

    print(
        template.format(
            "mean frame length",
            np.mean(np.diff(flystim_timestamps)),
            np.mean(np.diff(fictrac_timestamps))
        )
    )
    print('-' * table_width)

    print(
        template.format(
            "std frame length",
            np.std(np.diff(flystim_timestamps)),
            np.std(np.diff(fictrac_timestamps))
        )
    )
    print('-' * table_width)

    print(
        template.format(
            "min frame length",
            np.min(np.diff(flystim_timestamps)),
            np.min(np.diff(fictrac_timestamps))
        )
    )
    print('-' * table_width)

    print(
        template.format(
            "max frame length",
            np.max(np.diff(flystim_timestamps)),
            np.max(np.diff(fictrac_timestamps))
        )
    )
    print('-' * table_width)
