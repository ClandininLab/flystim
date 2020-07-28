#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))

    #manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    tv_pairs = [(0, -45), (4, 45)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    occ_tv_pairs = [(0, 0), (4, 0)]
    occ_theta_traj = Trajectory(occ_tv_pairs, kind='linear').to_dict()

    # tv_pairs = [(0, 0), (4, 1)]
    # color_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tf = 2 # Hz
    t = np.linspace(0, 6, 100)
    c = np.sin(2*np.pi*tf*t) + 1
    tv_pairs = list(zip(t, c))
    color_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 1), (4, 45)]
    radius_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    #manager.load_stim(name='MovingSpot', radius=radius_traj, sphere_radius=1, color=color_traj, theta=0, phi=0, hold=True)

    manager.load_stim(name='MovingPatch', width=2, height=60, phi=0, color=1, theta=theta_traj, angle=0, sphere_radius=10.0, hold=True)
    manager.load_stim(name='MovingPatch', width=4, height=60, phi=0, color=0.8, theta=occ_theta_traj, angle=0, sphere_radius=8.0, hold=True)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
