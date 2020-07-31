#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np
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

    # manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))
    manager = launch_stim_server(screen)

    manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)
    manager.load_stim(name='Floor', color=[0.5, 0.5, 0.5, 1.0], z_level=-0.1, side_length=5, hold=True)

    manager.load_stim(name='Tower', color=[1, 0, 0, 1.0], cylinder_location=[-0.25, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # red, +y, left
    manager.load_stim(name='Tower', color=[0, 1, 0, 1.0], cylinder_location=[0.0, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # green, +y, center
    manager.load_stim(name='Tower', color=[0, 0, 1, 1], cylinder_location=[+0.25, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # blue, +y, right


    tree_locations = []
    for tree in range(40):
        tree_locations.append([np.random.uniform(-2, 2), np.random.uniform(-2, 2), np.random.uniform(0, 0)])
    manager.load_stim(name='Forest', color=[0, 0, 0, 1], cylinder_radius=0.05, cylinder_height=0.1, n_faces=8, cylinder_locations=tree_locations, hold=True)

    tt = np.arange(0, 12, 0.01) # seconds
    velocity_x = 0.00 # meters per sec
    velocity_y = 0.1

    xx = tt * velocity_x
    yy = tt * velocity_y

    # dtheta = 0.0*np.random.normal(size=len(tt))
    dtheta = tt * 0.0
    theta = np.cumsum(dtheta)

    fly_x_trajectory = Trajectory(list(zip(tt, xx))).to_dict()
    fly_y_trajectory = Trajectory(list(zip(tt, yy))).to_dict()
    fly_theta_trajectory = Trajectory(list(zip(tt, theta))).to_dict()
    manager.set_fly_trajectory(fly_x_trajectory,
                               fly_y_trajectory,
                               fly_theta_trajectory)

    sleep(0.5)

    manager.start_stim()
    sleep(16)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
