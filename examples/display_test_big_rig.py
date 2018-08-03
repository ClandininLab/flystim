from time import sleep

from flystim.launch import StimManager, StimClient
from flystim.screen import Screen
from math import pi

# 1: west
# 2: north
# 3: south
# 4: east

def main(use_server=False):
    w = 43*2.54e-2
    h = 24*2.54e-2

    if use_server:
        manager = StimClient()
    else:
        screens = [Screen(id=1, rotation=pi/2, width=w, height=h, offset=(-w/2, 0, h/2)),
                   Screen(id=2, rotation=0, width=w, height=h, offset=(0, w/2, h/2)),
                   Screen(id=3, rotation=pi, width=w, height=h, offset=(0, -w/2, h/2)),
                   Screen(id=4, rotation=-pi/2, width=w, height=h, offset=(w/2, 0, h/2))]
        manager = StimManager(screens)

    manager.load_stim(name='Checkerboard', theta_period=6, phi_period=6)
    manager.start_stim()
    manager.hide_corner_square()

if __name__ == '__main__':
    main()