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

    tv_pairs = [(0, -45), (4, 45)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 45), (4, -45)]
    phi_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    manager.load_stim(name='MovingPatch', width=20, height=5, phi=phi_traj, color=1, theta=theta_traj, hold=True, angle=0, sphere_radius=1.0)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
