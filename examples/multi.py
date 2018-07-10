#!/usr/bin/env python3

# Example client program that walks through all available stimuli
# MultiCall is modeled after xmlrpclib.MultiCall

from time import sleep

from flystim.launch import StimManager, MultiCall
from flystim.screen import Screen

def main():
    screens = [Screen()]
    manager = StimManager(screens)

    stims = ['SineGrating', 'RotatingBars', 'ExpandingEdges', 'SequentialBars', 'RandomBars',
             'RandomGrid', 'Checkerboard', 'MovingPatch']

    for stim in stims:

        multicall = MultiCall(manager)
        multicall.load_stim(stim)
        multicall.start_stim()
        multicall.start_corner_square()
        multicall()

        sleep(2.5)

        multicall = MultiCall(manager)
        multicall.stop_stim()
        multicall.black_corner_square()
        multicall()

        sleep(1)

if __name__ == '__main__':
    main()
