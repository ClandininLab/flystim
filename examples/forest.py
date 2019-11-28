#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np
import os

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))
    z_level = -0.01

    # random walk trajectory
    tt = np.linspace(0 ,4, 100) #sec
    dx = 0.00 * np.ones(shape=(100,1)) # meters
    dy = -0.000 * np.ones(shape=(100,1)) # meters
    dtheta = 0*np.random.normal(size=100) # degrees

    fly_x_trajectory = Trajectory(list(zip(tt, np.cumsum(dx)))).to_dict()
    fly_y_trajectory = Trajectory(list(zip(tt, np.cumsum(dy)))).to_dict()
    fly_theta_trajectory = Trajectory(list(zip(tt, np.cumsum(dtheta)))).to_dict()

    manager.set_fly_trajectory(fly_x_trajectory, fly_y_trajectory, fly_theta_trajectory)

    base_dir = r'C:\Users\mhturner\Documents\GitHub\visprotocol\resources\mht\images\VH_NatImages'
    fn = 'imk00125.iml'

    manager.set_global_fly_pos(0, 0, 0)
    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0])
    manager.load_stim(name='HorizonCylinder',image_path=os.path.join(base_dir, fn))
    manager.load_stim(name='TexturedGround', color=[0.25, 0.25, 0.25, 1.0], hold=True, z_level=z_level)

    manager.load_stim(name='Tower', color=[1, 1, 1, 1], cylinder_location=[+0.5, +1, 0], cylinder_radius=0.05, hold=True) #white front right
    manager.load_stim(name='Tower', color=[0, 0, 0, 1], cylinder_location=[-0.5, +1, 0], cylinder_radius=0.05, hold=True) #black front left

    manager.load_stim(name='Tower', color=[1, 0, 0, 1], cylinder_location=[0, 1, 0], cylinder_radius=0.05, hold=True) #red +y
    manager.load_stim(name='Tower', color=[0, 1, 0, 1], cylinder_location=[0, -1, 0], cylinder_radius=0.2, hold=True) #green -y
    manager.load_stim(name='Tower', color=[0, 0, 1, 1], cylinder_location=[1, 0, 0], cylinder_radius=0.2, hold=True) # blue +x
    manager.load_stim(name='Tower', color=[1, 1, 1, 1], cylinder_location=[-1, 0, 0], cylinder_radius=0.2, hold=True) # white -x

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
