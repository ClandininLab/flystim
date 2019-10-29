#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
import numpy as np

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    # rotating grating
    manager.load_stim(name='RotatingGrating', angle=0, rate=20, period=20, contrast=0.75, profile='square')

    sleep(1)

    manager.start_stim()
    sleep(6)

    manager.stop_stim(print_profile=False)
    sleep(1)

if __name__ == '__main__':
    main()
