#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=1, id=0, vsync=False))

    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    theta_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, -25), (4, 25)],
                        'kind': 'linear'}

    phi_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, 0), (4, 20)],
                        'kind': 'linear'}
    # phi_trajectory = 0

    width_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, 2), (4, 20)],
                        'kind': 'linear'}

    height_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, 30), (4, 3)],
                        'kind': 'linear'}

    # color_trajectory = {'name': 'Sinusoid',
    #                     'temporal_frequency': 2,
    #                     'amplitude': 1,
    #                     'offset': 1}

    color_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, (0, 0, 0, 1)), (1, (0, 0, 0, 0)), (2, (0, 0, 0, 1))],
                        'kind': 'linear'}


    # manager.load_stim(name='MovingPatch', width=width_trajectory, height=height_trajectory, sphere_radius=1, color=color_trajectory, theta=theta_trajectory, phi=phi_trajectory, hold=True)
    # manager.load_stim(name='MovingPatchOnCylinder', width=width_trajectory, height=height_trajectory, cylinder_radius=1, color=color_trajectory, theta=theta_trajectory, phi=phi_trajectory, hold=True)
    manager.load_stim(name='MovingSpot', radius=width_trajectory, sphere_radius=1, color=color_trajectory, theta=theta_trajectory, phi=phi_trajectory, hold=True)
    # manager.load_stim(name='MovingEllipse', width=width_trajectory, height=height_trajectory, sphere_radius=1, color=color_trajectory, theta=theta_trajectory, phi=phi_trajectory, hold=True)
    # manager.load_stim(name='MovingEllipseOnCylinder', width=width_trajectory, height=height_trajectory, cylinder_radius=1, color=color_trajectory, theta=theta_trajectory, phi=phi_trajectory, hold=True)


    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
