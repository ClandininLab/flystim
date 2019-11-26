#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep


def main():
    def_screen = Screen(fullscreen=False, server_number = 1, id = 0, vsync=True)

    #AODscope screen:
    pts = [
            ((1.0, 1.0), (20.1e-3, -46.3e-3, 12.0e-3)),
            ((-0.70, 1.0), (20.1e-3, +72.4e-3, 12.0e-3)),
            ((-0.70, -1.0), (20.1e-3, +72.4e-3, -82.9e-3)),
            ((1.0, -1.0), (20.1e-3, -46.3e-3, -82.9e-3))
        ]

    tri_list = Screen.quad_to_tri_list(*pts)
    AODscope_screen = Screen(tri_list=tri_list, server_number=1, id=0, fullscreen=False, vsync=True, square_side=0, square_loc='ll')


    draw_screens([def_screen, AODscope_screen])
    plt.show()

# # # # # # # # # # # # # # # # # # # # #
    manager = launch_stim_server(AODscope_screen)


    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='RotatingGrating', rate=25, period=25, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=0, phi=0, angle=0)

    tv_pairs = [(0, 0), (4, 360)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 45), (4, -45)]
    phi_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='MovingPatch',width=10, height=10, phi=0, color=0.5, theta=0, hold=True, angle=0)

    manager.load_stim(name='Tower', color=[1, 0, 0, 1], cylinder_location=[1, 0, 0],  cylinder_height=1, cylinder_radius=0.5, hold=True) #red +y

    sleep(1)

    manager.start_stim()
    sleep(4)

    manager.stop_stim(print_profile=False)
    sleep(1)

if __name__ == '__main__':
    main()
