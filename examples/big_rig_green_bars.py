#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep

#from flyrpc.launch import launch_server
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen


def main():
    duration = 4.0

    distribution_data = {'name': 'Binary',
                         'args': [],
                         'kwargs': {'rand_min': 0.0,
                                    'rand_max': 0.0}}

    kwargs = {'name': 'RandomBars', 'period': 90, 'width': 20, 'vert_extent': 170, 'background': 0.5,
              'distribution_data': distribution_data, 'update_rate':10.0, 'start_seed':0,
              'color': [0, 1, 0, 1], 'cylinder_radius': 1, 'theta': -20}
    manager = launch_stim_server(Screen(fullscreen=False, server_number=1, id=0))


    print('Press Ctrl-C to quit the program...')

    manager.load_stim(**kwargs)
    manager.start_stim()

    sleep(duration)

    manager.stop_stim()

if __name__ == '__main__':
    main()
