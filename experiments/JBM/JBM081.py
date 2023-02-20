#!/usr/bin/env python3
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
    experiment_name = __file__.split('.')[0]
        
    if os.path.exists('/home/baccuslab/logs/{}_log.txt'.format(experiment_name)):
        resp = input('WARNING: {} log already exists. Delete it and continue? (y/n)'.format(experiment_name))
        if resp == 'y':
            os.remove('/home/baccuslab/logs/{}_log.txt'.format(experiment_name))
        if resp == 'n':
            sys.exit()

    logfile_path = '/home/baccuslab/logs/{}_log.txt'.format(experiment_name)

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
    manager.stop_stim()
    manager()


    manager.black_corner_square()
    manager.set_idle_background(0)
    manager()
    idle(2)

#     # OF Test Repeats
#     for i in range(N_TEST):
#         manager.black_corner_square()
#         manager.set_idle_background(0)
#         manager()

#         manager.set_global_fly_pos(0,0,-0.2) #midline of the stimulus
#         idle(INTERVAL)
        
#         rwg = random_word.RandomWords()
#         memname = rwg.get_random_word()


#         root_stim = NaturalMovie(memname, OFTest, 60, TEST_DUR, logfile=logfile_path)

#         process = threading.Thread(target=root_stim.stream).start()
        
#         dim = get_video_dim(OFTest)

#         manager.load_stim(name='PixMap', memname=memname, frame_size=dim,surface='cylindrical')
#         manager()
        
#         # Start the stimulus
#         manager.start_stim()
#         manager.start_corner_square()
#         manager()

#         # Preload the stop so that extra time isnt taken setting up these calls during the idle period
#         # Meanwhile stimulus is running
#         manager.stop_stim()
#         manager.black_corner_square()
#         manager.set_idle_background(0)

#         idle(TEST_DUR)
        
        
#         manager()
        

#         try:
#             process.terminate()
#         except:
#             pass

#         idle(INTERVAL)

#         del root_stim,process

    #### TEST WN
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        idle(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        root_stim = WhiteNoise(memname, (NUM_PIXELS_HEIGHT, NUM_PIXELS_WIDTH), UPDATE_RATE, TEST_DUR, seed=TEST_SEED, logfile = logfile_path)
        process = threading.Thread(target=root_stim.stream).start()

        manager.load_stim(name='PixMap', memname=memname, frame_size=(NUM_PIXELS_HEIGHT,NUM_PIXELS_WIDTH,3),surface='spherical')
        manager()
        
        # Start the stimulus
        manager.start_stim()
        manager.start_corner_square()
        manager()

        # Preload the stop so that extra time isnt taken setting up these calls during the idle period
        # Meanwhile stimulus is running
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        idle(TEST_DUR)
        
        manager()
        

        try:
            process.terminate()
        except:
            pass

        idle(INTERVAL)

        del root_stim,process
    #OF TRAIN
    for i in range(N_TRAIN):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        manager.set_global_fly_pos(0,0,-0.2) #midline of the stimulus
        idle(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()


        root_stim = NaturalMovie(memname, OF1, 29.97, TRAIN_DUR, logfile=logfile_path)

        process = threading.Thread(target=root_stim.stream).start()
        
        dim = get_video_dim(OF1)

        manager.load_stim(name='PixMap', memname=memname, frame_size=dim,surface='cylindrical')
        manager()
        
        # Start the stimulus
        manager.start_stim()
        manager.start_corner_square()
        manager()

        # Preload the stop so that extra time isnt taken setting up these calls during the idle period
        # Meanwhile stimulus is running
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        idle(TRAIN_DUR)
        
        
        manager()
        

        try:
            process.terminate()
        except:
            pass

        idle(INTERVAL)

        del root_stim,process

    #### TRAIN WN
    for i in range(N_TRAIN):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        idle(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        root_stim = WhiteNoise(memname, (NUM_PIXELS_HEIGHT, NUM_PIXELS_WIDTH), UPDATE_RATE, TRAIN_DUR, seed=TRAIN_SEED, logfile = logfile_path)
        process = threading.Thread(target=root_stim.stream).start()

        manager.load_stim(name='PixMap', memname=memname, frame_size=(NUM_PIXELS_HEIGHT,NUM_PIXELS_WIDTH,3),surface='spherical')
        manager()
        
        # Start the stimulus
        manager.start_stim()
        manager.start_corner_square()
        manager()

        # Preload the stop so that extra time isnt taken setting up these calls during the idle period
        # Meanwhile stimulus is running
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        idle(TRAIN_DUR)
        
        manager()
        

        try:
            process.terminate()
        except:
            pass

        idle(INTERVAL)

        del root_stim,process

    # OF Test Repeats
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        manager.set_global_fly_pos(0,0,-0.2) #midline of the stimulus
        idle(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()


        root_stim = NaturalMovie(memname, OFTest, 60, TEST_DUR, logfile=logfile_path)

        process = threading.Thread(target=root_stim.stream).start()
        
        dim = get_video_dim(OFTest)

        manager.load_stim(name='PixMap', memname=memname, frame_size=dim,surface='cylindrical')
        manager()
        
        # Start the stimulus
        manager.start_stim()
        manager.start_corner_square()
        manager()

        # Preload the stop so that extra time isnt taken setting up these calls during the idle period
        # Meanwhile stimulus is running
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        idle(TEST_DUR)
        
        
        manager()
        

        try:
            process.terminate()
        except:
            pass

        idle(INTERVAL)

        del root_stim,process

    #### TEST WN
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        idle(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        root_stim = WhiteNoise(memname, (NUM_PIXELS_HEIGHT, NUM_PIXELS_WIDTH), UPDATE_RATE, TEST_DUR, seed=TEST_SEED, logfile = logfile_path)
        process = threading.Thread(target=root_stim.stream).start()

        manager.load_stim(name='PixMap', memname=memname, frame_size=(NUM_PIXELS_HEIGHT,NUM_PIXELS_WIDTH,3),surface='spherical')
        manager()
        
        # Start the stimulus
        manager.start_stim()
        manager.start_corner_square()
        manager()

        # Preload the stop so that extra time isnt taken setting up these calls during the idle period
        # Meanwhile stimulus is running
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        idle(TEST_DUR)
        
        manager()
        

        try:
            process.terminate()
        except:
            pass

        idle(INTERVAL)

        del root_stim,process
if __name__ == '__main__':
    main()

