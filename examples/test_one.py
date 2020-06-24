#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
import numpy as np
import sys

from time import sleep

stim_name = sys.argv[1]


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))

    manager.load_stim(name=stim_name)

    sleep(0.25)

    manager.start_stim()
    sleep(2)

    manager.stop_stim(print_profile=True)

if __name__ == '__main__':
    main()
