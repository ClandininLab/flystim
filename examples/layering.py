#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)
    manager.load_stim(name='Tower', color=[1, 0, 0, 1], cylinder_location=[1, +0.25, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # red, +x, left
    manager.load_stim(name='Tower', color=[0, 1, 0, 1], cylinder_location=[1, 0, 0.25],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # green, +x, center
    manager.load_stim(name='Tower', color=[0, 0, 1, 1], cylinder_location=[1, -0.25, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # blue, +x, right

    tt = np.arange(0, 4, 0.01) # seconds
    velocity_x = 0.02 # meters per sec
    velocity_y = 0.00

    xx = tt * velocity_x
    yy = tt * velocity_y

    dtheta = 0.0*np.random.normal(size=len(tt))
    theta = np.cumsum(dtheta)

    fly_x_trajectory = Trajectory(list(zip(tt, xx))).to_dict()
    fly_y_trajectory = Trajectory(list(zip(tt, yy))).to_dict()
    fly_theta_trajectory = Trajectory(list(zip(tt, theta))).to_dict()
    manager.set_fly_trajectory(fly_x_trajectory,
                               fly_y_trajectory,
                               fly_theta_trajectory)


    distribution_data = {'name': 'Gaussian',
                         'args': [],
                         'kwargs': {'rand_mean': 0.5,
                                    'rand_stdev': 0.3}}

    # manager.load_stim(name='RandomGrid', patch_width=5, patch_height=5, start_seed=0, update_rate=5.0,
    #                   distribution_data=distribution_data, color=[1, 1, 1, 1], angle=15,
    #                   cylinder_radius=2, cylinder_vertical_extent=20, cylinder_angular_extent=20, theta=90, phi=0, hold=True)

    tv_pairs = [(0,0), (4, 180)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    manager.load_stim(name='MovingPatch',width=10, height=10, phi=0, color=1, theta=90, hold=True, angle=0)
    sleep(0.5)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
