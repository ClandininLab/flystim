#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep

    
def get_subscreen(dir):
    # Define screen(s) for the rig. Units in meters
    # Fly is at (0, 0, 0), fly looking down +y axis.
    z_bottom  = -27.25e-2 #m
    z_top     = +27.25e-2
    x_left    = -15.25e-2
    x_right   = +15.25e-2
    y_forward = +15.25e-2
    y_back    = -15.25e-2
    
    if dir == 'l':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_left, y_back,    z_bottom)
        pb = (x_left, y_forward, z_bottom)
        pc = (x_left, y_back,    z_top)

    elif dir == 'c':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_left,  y_forward, z_bottom)
        pb = (x_right, y_forward, z_bottom)
        pc = (x_left,  y_forward, z_top)

    elif dir == 'r':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_right, y_forward, z_bottom)
        pb = (x_right, y_back,    z_bottom)
        pc = (x_right, y_forward, z_top)

    elif dir == 'aux':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_left,  y_forward, z_bottom)
        pb = (x_right, y_forward, z_bottom)
        pc = (x_left,  y_forward, z_top)

    else:
        raise ValueError('Invalid direction.')

    return SubScreen(pa=pa, pb=pb, pc=pc, viewport_ll=viewport_ll, viewport_width=viewport_width, viewport_height=viewport_height)

def main():
    left_screen = Screen(subscreens=[get_subscreen('l')], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.1, 0.1), square_loc=(1, -1), name='Left', horizontal_flip=False)

    center_screen = Screen(subscreens=[get_subscreen('c')], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.1, 0.1), square_loc=(-1, -1), name='Center', horizontal_flip=False)

    right_screen = Screen(subscreens=[get_subscreen('r')], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.1, 0.122), square_loc=(-1, -1), name='Right', horizontal_flip=False)

    aux_screen = Screen(subscreens=[get_subscreen('aux')], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

    draw_screens([left_screen, center_screen, right_screen])
    plt.show()

    screens = [left_screen, center_screen, right_screen, aux_screen]

    manager = launch_stim_server(screens)

    manager.black_corner_square()
    manager.set_idle_background(0)
    
    
    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    manager.load_stim(name='RotatingGrating', rate=25, period=30, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=0, phi=0, angle=90, hold=True)

    tv_pairs = [(0, 0), (4, 360)]
    theta_traj = {'name': 'tv_pairs',
                  'tv_pairs': tv_pairs,
                  'kind': 'linear'}

    manager.load_stim(name='MovingPatch', width=30, height=30, phi=0, color=[1, 0, 0, 0.5], theta=theta_traj, hold=True, angle=0)

    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=True)
    sleep(0.5)
    
    manager.black_corner_square()
    manager.set_idle_background(0)
if __name__ == '__main__':
    main()
