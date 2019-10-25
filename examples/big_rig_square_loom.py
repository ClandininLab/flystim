#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from time import sleep
from math import pi

from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory, Trajectory
from flystim.stim_server import launch_stim_server

def main(use_server=False):

    manager = launch_stim_server(Screen(fullscreen=False))

    trajectory = RectangleTrajectory(h=[(0,10),(.5,50),(1,10),(1.5,50),(2,10),(2.5,50),(3,10),(3.5,50)],
                                     w=[(0,10),(.5,50),(1,10),(1.5,50),(2,10),(2.5,50),(3,10),(3.5,50)],
                                     x=[(0,0),(.5,0),(1,90),(1.5,90),(2,180),(2.5,180),(3,270),(3.5,270)],
                                     y=[(0,45),(.5,45),(1,45),(1.5,45),(2,45),(2.5,45),(3,45),(3.5,45)],
                                     color=0
                                    )

    manager.hide_corner_square()
    for _ in range(5):
        manager.load_stim(name='MovingPatch', trajectory=trajectory.to_dict(), background=1)
        #manager.load_stim(name='MovingPatch', trajectory=trajectory2.to_dict())
        #sleep(550e-3)

        manager.start_stim()
        sleep(20)

        manager.stop_stim()
        #sleep(500e-3)


if __name__ == '__main__':
    main()
