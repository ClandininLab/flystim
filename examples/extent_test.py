#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory, Trajectory

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False))

    manager.load_stim('RotatingBars', angle=0, rate=-10)
    manager.load_stim('RotatingBars', angle=0, box_min_x=85, box_max_x=95, box_min_y=85, box_max_y=95, hold=True)

    manager.start_stim()
    sleep(5)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
