#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))

    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    x_trajectory = {'name': 'tv_pairs',
                    'tv_pairs': [(0, -2), (2, 2)],
                    'kind': 'linear'}
    y_trajectory = {'name': 'tv_pairs',
                    'tv_pairs': [(0, 4), (2, 6)],
                    'kind': 'linear'}
    z_trajectory = {'name': 'tv_pairs',
                    'tv_pairs': [(0, -2), (2, 2)],
                    'kind': 'linear'}

    color_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, (0, 0, 0, 1)), (1, (0, 1, 0, 1)), (2, (0, 1, 1, 1))],
                        'kind': 'linear'}
    
    theta_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, 0), (2, 180)],
                        'kind': 'linear'}
    phi_trajectory   = {'name': 'tv_pairs',
                        'tv_pairs': [(0, 0), (2, 0)],
                        'kind': 'linear'}
    angle_trajectory = {'name': 'tv_pairs',
                        'tv_pairs': [(0, 0), (2, 0)],
                        'kind': 'linear'}

    manager.load_stim(name='MovingBox', x_length=1, y_length=2, z_length=1, color=color_trajectory, 
                                        x=x_trajectory, y=y_trajectory, z=z_trajectory, 
                                        theta=theta_trajectory, phi=phi_trajectory, angle=angle_trajectory, 
                                        hold=True)

    sleep(1)

    manager.start_stim()
    sleep(2)
 
    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
