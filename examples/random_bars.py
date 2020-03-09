#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    distribution_data = {'name': 'Binary',
                         'args': [],
                         'kwargs': {'rand_min': 0.0,
                                    'rand_max': 0.0}}

    manager.load_stim(name='RandomBars', period=25, width=5, vert_extent=20, theta_offset=0, background=0.5,
                     distribution_data=distribution_data, update_rate=60.0, start_seed=0,
                     color=[1, 1, 1, 1], cylinder_radius=1, theta=0, phi=0, angle=0.00)

    sleep(1)

    manager.start_stim()
    sleep(6)

    manager.stop_stim(print_profile=False)
    sleep(1)

if __name__ == '__main__':
    main()
