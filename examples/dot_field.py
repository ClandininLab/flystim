#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=True))

    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

    manager.load_stim(name='MovingDotField', n_points=200, point_size=80, sphere_radius=1, color=[0, 0, 0, 1],
                      speed=60, signal_direction=np.pi/4, coherence=0.0, random_seed=0, hold=True)

    sleep(1)

    manager.start_stim()
    sleep(6)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
