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
    h = 3.0e-2
    # set coordinates as a function of direction
    if dir == 'w':
        pa = ((-0.8, -0.6), (-w/2, -w/2, -h/2))
        pb = ((-0.2, -0.6), (-w/2, +w/2, -h/2))
        pc = ((-0.8, +0.0), (-w/2, -w/2, +h/2))
        p4 = ((-0.2, +0.0), (-w/2, +w/2, +h/2))

    elif dir == 'n':
        pa = ((-0.3, 0.0), (-w/2, +w/2, -h/2))
        pb = ((+0.3, 0.0), (+w/2, +w/2, -h/2))
        pc = ((-0.3, +0.6), (-w/2, +w/2, +h/2))
        p4 = ((+0.3, +0.6), (+w/2, +w/2, +h/2))

    elif dir == 'e':
        pa = ((+0.2, -0.6), (+w/2, +w/2, -h/2))
        pb = ((+0.8, -0.6), (+w/2, -w/2, -h/2))
        pc = ((+0.2, +0.0), (+w/2, +w/2, +h/2))
        p4 = ((+0.8, +0.0), (+w/2, -w/2, +h/2))
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(pa, pb, pc, p4)

def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def main():
    screen = Screen(server_number=0, id=0, fullscreen=False, tri_list=make_tri_list(), square_loc=(0.75, -1.0), square_size=(0.25, 0.25), vsync=True)

    draw_screens(screen)

    manager = launch_stim_server(screen)


    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    manager.load_stim(name='RotatingGrating', rate=25, period=30, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=0, phi=0, angle=90, hold=True)

    tv_pairs = [(0, 0), (4, 360)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='MovingPatch',width=30, height=30, phi=0, color=[1, 0, 0, 1], theta=theta_traj, hold=True, angle=0)

    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
