from flystim1.screen import Screen
import numpy as np
from scipy.interpolate import interp1d

from warnings import warn

def make_tri_list():
    def dir_to_tri_list(dir):

        north_w = 2.956e-2
        side_w = 2.96e-2

        # set coordinates as a function of direction
        if dir == 'w':
           # set screen width and height
           h = 3.10e-2
           pts = [
                ((+0.4900, -0.3400), (-north_w/2, -side_w/2, -h/2)),
                ((+0.4900, -0.6550), (-north_w/2, +side_w/2, -h/2)),
                ((+0.2850, -0.6550), (-north_w/2, +side_w/2, +h/2)),
                ((+0.2850, -0.3400), (-north_w/2, -side_w/2, +h/2))
            ]
        elif dir == 'n':
           # set screen width and height
           h = 3.29e-2
           pts = [
                ((+0.1850, +0.5850), (-north_w/2, +side_w/2, -h/2)),
                ((+0.1850, +0.2800), (+north_w/2, +side_w/2, -h/2)),
                ((-0.0200, +0.2800), (+north_w/2, +side_w/2, +h/2)),
                ((-0.0200, +0.5850), (-north_w/2, +side_w/2, +h/2))
            ]

        elif dir == 'e':
            # set screen width and height
            h = 3.40e-2
            pts = [
                ((-0.1350, -0.3550), (+north_w/2, +side_w/2, -h/2)),
                ((-0.1350, -0.6550), (+north_w/2, -side_w/2, -h/2)),
                ((-0.3500, -0.6550), (+north_w/2, -side_w/2, +h/2)),
                ((-0.3500, -0.3550), (+north_w/2, +side_w/2, +h/2))
            ]
        else:
            raise ValueError('Invalid direction.')

        return Screen.quad_to_tri_list(*pts)

    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def shortest_deg_to_0(angle):
    angle = angle % 360
    return angle if abs(angle) < abs(angle-360) else angle-360


def latency_report(flystim_timestamps, flystim_sync, fictrac_timestamps, fictrac_sync,
                   window_size=10, n_windows=32):
    """ Latency analysis report


    Args:
      flystim_timestamps: list of timestamps when sync square was updated - (n_fs,)
        units: seconds
      flystim_sync: list of sync square states, as recorded by flystim - (n_fs,)
      fictrac_timestamps: list of timestamps when fictrac captured a frame - (n_ft,)
        units: seconds
      fictrac_sync: list of sync square states, as captured by fictrac - (n_ft,)
      window_size: size of window to use for local latency analysis
      n_windows: number of windows to compute lag for

    """
    assert len(flystim_timestamps) == len(flystim_sync)
    assert len(fictrac_timestamps) == len(fictrac_sync)

    flystim_timestamps = np.asarray(flystim_timestamps)
    flystim_sync = np.asarray(flystim_sync)
    fictrac_timestamps = np.asarray(fictrac_timestamps)
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

    # resample both traces to fictrac fps
    flystim_interp = interp1d(flystim_timestamps, flystim_sync)
    fictrac_interp = interp1d(fictrac_timestamps, fictrac_sync)

    resample_frame_len = np.mean(np.diff(fictrac_timestamps))

    time_bounds = (
        max(min(flystim_timestamps), min(fictrac_timestamps)),
        min(max(flystim_timestamps), max(fictrac_timestamps)),
    )
    trial_duration = time_bounds[1] - time_bounds[0]

    num_samples = 1 + int((time_bounds[1] - time_bounds[0]) / resample_frame_len)
    time_grid = np.linspace(*time_bounds, num_samples, endpoint=True)

    resampled_fs_sync = flystim_interp(time_grid)
    resampled_ft_sync = fictrac_interp(time_grid)

    global_lag = calculate_lag(resampled_fs_sync, resampled_ft_sync)

    print("Globally optimal lag: {:.1f}ms".format(global_lag * resample_frame_len * 1000))

    local_lags = []

    if window_size >= trial_duration:
        warn("window_size is larger than trial duration! try a smaller window_size")

    for start_time in np.linspace(time_bounds[0], time_bounds[1] - window_size, n_windows):
        time_grid = np.linspace(
            start_time,
            start_time + window_size,
            1  + int(window_size / resample_frame_len),
            endpoint=True
        )

        local_lags.append(
            calculate_lag(
                flystim_interp(time_grid),
                fictrac_interp(time_grid)
            ) * resample_frame_len * 1000
        )


    print("Local lag ({} {}s windows): {:.1f}ms mean, {:.1f}ms std".format(
        n_windows, window_size, np.mean(local_lags), np.std(local_lags)
    ))

    print("Total length of recording: {:1f} s".format(time_bounds[1] - time_bounds[0]))

# TODO: test!
# TODO: mean zero sequences?
def calculate_lag(ground_truth, lagged):
    """ Calculate delay between sequences that optimally aligns them

    Args:
      ground_truth: ground truth sequence to align against
      lagged: delayed ground truth sequence, perhaps with some added noise

    Returns
      lag: in units of indices!! - int
    """
    cross_corr = np.correlate(lagged, ground_truth, mode='full')
    return np.argmax(cross_corr) - len(ground_truth) + 1
