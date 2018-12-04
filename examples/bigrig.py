#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from flystim.stim_server import launch_stim_server
from time import sleep

from math import pi

from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory

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
    elif dir.lower() == 'gui':
        id = 0
        rotation = 0
        offset = (0, w/2, h/2)
        fullscreen = False
    else:
        raise ValueError('Invalid direction.')

    return Screen(id=id, server_number=1, rotation=rotation, width=w, height=h, offset=offset, fullscreen=fullscreen,
                  name='BigRig {} Screen'.format(dir.title()))

def main():
    screens = [get_bigrig_screen(dir) for dir in ['n', 'e', 's', 'w', 'gui']]
    manager = launch_stim_server(screens)
    manager.hide_corner_square()

    trajectory = RectangleTrajectory(x=-45, y=90, angle=0, w=3, h=180)
    kwargs = {'name': 'MovingPatch', 'trajectory': trajectory.to_dict()}
    manager.load_stim(**kwargs)

    manager.start_stim()
    sleep(10)
    manager.stop_stim()

if __name__ == '__main__':
    main()