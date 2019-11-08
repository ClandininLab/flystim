#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0, vsync=True))

    tv_pairs = [(0,-240), (3, -120)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)

    manager.load_stim(name='MovingPatch',width=20, height=20, phi=30, color=1, theta=theta_traj, hold=True, angle=45)

    manager.load_stim(name='MovingPatch',width=5, height=40, phi=0, color=1.0, theta=-180, hold=True, angle=45)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=True)
    sleep(1)

if __name__ == '__main__':
    main()
