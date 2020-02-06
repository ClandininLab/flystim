#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

from flystim.draw import draw_screens
from flystim.trajectory import RectangleTrajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server

from time import sleep, time
import numpy as np
import math
import socket
import os, subprocess

import matplotlib.pyplot as plt

def dir_to_tri_list(dir):

    north_w = 3.0e-2
    side_w = 2.96e-2

    # set coordinates as a function of direction
    if dir == 'w':
       # set screen width and height
       h = 2.94e-2
       pts = [
            ((+0.4602, -0.3159), (-north_w/2, -side_w/2, -h/2)),
            ((+0.4502, -0.6347), (-north_w/2, +side_w/2, -h/2)),
            ((+0.2527, -0.6234), (-north_w/2, +side_w/2, +h/2)),
            ((+0.2527, -0.3034), (-north_w/2, -side_w/2, +h/2))
        ]
    elif dir == 'n':
       # set screen width and height
       h = 3.29e-2
       pts = [
            ((+0.1295, +0.6278), (-north_w/2, +side_w/2, -h/2)),
            ((+0.1297, +0.3233), (+north_w/2, +side_w/2, -h/2)),
            ((-0.0675, +0.3213), (+north_w/2, +side_w/2, +h/2)),
            ((-0.0675, +0.6175), (-north_w/2, +side_w/2, +h/2))
        ]

    elif dir == 'e':
        # set screen width and height
        h = 3.18e-2
        pts = [
            ((-0.1973, -0.2634), (+north_w/2, +side_w/2, -h/2)),
            ((-0.1873, -0.5509), (+north_w/2, -side_w/2, -h/2)),
            ((-0.3986, -0.5734), (+north_w/2, -side_w/2, +h/2)),
            ((-0.4023, -0.2791), (+north_w/2, +side_w/2, +h/2))
        ]
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(*pts)

def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def fictrac_get_data(sock):
    data = sock.recv(1024)
    #if not data:
    #    break

    # Decode received data
    line = data.decode('UTF-8')
    endline = line.find("\n")
    line = line[:endline]
    toks = line.split(", ")

    # Fixme: sometimes we read more than one line at a time,
    # should handle that rather than just dropping extra data...
    if ((len(toks) < 26) | (toks[0] != "FT")):
        #print('Bad read')
        return fictrac_get_data(sock)
        #continue

    #dr_lab = [float(toks[6]), float(toks[7]), float(toks[8])]

    posx = float(toks[15])
    posy = float(toks[16])
    heading = float(toks[17])
    timestamp = float(toks[22])
    sync_illum = int(toks[24])
    sync_mean = float(toks[25])

    return (posx, posy, heading, timestamp, sync_illum, sync_mean)


def main():
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), \
                    square_side=0.08, square_loc='ur', square_toggle_prob=0.1, save_square_history=True)
    print(screen)

    FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
    FICTRAC_PORT = 33334         # The port used by the server
    RADIUS = 0.0045 # in meters; i.e. 4.5mm

    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: display a stimulus
    #####################################################


    manager = launch_stim_server(screen)

    stim_length = 11 #sec
    speed = 0 #degrees per sec
    still_duration = 1 #seconds
    sample_period = 6 #seconds
    occlusion_period = 2 #seconds
    trajectory = RectangleTrajectory(x=[(0,90),(still_duration,90),(stim_length, 90-speed*(stim_length-still_duration))], y=90, w=2, h=60)
    occluder = RectangleTrajectory(x=[(0,90-speed*(still_duration+sample_period)),(stim_length,90-speed*(still_duration+sample_period))], y=90, w=occlusion_period*speed, h=70)
    stim_length = 11 #sec
    still_duration = 1 #seconds

    manager.load_stim('MovingPatch', trajectory=trajectory.to_dict(), background=None)

    manager.start_stim()
    sleep(1)
    print('set_theta_off_set!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    for i in range(10000):
        theta_deg = i % 360 - 360
        manager.set_global_theta_offset(theta_deg)
        sleep(0.001)
    sleep(5)
    manager.stop_stim()


if __name__ == '__main__':
    main()
