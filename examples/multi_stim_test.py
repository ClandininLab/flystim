#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=False))

    # rotating grating 1
    manager.load_stim(name='RotatingGrating', angle=0, rate=20, period=20, contrast=0.75, profile='square')
    sleep(1)
    manager.start_stim()
    sleep(6)
    manager.stop_stim(print_profile=True)
    sleep(1)

    for t in range(100):
        # forest
        z_level = -0.2
        # random walk trajectory
        tt = np.linspace(0 ,6, 100)
        dx = -0.1 + 0.02*np.random.normal(size=100) # meters
        dy = 0.01*np.random.normal(size=100) # meters
        dtheta = 1*np.random.normal(size=100) # degrees
        fly_x_trajectory = Trajectory(list(zip(tt, np.cumsum(dx)))).to_dict()
        fly_y_trajectory = Trajectory(list(zip(tt, np.cumsum(dy)))).to_dict()
        fly_theta_trajectory = Trajectory(list(zip(tt, np.cumsum(dtheta)))).to_dict()
        manager.set_fly_trajectory(fly_x_trajectory, fly_y_trajectory, fly_theta_trajectory)
        manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0])
        manager.load_stim(name='Floor', color=[0.25, 0.25, 0.25, 0.0], hold=True, z_level=z_level)

        height = 1.0
        manager.load_stim(name='Tower', color = [1, 0, 0, 0.5], cylinder_height=height, cylinder_radius=0.1, cylinder_location=[2, 0.5, z_level+height/2], hold=True)
        manager.load_stim(name='Tower', color = [0, 1, 0, 0.5], cylinder_height=height, cylinder_radius=0.1, cylinder_location=[-2, 0.5, z_level+height/2], hold=True)
        manager.load_stim(name='Tower', color = [0, 0, 1, 0.5], cylinder_height=height, cylinder_radius=0.1, cylinder_location=[-2, -0.5, z_level+height/2], hold=True)
        manager.load_stim(name='Tower', color = [1, 1, 1, 0.5], cylinder_height=height, cylinder_radius=0.1, cylinder_location=[2, -0.5, z_level+height/2], hold=True)
        n_trees = 20
        for tree in range(n_trees):
            manager.load_stim(name='Tower', color = [0, 0, 0, 0.5], cylinder_height=height, cylinder_radius=0.1, cylinder_location=[np.random.uniform(-20,0), np.random.uniform(-3, 3), z_level+height/2], hold=True)

        sleep(0.5)
        manager.start_stim()
        sleep(1.0)
        manager.stop_stim(print_profile=True)
        sleep(0.5)

    # rotating grating 2
    manager.load_stim(name='RotatingGrating', angle=0, rate=20, period=20, contrast=1.0, profile='square')
    sleep(1)
    manager.start_stim()
    sleep(6)
    manager.stop_stim(print_profile=True)
    sleep(1)


if __name__ == '__main__':
    main()
