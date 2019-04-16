#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from math import pi

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from flystim.trajectory import RectangleTrajectory, Trajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server

from time import sleep

def dir_to_tri_list(dir):
    w = 1
    h = 1

    if dir.lower() in ['w', 'west']:
        rotation = pi/2
        offset = (-w/2, 0, 0)
        ll_ndc = (-0.6, -0.6)
        ul_ndc = (-0.6, -0.2)
        ur_ndc = (-0.2, -0.2)
        lr_ndc = (-0.2, -0.6)
    elif dir.lower() in ['n', 'north']:
        rotation = 0
        offset = (0, w/2, 0)
        ll_ndc = (-0.6, +0.2)
        ul_ndc = (-0.6, +0.6)
        ur_ndc = (-0.2, +0.6)
        lr_ndc = (-0.2, +0.2)
    elif dir.lower() in ['e', 'east']:
        rotation = -pi/2
        offset = (w/2, 0, 0)
        ll_ndc = (+0.2, +0.2)
        ul_ndc = (+0.2, +0.6)
        ur_ndc = (+0.6, +0.6)
        lr_ndc = (+0.6, +0.2)
    else:
        raise ValueError('Invalid direction.')

    return Screen.compute_tri_list(width=w, height=h, offset=offset, rotation=rotation, ll_ndc=ll_ndc, ul_ndc=ul_ndc,
                                   ur_ndc=ur_ndc, lr_ndc=lr_ndc)

def make_tri_list():
    tri_list = []

    tri_list += dir_to_tri_list('w')
    tri_list += dir_to_tri_list('n')
    tri_list += dir_to_tri_list('e')

    return tri_list


def main():
    screen = Screen(fullscreen=False, tri_list=make_tri_list())

    # part 1: draw the screen configuration

    fig = plt.figure()
    ax = Axes3D(fig)
    screen.draw(ax=ax)

    # draw fly in the center
    ax.scatter(0, 0, 0, c='g')

    #plt.show()

    # part 2: display a stimulus

    manager = launch_stim_server(screen)

    trajectory = RectangleTrajectory(x=[(0,0),(10,360)], y=90, w=30, h=180)

    manager.load_stim(name='MovingPatch', trajectory=trajectory.to_dict())
    sleep(1)

    manager.start_stim()
    sleep(5)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
