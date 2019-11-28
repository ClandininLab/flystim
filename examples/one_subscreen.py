#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

from flystim.draw import draw_screens
from flystim.trajectory import RectangleTrajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server

from time import sleep

def make_tri_list():
    # set screen width and height
    w = 3.0e-2
    h = 3.8e-2

    # set coordinates as a function of direction
    pts = [
        ((+0.17, +0.62), (-w/2, +w/2, -h/2)),
        ((+0.17, +0.33), (+w/2, +w/2, -h/2)),
        ((-0.03, +0.33), (+w/2, +w/2, +h/2)),
        ((-0.03, +0.62), (-w/2, +w/2, +h/2))
    ]

    return Screen.quad_to_tri_list(*pts)

def main():
    screen = Screen(server_number=1, id=1, tri_list=make_tri_list())

    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    # draw_screens(screen)

    #####################################################
    # part 2: display a stimulus
    #####################################################

    manager = launch_stim_server(screen)

    trajectory = RectangleTrajectory(x=[(0,135),(5,45)], y=90, w=30, h=180)

    manager.load_stim(name='MovingPatch', trajectory=trajectory.to_dict())
    sleep(1)

    manager.start_stim()
    sleep(5)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
