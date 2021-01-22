#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep
import itertools
import numpy as np

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleAnyTrajectory, SinusoidalTrajectory

def main():

    n_trials = 1

    iti = 5

    bar_width = 15
    bar_height = 90
    bar_color = 1
    background_color = 0

    screen = Screen(fullscreen=False, vsync=False)
    manager = launch_stim_server(screen)
    manager.set_idle_background(background_color)
    for i in range(n_trials):
        sleep(iti)
        fixbar_traj = RectangleAnyTrajectory(x=SinusoidalTrajectory(amplitude=15, period=1), y=90, w=bar_width, h=bar_height, color=bar_color)
        manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_traj.to_dict(), background=background_color)
        manager.start_stim()
        sleep(10)
        manager.stop_stim()


if __name__ == '__main__':
    main()
