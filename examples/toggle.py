#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep, time
from random import choice

from flyrpc.launch import launch_server
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from subprocess import Popen, PIPE

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


def main(vsync=False):
    num_trials = 60

    manager = launch_stim_server(Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), \
                    square_side=0.08, square_loc='ur', square_toggle_prob=0.1, save_square_history=True))
    manager.black_corner_square()

    while True:
        manager.white_corner_square()
        sleep(0.5)
        manager.black_corner_square()
        sleep(0.5)
    
#     fictrac = Popen(('/home/clandininlab/fictrac/bin/fictrac', '/home/clandininlab/fictrac/config2.txt'), stdout=PIPE)

#     timestamp_str = None
#     recv_time = None
#     for line in fictrac.stdout:
#         line = line.decode()
#         if line.startswith('optimum'):
#             recv_time = time()
#             manager.white_corner_square()
#             sleep(100e-3)
#             manager.black_corner_square()
#             print('Received command on python side at: {} ms'.format(1e3*recv_time))
#             print(line, end='')
#             if timestamp_str:
#                 print(timestamp_str)
#         if line.startswith('Timestamp'):
#             timestamp_str = line

# If
if __name__ == '__main__':
    main()
