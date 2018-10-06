#!/usr/bin/env python3

# Example client program that displays a patch that is sent on a square trajectory

from time import sleep

import flystim.stim_server
from flystim.trajectory import RectangleTrajectory, Trajectory

from flyrpc.launch import launch_server

def main():
    num_trials = 1

    manager = launch_server(flystim.stim_server, setup_name='macbook')

    trajectory = RectangleTrajectory(x=[(0,90),(1,95),(2,95),(3,90),(4,90),(5,90)],
                                     y=[(0,90),(1,90),(2,95),(3,95),(4,90),(5,90)],
                                     angle=Trajectory([(0,45),(2,-45),(4,45),(5,45)], 'zero'))

    for _ in range(num_trials):
        manager.load_stim(name='MovingPatch', trajectory=trajectory.to_dict())
        sleep(550e-3)

        manager.start_stim()
        sleep(6)

        manager.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
