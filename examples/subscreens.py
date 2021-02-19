#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep


def get_subscreen(dir):
    w = 3.0e-2 #meters
    h = 3.0e-2
    viewport_width = 0.6 #ndc
    viewport_height = 0.6
    if dir == 'w':
        viewport_ll = (-0.8, -0.6)
        pa = (-w/2, -w/2, -h/2)
        pb = (-w/2, +w/2, -h/2)
        pc = (-w/2, -w/2, +h/2)

    elif dir == 'n':
        viewport_ll = (-0.3, 0.0)
        pa = (-w/2, +w/2, -h/2)
        pb = (+w/2, +w/2, -h/2)
        pc = (-w/2, +w/2, +h/2)

    elif dir == 'e':
        viewport_ll = (+0.2, -0.6)
        pa = (+w/2, +w/2, -h/2)
        pb = (+w/2, -w/2, -h/2)
        pc = (+w/2, +w/2, +h/2)

    else:
        raise ValueError('Invalid direction.')

    return SubScreen(pa=pa, pb=pb, pc=pc, viewport_ll=viewport_ll, viewport_width=viewport_width, viewport_height=viewport_height)

def main():
    subscreens = [get_subscreen('w'), get_subscreen('n'), get_subscreen('e')]
    screen = Screen(subscreens=subscreens, server_number=0, id=0, fullscreen=False, square_loc=(0.75, -1.0), square_size=(0.25, 0.25), vsync=True)

    draw_screens(screen)

    manager = launch_stim_server(screen)

    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    manager.load_stim(name='RotatingGrating', rate=25, period=30, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=0, phi=0, angle=90, hold=True)

    tv_pairs = [(0, 0), (4, 360)]
    theta_traj = {'name': 'tv_pairs',
                  'tv_pairs': tv_pairs,
                  'kind': 'linear'}

    manager.load_stim(name='MovingPatch', width=30, height=30, phi=0, color=[1, 0, 0, 1], theta=theta_traj, hold=True, angle=0)

    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
