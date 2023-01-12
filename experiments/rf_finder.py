
#!/usr/bin/env python3
import sys
import os
from flystim.root_stimuli import NaturalMovie, WhiteNoise
import random_word
import cv2
import threading

import keyboard

from flystim.stim_server import launch_stim_server 
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens
# from flystim.util import get_video_dim, get_baccus_subscreen

from flystim.experiments import init_screens, get_video_dim
from time import sleep as idle
import time


def main():
    experiment_name = os.path.splitext(os.path.basename(__file__))[0]

    if os.path.exists('/home/baccuslab/logs/{}_log.txt'.format(experiment_name)):
        resp = input('WARNING: {} log already exists. Delete it and continue? (y/n)'.format(experiment_name))
        logfile_path = '/home/baccuslab/logs/{}_log.txt'.format(experiment_name)
        if resp == 'y':
            os.remove('/home/baccuslab/logs/{}_log.txt'.format(experiment_name))
            logfile_path = '/home/baccuslab/logs/{}_log.txt'.format(experiment_name)
        if resp == 'n':
            logfile_path = '/home/baccuslab/logs/temp.txt'
    else:
        logfile_path = '/home/baccuslab/logs/{}_log.txt'.format(experiment_name)

    manager = init_screens()

    manager.black_corner_square()
    manager.set_idle_background(0)
    manager()

    idle(2)
    

    manager.load_stim(name='MovingPatch', width=3, height= 180)
    manager()
    
    # Start the stimulus
    manager.start_stim()
    manager.start_corner_square()
    manager()

    running = True
   
    theta = 0
    speed = 2
    phi = 0
    width = 10.0
    while running:
        if keyboard.is_pressed('left'):
            theta -= speed
        elif keyboard.is_pressed('right'):
            theta += speed
        elif keyboard.is_pressed('1'):
            speed = 0.125
        elif keyboard.is_pressed('2'):
            speed = 0.25
        elif keyboard.is_pressed('3'):
            speed = 0.5
        elif keyboard.is_pressed('4'):
            speed = 1.0
        elif keyboard.is_pressed('5'):
            speed = 2.0
        elif keyboard.is_pressed('6'):
            speed = 4.0
        elif keyboard.is_pressed('7'):
            speed = 8.0
        elif keyboard.is_pressed('q'):
            break
        elif keyboard.is_pressed('space'):
            phi += 1
        
        manager.set_global_theta_offset(theta)
        manager()
        
        idle(0.01)



    # Preload the stop so that extra time isnt taken setting up these calls during the idle period
    # Meanwhile stimulus is running
    manager.stop_stim()
    manager.black_corner_square()
    manager.set_idle_background(0)

    
    manager()
    

    try:
        process.terminate()
    except:
        pass

    idle(INTERVAL)

    del root_stim,process
if __name__ == '__main__':
    main()
