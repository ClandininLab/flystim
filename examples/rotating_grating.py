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

    w = 20.6e-2; h = 12.8e-2; # meters of image at projection plane
    bruker_left_screen = Screen(width=w, height=h, rotation=-pi/2, offset=(4.0e-2, 3.9e-2, -6.1e-2), id=0, fullscreen=False, vsync=True, square_side=0, square_loc='lr')




    #AODscope screen:

    # pt1 = ((1.0, -1.0), (20.1e-3, 46.3e-3, -82.9e-3))
    # pt2 = ((-0.70, -1.0), (20.1e-3, -72.4e-3, -82.9e-3))
    # pt3 = ((-0.70, 1.0), (20.1e-3, -72.4e-3, 12.0e-3))
    # pt4 = ((1.0, 1.0), (20.1e-3, 46.3e-3, 12.0e-3))

    pt2 = ((1.0, -1.0), (20.1e-3, 46.3e-3, -82.9e-3))
    pt1 = ((-0.70, -1.0), (20.1e-3, -72.4e-3, -82.9e-3))
    pt4 = ((-0.70, 1.0), (20.1e-3, -72.4e-3, 12.0e-3))
    pt3 = ((1.0, 1.0), (20.1e-3, 46.3e-3, 12.0e-3))

    tri_list = Screen.quad_to_tri_list(pt1, pt2, pt3, pt4)

    AODscope_screen = Screen(tri_list=tri_list, server_number=1, id=0, fullscreen=False, vsync=True, square_side=5e-3, square_loc='ll')

    draw_screens([AODscope_screen])
    plt.show()

# # # # # # # # # # # # # # # # # # # # #
    manager = launch_stim_server(AODscope_screen)


    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='RotatingGrating', rate=25, period=25, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                      color=[1, 1, 1, 1], cylinder_radius=1.1, cylinder_height=10, theta=180, phi=0, angle=0)

    tv_pairs = [(0, 0), (4, 360)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, 0), (4, 360)]
    angle_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    tv_pairs = [(0, -90), (2, 90)]
    phi_traj = Trajectory(tv_pairs, kind='linear').to_dict()

    manager.load_stim(name='MovingPatch',width=10, height=10, phi=-40, color=0.5, theta=180, hold=True, angle=0)

    # manager.load_stim(name='Tower', color=[1, 0, 0, 1], cylinder_location=[-1, 0, 0],  cylinder_height=1, cylinder_radius=0.5, hold=True) #red +y

    sleep(0.5)

    manager.start_stim()
    sleep(2)

    manager.stop_stim(print_profile=False)
    sleep(0.5)

if __name__ == '__main__':
    main()
