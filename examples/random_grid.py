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

    manager.load_stim(name='ConstantBackground', color=[1,1,1,1])

    manager.load_stim(name='RandomGrid', patch_width=10, patch_height=10, start_seed=0, update_rate=5,
                  distribution_data=distribution_data, color=[1, 1, 1, 1.0], angle=0.0, cylinder_radius=2, cylinder_height=10, hold=True)

    manager.load_stim(name='MovingSpot', radius=10, phi=0, color=[1,1,1,1.0], hold=True)

    manager.set_global_fly_pos(+0,0,0)

    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=False)
    sleep(0.5)

if __name__ == '__main__':
    main()
