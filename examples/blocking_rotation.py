#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory, Trajectory

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False))

    trajectory = RectangleTrajectory(x=[(0,90),(1,95),(2,95),(3,90),(4,90),(5,90)],
                                     y=[(0,90),(1,90),(2,95),(3,95),(4,90),(5,90)],
                                     angle=Trajectory([(0,45),(2,-45),(4,45),(5,45)], 'zero'), w=5, h=5,
                                     color=0.5)

    manager.load_stim('RotatingBars', angle=0)
    manager.load_stim('MovingPatch', trajectory=trajectory.to_dict(), vary='intensity', background=None, hold=True)

    manager.start_stim()
    sleep(15)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
