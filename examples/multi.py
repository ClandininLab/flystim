#!/usr/bin/env python3

# Example client program that walks through all available stimuli
# MultiCall is modeled after xmlrpclib.MultiCall

from time import sleep

import flystim.stim_server

from flyrpc.launch import launch_server
from flyrpc.multicall import MyMultiCall

def main():
    manager = launch_server(flystim.stim_server, setup_name='macbook')

    stims = ['SineGrating', 'RotatingBars', 'ExpandingEdges', 'SequentialBars', 'RandomBars',
             'RandomGrid', 'Checkerboard', 'MovingPatch']

    for stim in stims:

        multicall = MyMultiCall(manager)
        multicall.load_stim(stim)
        multicall.start_stim()
        multicall.start_corner_square()
        multicall()

        sleep(2.5)

        multicall = MyMultiCall(manager)
        multicall.stop_stim()
        multicall.black_corner_square()
        multicall()

        sleep(1)

if __name__ == '__main__':
    main()
