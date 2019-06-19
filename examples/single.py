#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep

#from flyrpc.launch import launch_server
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen


def main():
    stim_type = 'RandomBars'
    duration = 4.0
    
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0))


    print('Press Ctrl-C to quit the program...')

    manager.load_stim(name=stim_type, period=30, vert_extent=30, width=2, rand_min=0.0, rand_max=1.0, start_seed=0,
                  update_rate=60.0, background=0.5, theta_offset = 0)
    manager.start_stim()

    sleep(duration)

    manager.stop_stim()

def freeze():
    while True:
        sleep(1)

if __name__ == '__main__':
    main()
