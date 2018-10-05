#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep

from flyrpc.launch import launch_server
import flystim.stim_server

def main():
    stim_type = 'Checkerboard'
    should_freeze = False
    duration = 4.0

    manager = launch_server(flystim.stim_server, setup_name='macbook')

    print('Press Ctrl-C to quit the program...')
    while True:
        manager.load_stim(name=stim_type)
        manager.start_stim()

        if should_freeze:
            freeze()
        else:
            sleep(duration)
            manager.stop_stim()

def freeze():
    while True:
        sleep(1)

if __name__ == '__main__':
    main()
