#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)
    manager.load_stim(name='Tower', color=[1, 0, 0, 1], cylinder_location=[1, 0, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) #red +x
    manager.load_stim(name='Tower', color=[0, 1, 0, 1], cylinder_location=[0.8, 0.2, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) #green left

    manager.load_stim(name='Tower', color=[0, 0, 1, 1], cylinder_location=[0.8, -0.2, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) #blue right

    tv_pairs = [(0, 0), (4, 0.5)]
    x_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 0), (4, 0)]
    y_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 0), (4, 0)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    theta = 0
    phi = 0
    manager.set_global_phi_offset(phi)
    manager.set_global_theta_offset(theta)

    manager.set_global_fly_pos(-0.5, 0, 0)

    # manager.set_fly_trajectory(x_trajectory=x_traj,
    #                            y_trajectory=y_traj,
    #                            theta_trajectory=theta_traj)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
