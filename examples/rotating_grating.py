#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep


def dir_to_tri_list(dir):
    w = 3.0e-2
    # set coordinates as a function of direction
    if dir == 'w':
        h = 3e-2
        pts = [
            ((-0.8, -0.6), (-w/2, -w/2, -h/2)), # ll
            ((-0.8, +0.0), (-w/2, +w/2, -h/2)), # ul
            ((-0.2, +0.0), (-w/2, +w/2, +h/2)), # ur
            ((-0.2, -0.6), (-w/2, -w/2, +h/2)) # lr
        ]
    elif dir == 'n':
        h = 3e-2
        pts = [
            ((-0.3, -0.0), (-w/2, +w/2, -h/2)),
            ((-0.3, +0.6), (+w/2, +w/2, -h/2)),
            ((+0.3, +0.6), (+w/2, +w/2, +h/2)),
            ((+0.3, -0.0), (-w/2, +w/2, +h/2))
        ]

    elif dir == 'e':
        h = 3e-2
        pts = [
            ((+0.2, -0.6), (+w/2, +w/2, -h/2)),
            ((+0.2, +0.0), (+w/2, -w/2, -h/2)),
            ((+0.8, +0.0), (+w/2, -w/2, +h/2)),
            ((+0.8, -0.6), (+w/2, +w/2, +h/2))
        ]
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(*pts)

def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def main():
    screen = Screen(server_number=0, id=0, fullscreen=False, tri_list=make_tri_list())

    manager = launch_stim_server(screen)


    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    manager.load_stim(name='RotatingGrating', rate=25, period=30, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=90, phi=0, angle=90, hold=True)

    tv_pairs = [(0, 0), (4, 360)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='MovingPatch',width=30, height=30, phi=0, color=0.5, theta=theta_traj, hold=True, angle=0)

    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=False)
    sleep(0.5)

if __name__ == '__main__':
    main()
