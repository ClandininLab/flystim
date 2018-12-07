#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep, time
from random import choice

from flyrpc.launch import launch_server
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from subprocess import Popen, PIPE 

def main(vsync=False):
    num_trials = 60

    manager = launch_stim_server(Screen(width=1, height=1, square_side=1, square_loc='ll', id=1, vsync=vsync))
    manager.black_corner_square()
    fictrac = Popen(('/home/clandininlab/fictrac/bin/fictrac', '/home/clandininlab/fictrac/config2.txt'), stdout=PIPE)

    timestamp_str = None
    recv_time = None
    for line in fictrac.stdout:
        line = line.decode()
        if line.startswith('optimum'):
            recv_time = time()
            manager.white_corner_square()
            sleep(100e-3)
            manager.black_corner_square()
            print('Received command on python side at: {} ms'.format(1e3*recv_time))
            print(line, end='')
            if timestamp_str:
                print(timestamp_str)
        if line.startswith('Timestamp'):
            timestamp_str = line

if __name__ == '__main__':
    main()
