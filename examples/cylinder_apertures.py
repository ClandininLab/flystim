#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep


def main():
    screen = Screen(fullscreen=False, server_number=0, id=0, vsync=False)

    # draw_screens(screen)

    manager = launch_stim_server(screen)

    # manager.load_stim(name='RotatingGrating', rate=60, period=20, mean=0.5, contrast=1.0, offset=0.0, profile='sine',
    #                 color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=0, phi=0, angle=0, hold=True)

    manager.load_stim(name='MaskOnCylinder', cylinder_radius=20.0, cylinder_height=0.25, color=[1, 1, 1, 1], hold=True)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
