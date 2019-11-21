#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=1, id=0, vsync=False))

    distribution_data = {'name': 'Gaussian',
                         'args': [],
                         'kwargs': {'rand_mean': 0.5,
                                    'rand_stdev': 0.3}}

    manager.set_global_fly_pos(0,0,0)
    manager.load_stim(name='RandomGrid', patch_width=20, patch_height=5, start_seed=0, update_rate=0,
                      distribution_data=distribution_data, color=[1, 1, 1, 1], angle=0,
                      cylinder_radius=1.0, cylinder_vertical_extent=160, cylinder_angular_extent=180, theta=0, phi=0, hold=True)

    manager.load_stim(name='MovingPatch', width=20, height=10, phi=0, color=1.0, theta=0, hold=True, sphere_radius=0.99)
    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
