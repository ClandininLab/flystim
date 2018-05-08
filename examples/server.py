#!/usr/bin/env python3

# Example server program for one screen.
# Please start this program first before launching client.py.  You can exit the server by pressing Ctrl+C.

# In order to display perspective-corrected stimuli, you will need to modify this program so that the Screen
# object is instantiated with the right screen dimensions, and you should also set fullscreen=True.

from flystim.launch import launch
from flystim.screen import Screen

def main(port=62632):
    screens = [Screen(fullscreen=False)]
    launch(screens=screens, port=port)

if __name__ == '__main__':
    main()