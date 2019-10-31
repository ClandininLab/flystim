#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
import numpy as np

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    manager.load_stim(name='Checkerboard', patch_width=10, patch_height=2, vert_extent = 120,
                  color=[1, 1, 1, 1], angle=0.0, cylinder_radius=2)

    manager.load_stim(name='MovingSpot', radius=5, hold=True)

    manager.set_global_fly_pos(+0,0,0)

    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=False)
    sleep(0.5)

if __name__ == '__main__':
    main()
