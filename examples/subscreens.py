#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep

def get_subscreen(dir):
    '''
    Tuned for ballrig with "rotate left" in /etc/X11/xorg.conf
    Because screens are flipped l<->r, viewport_ll is actually lower right corner.
    '''
    north_w = 2.956e-2
    side_w = 2.96e-2

    # set coordinates as a function of direction
    if dir == 'w':
       # set screen width and height
       h = 3.10e-2
       pa = (-north_w/2, -side_w/2, -h/2)
       pb = (-north_w/2, +side_w/2, -h/2)
       pc = (-north_w/2, -side_w/2, +h/2)
       viewport_ll = (-0.636, -0.5)
       viewport_width = -0.636 - (-0.345)
       viewport_height = -0.289 - (-0.5)
    elif dir == 'n':
       # set screen width and height
       h = 3.29e-2
       pa = (-north_w/2, +side_w/2, -h/2)
       pb = (+north_w/2, +side_w/2, -h/2)
       pc = (-north_w/2, +side_w/2, +h/2)
       viewport_ll = (+0.2956, -0.1853)
       viewport_width = +0.2956 - 0.5875
       viewport_height = +0.015 - (-0.1853)
    elif dir == 'e':
        # set screen width and height
        h = 3.40e-2
        pa = (+north_w/2, +side_w/2, -h/2)
        pb = (+north_w/2, -side_w/2, -h/2)
        pc = (+north_w/2, +side_w/2, +h/2)
        viewport_ll = (-0.631, +0.135)
        viewport_width = -0.631 - (-0.355)
        viewport_height = +0.3397- (+0.135)
    else:
        raise ValueError('Invalid direction.')

    return SubScreen(pa=pa, pb=pb, pc=pc, viewport_ll=viewport_ll, viewport_width=abs(viewport_width), viewport_height=abs(viewport_height))


def main():
    subscreens = [get_subscreen('w'), get_subscreen('n'), get_subscreen('e')]
    screen = Screen(subscreens=subscreens, server_number=1, id=1, fullscreen=True, square_loc=(0.75, -1.0), square_size=(0.25, 0.25), vsync=True, horizontal_flip=True)

    #draw_screens(screen)

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
