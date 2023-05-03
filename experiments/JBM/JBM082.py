#!/usr/bin/env python3
import numpy as np
from multiprocessing import shared_memory
import coltrane
import sys
import os
from flystim.root_stimuli import NaturalMovie, WhiteNoise
import random_word
import cv2
import threading

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

    DM1 = '/home/baccuslab/Videos/stimulus_videos/DM1.avi'
    DM2 = '/home/baccuslab/Videos/stimulus_videos/DM2.avi'
    DMTest = '/home/baccuslab/Videos/stimulus_videos/DMTest.avi'

    OF1 = '/home/baccuslab/Videos/stimulus_videos/OF1.avi'#'/home/baccuslab/Videos/stimulus_videos/OF1.avi'
    OF2 = '/home/baccuslab/Videos/stimulus_videos/OF2.avi'
    OFTest = '/home/baccuslab/Videos/stimulus_videos/OFTest.avi'

    INTERVAL= 3

    TRAIN_SEED  = 7
    TEST_SEED = 23

    UPDATE_RATE = 20
    NUM_PIXELS_WIDTH = 180
    NUM_PIXELS_HEIGHT = int((1080/1920) * NUM_PIXELS_WIDTH)

    N_TRAIN=1
    N_TEST=10

    TRAIN_DUR= 60*25
    TEST_DUR = 15


    manager = init_screens()
    
    manager.black_corner_square()
    manager.set_idle_background(0)
    manager.start_stim()
    manager()
    

    

    ############################################################
    # OF Test Repeats
    manager.black_corner_square()
    manager.set_idle_background(0)
    manager()

    manager.set_global_fly_pos(0,0,-0.2) #midline of the stimulus
    idle(INTERVAL)
    
    rwg = random_word.RandomWords()
    memname = rwg.get_random_word()
    import coltrane
    log = coltrane.load_flystim_log('/home/baccuslab/logs/JBM075_log.txt')

    root_stim = NaturalMovie(memname, OF1, 29.97, TRAIN_DUR, reconstruct=True, secs=log[20]['sec'], frame_numbers=log[20]['frame_numbers'])

    process = threading.Thread(target=root_stim.reconstruct).start()
    
    dim = get_video_dim(OF1)

    manager.load_stim(name='PixMap', memname=memname, frame_size=dim,surface='cylindrical')
    manager()
    
    # Start the stimulus
    manager.start_stim(reconstruct=True)
    manager.start_corner_square()
    manager()

    # Preload the stop so that extra time isnt taken setting up these calls during the idle period
    # Meanwhile stimulus is running

    size = np.arange(10).shape        
    mem = shared_memory.SharedMemory(name=memname+'_rec')
    code = np.ndarray(size,dtype=np.uint8, buffer=mem.buf)
    
    running = True
    while running:
        if code[-2] == 1:
            running = False
    
    manager.save_rendered_movie('/home/baccuslab/NS_20')
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

