#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory, Trajectory

from time import sleep, time

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=1))

    manager.load_stim('RotatingBars', angle=0, rate=0)

    manager.start_stim()
    t_start = time()
    while (time() - t_start) < 10:
        sleep(0.01)
        manager.set_global_fly_pos(0, (time() - t_start)*0.02, 0)
        manager.set_global_theta_offset((time() - t_start)*4)

    manager.stop_stim()

if __name__ == '__main__':
    main()
