#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from time import sleep

from flystim.launch import StimManager
from flystim.screen import Screen

def main():
    screens = [Screen()]
    manager = StimManager(screens)

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
