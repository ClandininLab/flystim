#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
import numpy as np
from flystim.draw import draw_screens

from time import sleep


def main():
    screen = Screen(fullscreen=False, server_number=0, id=0, vsync=True)

    draw_screens(screen)

    manager = launch_stim_server(screen)

    # contrast-reversing grating
    tf = 1 # Hz
    t = np.linspace(0, 6, 100)
    c = np.sin(2*np.pi*tf*t)
    tv_pairs = list(zip(t, c))
    contrast_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='CylindricalGrating', period=10, mean=0.5, contrast=contrast_traj, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1, cylinder_height=10, theta=0, phi=0, angle=0)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
