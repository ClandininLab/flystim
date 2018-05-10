#!/usr/bin/env python3

# Example server program for one screen.
# Please start this program first before launching client.py.  You can exit the server by pressing Ctrl+C.

# In order to display perspective-corrected stimuli, you will need to modify this program so that the Screen
# object is instantiated with the right screen dimensions, and you should also set fullscreen=True.

from flystim.launch import launch
from flystim.screen import Screen

def main(port=62632):
    # screens = [Screen(fullscreen=False)]
    w = 14.2e-2; h = 9e-2; # cm of image at projection plane, screen only shows 9x9 of this
    zDistToScreen = 5.36e-2; # cm

    pa = [-w/2, -h, -zDistToScreen]; # lower left
    pb = [ w/2, -h, -zDistToScreen]; # lower right
    pc = [-w/2, 0, -zDistToScreen]; # upper left
    # screens = [Screen(fullscreen=True, id = 1, pa=pa, pb=pb, pc=pc),Screen(fullscreen=True, id = 2, pa=pa, pb=pb, pc=pc)]
    screens = [Screen(fullscreen=True, id = 1, pa=pa, pb=pb, pc=pc)]
    launch(screens=screens, port=port)

if __name__ == '__main__':
    main()
