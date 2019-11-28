#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

from flystim.draw import draw_screens
from flystim.trajectory import Trajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server

from time import sleep

def dir_to_tri_list(dir):
    # set screen width and height
    w = 3.0e-2
    #h = 1

    # set coordinates as a function of direction
    if dir == 'w':
        h = 2.9e-2
        pts = [
            ((+0.563125, -0.32875), (-w/2, -w/2, -h/2)),
            ((+0.563125, -0.66125), (-w/2, +w/2, -h/2)),
            ((+0.354375, -0.66125), (-w/2, +w/2, +h/2)),
            ((+0.354375, -0.32875), (-w/2, -w/2, +h/2))
        ]
    elif dir == 'n':
        h = 3.1e-2
        pts = [
            ((+0.2150, +0.62000), (-w/2, +w/2, -h/2)),
            ((+0.2150, +0.31625), (+w/2, +w/2, -h/2)),
            ((+0.0125, +0.31625), (+w/2, +w/2, +h/2)),
            ((+0.0125, +0.62000), (-w/2, +w/2, +h/2))
        ]

    elif dir == 'e':
        h = 3.2e-2
        pts = [
            ((-0.101875, -0.28500), (+w/2, +w/2, -h/2)),
            ((-0.101875, -0.58875), (+w/2, -w/2, -h/2)),
            ((-0.314375, -0.58875), (+w/2, -w/2, +h/2)),
            ((-0.314375, -0.28500), (+w/2, +w/2, +h/2))
        ]
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(*pts)

def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def main():
    #screen = Screen(fullscreen=False, tri_list=make_tri_list())
    screen = Screen(server_number=1, id=0, fullscreen=False, tri_list=make_tri_list())
    # screen = Screen(server_number=1, id=1, tri_list=make_tri_list())

    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: display a stimulus
    #####################################################



    manager = launch_stim_server(screen)
    manager.load_stim(name='RotatingGrating', angle=90, rate=20, period=20, contrast=1.0, profile='square', cylinder_radius=2)


    tv_pairs = [(0,-90), (5,270)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    manager.load_stim(name='MovingPatch',width=30, height=50, phi=0, color=1, theta=theta_traj, angle=45, hold=True)

    sleep(1)

    manager.start_stim()
    sleep(5)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
