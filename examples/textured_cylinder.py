#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0))


    manager.load_stim(name='RotatingBars', angle=45, rate=40)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
