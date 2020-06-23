#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=True))

    manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)

    manager.load_stim(name='Tower', color=[1, 0, 0, 1.0], cylinder_location=[1, +0.25, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # red
    manager.load_stim(name='Tower', color=[0, 1, 0, 1.0], cylinder_location=[0.5, 0, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # green, +x, center
    manager.load_stim(name='Tower', color=[0, 0, 1, 1], cylinder_location=[1, -0.25, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # blue, +x, right
    #
    tt = np.arange(0, 4, 0.01) # seconds
    velocity_x = 0.25 # meters per sec
    velocity_y = 0.00

    xx = tt * velocity_x
    yy = tt * velocity_y

    # dtheta = 0.0*np.random.normal(size=len(tt))
    dtheta = tt * 0.05
    theta = np.cumsum(dtheta)

    fly_x_trajectory = Trajectory(list(zip(tt, xx))).to_dict()
    fly_y_trajectory = Trajectory(list(zip(tt, yy))).to_dict()
    fly_theta_trajectory = Trajectory(list(zip(tt, theta))).to_dict()
    manager.set_fly_trajectory(fly_x_trajectory,
                               fly_y_trajectory,
                               fly_theta_trajectory)

    sleep(0.5)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
