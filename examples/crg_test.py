#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False))

    
    manager.load_stim(name='MovingPatch', background = 0.5, trajectory=RectangleTrajectory(w = 0, h = 0).to_dict())
    manager.load_stim('ContrastReversingGrating', spatial_period=10, temporal_frequency=1.0, contrast_scale=1.0, mean=0.5, angle=0.0,
                      box_min_x=75, box_max_x=105, box_min_y=75, box_max_y=105, hold = True)

    sleep(1)
    
    manager.start_stim()
    sleep(3)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
