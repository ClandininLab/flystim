#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=True))

    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    tv_pairs = [(0, -45), (4, 45)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tf = 2 # Hz
    t = np.linspace(0, 6, 100)
    c = np.sin(2*np.pi*tf*t) + 1
    tv_pairs = list(zip(t, c))
    color_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    # manager.load_stim(name='MovingPatch', width=5, height=10, sphere_radius=1, color=color_traj, theta=theta_traj, phi=0, hold=True)

    manager.load_stim(name='RandomGridOnSphericalPatch', width=40, height=40)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
