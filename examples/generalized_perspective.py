#!/usr/bin/env python3
""" Test generalized perspective transform
"""

from math import radians

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    screen = Screen(
        fullscreen=False,
        server_number=1,
        screen_id=0,
        vsync=True,
        azimuth=radians(0),
        offset=(0, 0, -0.3)
    )

    print(screen.tri_list[0])
    print(screen.tri_list[1])
    manager = launch_stim_server(screen)

    manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)

    # red, -x, left
    manager.load_stim(
        name='Tower',
        color=[1, 0, 0, 1],
        cylinder_location=[-0.25, 0, -1],
        cylinder_height=0.1,
        cylinder_radius=0.05,
        hold=True
    )
    # green, +y, center
    manager.load_stim(
        name='Tower',
        color=[0, 1, 0, 1],
        cylinder_location=[0, 0.25, -1],
        cylinder_height=0.1,
        cylinder_radius=0.05,
        hold=True
    )
    # blue, +x, right
    manager.load_stim(
        name='Tower',
        color=[0, 0, 1, 1],
        cylinder_location=[0.25, 0, -1],
        cylinder_height=0.1,
        cylinder_radius=0.05,
        hold=True
    )

    tt = np.arange(0, 10, 0.01) # seconds
    velocity_x = 0.0 # meters per sec
    velocity_y = 0.0
    velocity_z = -0.02

    xx = tt * velocity_x
    yy = tt * velocity_y
    zz = tt * velocity_z

    theta = tt * 0


    fly_x_trajectory = Trajectory(list(zip(tt, xx))).to_dict()
    fly_y_trajectory = Trajectory(list(zip(tt, yy))).to_dict()
    fly_z_trajectory = Trajectory(list(zip(tt, zz))).to_dict()
    fly_theta_trajectory = Trajectory(list(zip(tt, theta))).to_dict()
    manager.set_fly_trajectory(fly_x_trajectory,
                               fly_y_trajectory,
                               fly_z_trajectory,
                               fly_theta_trajectory)


    # distribution_data = {'name': 'Gaussian',
    #                      'args': [],
    #                      'kwargs': {'rand_mean': 0.5,
    #                                 'rand_stdev': 0.3}}

    # manager.load_stim(name='RandomGrid', patch_width=5, patch_height=5, start_seed=0, update_rate=5.0,
    #                   distribution_data=distribution_data, color=[1, 1, 1, 1], angle=15,
    #                   cylinder_radius=2, cylinder_vertical_extent=20, cylinder_angular_extent=20, theta=90, phi=0, hold=True)
    sleep(0.5)

    manager.start_stim()
    sleep(10)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
