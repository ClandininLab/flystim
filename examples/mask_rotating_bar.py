#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory, Trajectory
from flystim.dlpc350 import make_dlpc350_objects
from math import pi, sqrt

from time import sleep

def main():

    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.pattern_mode(fps=115.06)

    if len(dlpc350_objects) == 0:
        print('No lightcrafters detected! Try sudo') 

    w = 14.2e-2
    h = 9e-2
    d = (w/2) * sqrt(2)
    s = (w/2) / sqrt(2)
    eye_correction = -10e-3

    right_screen = Screen(width=w, height=h, rotation=0, offset=(+s+eye_correction, -d + s, -h / 2), id=1, fullscreen=True, vsync=None, square_side=4e-2, square_loc='lr')
    left_screen = Screen(width=w, height=h, rotation=0, offset=(-s-eye_correction, -d + s, -h / 2), id=2, fullscreen=True, vsync=None, square_side=4e-2, square_loc='ll')

    #manager = launch_stim_server(Screen(fullscreen=False))
    screens = [left_screen]
    manager = launch_stim_server(screens)

    trajectory = RectangleTrajectory(x=[(0,90),(10,95),(20,95),(30,90),(40,90),(50,90)],
                                     y=[(0,90),(10,90),(20,95),(30,95),(40,90),(50,90)],
                                     angle=Trajectory([(0,45),(2,-45),(4,45),(5,45)], 'zero'), w=5, h=5,
                                     color=0.0)

    manager.load_stim('RotatingBars', angle=0)
    manager.load_stim('MovingPatch', trajectory=trajectory.to_dict(), vary='alpha', background=0.5, hold=True)

    manager.start_stim()
    sleep(10)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
