#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep


def main():
    # Define screen(s) for the rig
    w = 20.6e-2; h = 12.8e-2; # meters of image at projection plane

    def_screen = Screen(fullscreen=False, server_number = 1, id = 0, vsync=True)
    aux_screen = Screen(width=w, height=h, rotation=pi-pi/4, offset=(4.0e-2, 3.9e-2, -6.1e-2), id=0, fullscreen=False, vsync=True, square_side=0)

    # draw_screens([aux_screen, def_screen])
    # plt.show()

    manager = launch_stim_server(aux_screen)


    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='RotatingGrating', rate=25, period=25, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=180, phi=0, angle=0)

    tv_pairs = [(0, 180-45), (4, 180+135)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 45), (4, -45)]
    phi_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='MovingPatch',width=5, height=5, phi=-30, color=0.5, theta=225, hold=True, angle=90)

    # manager.load_stim(name='Tower', color=[1, 0, 0, 1], cylinder_location=[0, 1, -0.5],  cylinder_height=3, cylinder_radius=2, hold=True) #red +y

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=False)
    sleep(1)

if __name__ == '__main__':
    main()
