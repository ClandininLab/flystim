#!/usr/bin/env python3


import json
from flystim.stim_server import launch_stim_server
from time import sleep

from random import choice
from math import pi

from flystim.screen import Screen
from flyrpc.multicall import MyMultiCall
from flystim.trajectory import Trajectory

import os, os.path

def get_bigrig_screen(dir):
    w = 43 * 2.54e-2
    h = 24 * 2.54e-2

    if dir.lower() in ['w', 'west']:
        id = 1
        rotation = pi/2
        offset = (-w/2, 0, h/2)
        fullscreen = True
    elif dir.lower() in ['n', 'north']:
        id = 3
        rotation = 0
        offset = (0, w/2, h/2)
        fullscreen = True
    elif dir.lower() in ['s', 'south']:
        id = 2
        rotation = pi
        offset = (0, -w/2, h/2)
        fullscreen = True
    elif dir.lower() in ['e', 'east']:
        id = 4
        rotation = -pi/2
        offset = (w/2, 0, h/2)
        fullscreen = True
    else:
        raise ValueError('Invalid direction.')

    return Screen(id=id, server_number=1, rotation=rotation, width=w, height=h, offset=offset, fullscreen=fullscreen,
                  name='BigRig {} Screen'.format(dir.title()))

def main():
    screens = [get_bigrig_screen(dir) for dir in ['n', 'e', 's', 'w']]
    manager = launch_stim_server(screens)
    manager.hide_corner_square()

    angles = [
        ('east', 0),
        ('north', 90),
        ('west', 180),
        ('south', 270)
    ]

    for name, value in angles:

        tv_pairs = [(0, value), (10, value)]
        theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()
        manager.load_stim(name='MovingPatch',width=30, height=180, phi=0, color=1, theta=theta_traj)

        print(f'{name} ({value} deg)')

        sleep(5)

if __name__ == '__main__':
    main()
