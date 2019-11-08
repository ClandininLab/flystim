#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
import numpy as np

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    # contrast-reversing grating
    tf = 1 #Hz
    t = np.linspace(0,6,100)
    c = np.sin(2*np.pi*tf*t)
    tv_pairs = list(zip(t, c))
    contrast_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='CylindricalGrating', angle=0, period=20, contrast=contrast_traj, profile='square')

    sleep(1)

    manager.start_stim()
    sleep(3)

    manager.stop_stim(print_profile=False)
    sleep(1)

if __name__ == '__main__':
    main()
