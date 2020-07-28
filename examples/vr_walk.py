#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np
from flystim.draw import draw_screens

from time import sleep

def main():
    w = 0.5
    h = 0.25
    screen = Screen(server_number=0, id=0, fullscreen=False, width=w, height=h, rotation=0, offset=(0, 0.05, 0),
                    square_loc=(0.75, -1.0), square_size=(0.25, 0.25), vsync=True)

    draw_screens(screen)

    manager = launch_stim_server(screen)

    manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)
    manager.load_stim(name='Floor', color=[0.5, 0.5, 0.5, 1.0], z_level=-0.1, side_length=5, hold=True)

    manager.load_stim(name='Tower', color=[1, 0, 0, 1.0], cylinder_location=[-0.25, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # red, +y, left
    manager.load_stim(name='Tower', color=[0, 1, 0, 1.0], cylinder_location=[0.0, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # green, +y, center
    manager.load_stim(name='Tower', color=[0, 0, 1, 1], cylinder_location=[+0.25, +1, 0],  cylinder_height=0.1, cylinder_radius=0.05, hold=True) # blue, +y, right


    tree_locations = []
    for tree in range(40):
        tree_locations.append([np.random.uniform(-2, 2), np.random.uniform(-2, 2), np.random.uniform(0, 0)])
    # manager.load_stim(name='Forest', color=[0, 0, 0, 1], cylinder_radius=0.05, cylinder_height=0.1, n_faces=8, cylinder_locations=tree_locations, hold=True)

    tt = np.arange(0, 12, 0.01) # seconds
    velocity_x = 0.0 # meters per sec
    velocity_y = 0.2

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
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
