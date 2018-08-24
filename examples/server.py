#!/usr/bin/env python3

# Launches a single-screen server for StimManager

from flystim.launch import StimManager, stim_server
from flystim.screen import Screen

def main():
    screens = [Screen()]

    # Define screen(s) for the rig you use
    w = 14.2e-2; h = 9e-2; # meters of image at projection plane, screen only shows 9x9 of this
    zDistToScreen = 5.36e-2; # meters
    screens = [Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=2, fullscreen=True, vsync=None,
	     square_side=5e-2, square_loc='lr'),
	    Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=1, fullscreen=True, vsync=None,
	     square_side=5e-2, square_loc='ll')]

    manager = StimManager(screens)
    stim_server(manager)

if __name__ == '__main__':
    main()
