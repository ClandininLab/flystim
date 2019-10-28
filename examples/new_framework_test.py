#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory

from time import sleep

def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number = 1, id = 0))


    tv_pairs = [(0,1), (0.5,0), (1,1), (1.5,0), (2,1), (2.5,0), (3,1)]
    color_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0,-240), (3, -120)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()


    manager.load_stim(name='MovingPatch',width=20, height=20, phi=0, color=color_traj, theta=theta_traj)

    manager.load_stim(name='MovingPatch',width=20, height=20, phi=-30, color=0.5, theta=-180, hold=True)

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
