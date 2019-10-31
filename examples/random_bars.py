#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    distribution_data = {'name': 'Gaussian',
                         'args': [],
                         'kwargs': {'rand_mean': 0.5,
                                    'rand_stdev': 0.3}}
    manager.load_stim(name='RandomBars', period=30, width=30, vert_extent=90,
                      start_seed=0, update_rate=60.0,
                      background=0.5, theta_offset=0, distribution_data=distribution_data,
                      color=[1, 1, 1, 1], angle=0.0, cylinder_radius=1)

    manager.set_global_fly_pos(0,0,0)

    sleep(0.5)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=False)
    sleep(0.5)

if __name__ == '__main__':
    main()
