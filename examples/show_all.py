#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from time import sleep

from flystim.launch import StimManager, StimClient
from flystim.screen import Screen

def main(use_server=True):
    if use_server:
        manager = StimClient()
    else:
        screens = [Screen()]
        # Define screen(s) for the rig you use
        w = 14.2e-2; h = 9e-2; # meters of image at projection plane, screen only shows 9x9 of this
        zDistToScreen = 5.36e-2; # meters
        screens = [Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=2, fullscreen=True, vsync=None,
	         square_side=5e-2, square_loc='lr'),
	        Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=1, fullscreen=True, vsync=None,
	         square_side=5e-2, square_loc='ll')]
    
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
