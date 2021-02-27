#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
import numpy as np
from flystim.draw import draw_screens
import flyrpc.multicall

from time import sleep

"""
Demonstrates:
1) subscreens with different screen geometry and viewports
2) synchronizing load/start calls with multicall objects
3) applying fly trajectory
"""

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

    # draw_screens(screen)

    manager = launch_stim_server(screen)
    manager.black_corner_square() # turn off square as server starts up

    num_trials = 5
    pre_time = 1 #sec
    stim_time = 4 #sec
    tail_time = 1 #sec
    for rep in range(num_trials):

        # (1) LOAD STIMS
        multicall_load = flyrpc.multicall.MyMultiCall(manager)

        multicall_load.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)
        multicall_load.load_stim(name='Floor', color=[0.5, 0.5, 0.5, 1.0], z_level=-0.1, side_length=5, hold=True)

        multicall_load.load_stim(name='Tower', color=[1, 0, 0, 1.0], cylinder_location=[-0.25, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # red, +y, left
        multicall_load.load_stim(name='Tower', color=[0, 1, 0, 1.0], cylinder_location=[0.0, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # green, +y, center
        multicall_load.load_stim(name='Tower', color=[0, 0, 1, 1], cylinder_location=[+0.25, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # blue, +y, right


        tree_locations = []
        for tree in range(40):
            tree_locations.append([np.random.uniform(-2, 2), np.random.uniform(-2, 2), np.random.uniform(0, 0)])
        multicall_load.load_stim(name='Forest', color=[0, 0, 0, 1], cylinder_radius=0.05, cylinder_height=0.1, n_faces=8, cylinder_locations=tree_locations, hold=True)

        tt = np.arange(0, 12, 0.01) # seconds
        velocity_x = 0.00 # meters per sec
        velocity_y = 0.1

        xx = tt * velocity_x
        yy = tt * velocity_y

        # dtheta = 0.0*np.random.normal(size=len(tt))
        dtheta = tt * 0.0
        theta = np.cumsum(dtheta)

        fly_x_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(tt, xx)),
                            'kind': 'linear'}
        fly_y_trajectory = {'name': 'tv_pairs',
                            'tv_pairs': list(zip(tt, yy)),
                            'kind': 'linear'}
        fly_theta_trajectory = {'name': 'tv_pairs',
                                'tv_pairs': list(zip(tt, theta)),
                                'kind': 'linear'}
        multicall_load.set_fly_trajectory(fly_x_trajectory, fly_y_trajectory, 0)

        multicall_load() # load stims

        sleep(pre_time)

        # (2) START STIMS, FLICKER CORNER
        multicall_start = flyrpc.multicall.MyMultiCall(manager)
        multicall_start.start_stim()
        multicall_start.start_corner_square()
        multicall_start() #start stims

        sleep(stim_time)

        # (3) STOP STIMS, SET CORNER TO BLACK
        multicall_stop = flyrpc.multicall.MyMultiCall(manager)
        multicall_stop.stop_stim(print_profile=True)
        multicall_stop.black_corner_square()
        multicall_stop()
        sleep(tail_time)

if __name__ == '__main__':
    main()
