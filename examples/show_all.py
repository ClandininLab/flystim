#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from flyrpc.launch import launch_server
import flystim.stim_server

from time import sleep

def main():
    manager = launch_server(flystim.stim_server, setup_name='macbook')

    stims = ['SineGrating', 'RotatingBars', 'ExpandingEdges', 'SequentialBars', 'RandomBars',
             'RandomGrid', 'Checkerboard', 'MovingPatch']

    for stim in stims:
        manager.load_stim(stim)
        sleep(500e-3)

        manager.start_stim()
        sleep(2.5)

        manager.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
