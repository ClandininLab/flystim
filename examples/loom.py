#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory

import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=1, id=0, vsync=False))

    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    stim_time = 4
    start_size = 1
    end_size = 60
    rv_ratio = 5 / 1e3  # msec -> sec
    time_steps, angular_size = getLoomTrajectory(rv_ratio, stim_time, start_size, end_size)

    r_traj = Trajectory(list(zip(time_steps, angular_size)), kind='previous').to_dict()

    manager.load_stim(name='MovingSpot', radius=r_traj, phi=0, color=1, theta=0, sphere_radius=1.0, hold=True)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)


def getLoomTrajectory(rv_ratio, stim_time, start_size, end_size):
    # rv_ratio in sec
    time_steps = np.arange(0, stim_time-0.001, 0.001)  # time steps of trajectory
    # calculate angular size at each time step for this rv ratio
    angular_size = 2 * np.rad2deg(np.arctan(rv_ratio * (1 / (stim_time - time_steps))))

    # shift curve vertically so it starts at start_size
    min_size = angular_size[0]
    size_adjust = min_size - start_size
    angular_size = angular_size - size_adjust
    # Cap the curve at end_size and have it just hang there
    max_size_ind = np.where(angular_size > end_size)[0][0]
    angular_size[max_size_ind:] = end_size
    # divide by  2 to get spot radius
    angular_size = angular_size / 2

    return time_steps, angular_size

if __name__ == '__main__':
    main()
