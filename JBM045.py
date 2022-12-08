#!/usr/bin/env python3
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
from time import sleep

def main():
    if os.path.exists('/home/baccuslab/log45.txt'):
        resp = input('Delete log.txt?')
        if resp == 'y':
            os.remove('/home/baccuslab/log45.txt')   

    INTERVAL=1
    N_TEST=10

    N_TRAIN=1

    TRAIN_DUR= 30*60
    TEST_DUR = 15

    WN_NPIX = 100


    manager = init_screens()
    
    manager.black_corner_square()
    manager.set_idle_background(0)
    manager.start_stim()
    manager()
    sleep(60*5)
    #### TEST WHITENOISE
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (int(800/1920*WN_NPIX), WN_NPIX), 10, TEST_DUR, seed=420)
        p = threading.Thread(target=wn.stream).start()
        manager.load_stim(name='PixMap', memname=memname, frame_size=(int(800/1920*WN_NPIX),WN_NPIX,3))
        manager()

        manager.start_stim()
        manager.start_corner_square()
        manager()

        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        sleep(TEST_DUR)
        
        manager()

        try:
            p.terminate()
        except:
            pass

        sleep(INTERVAL)

        del wn,p


    #### TRAIN WN
    for i in range(N_TRAIN):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (int(800/1920*WN_NPIX), WN_NPIX), 10, TRAIN_DUR, seed=37)
        p = threading.Thread(target=wn.stream).start()
        manager.load_stim(name='PixMap', memname=memname, frame_size=(int(800/1920*WN_NPIX),WN_NPIX,3))
        manager()

        manager.start_stim()
        manager.start_corner_square()
        manager()

        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        sleep(TRAIN_DUR)
        
        manager()

        try:
            p.terminate()
        except:
            pass

        sleep(INTERVAL)

        del wn,p

    #### TEST WHITENOISE
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (int(800/1920*WN_NPIX),WN_NPIX), 10, TEST_DUR, seed=420)
        p = threading.Thread(target=wn.stream).start()
        manager.load_stim(name='PixMap', memname=memname, frame_size=(int(800/1920*WN_NPIX),WN_NPIX,3))
        manager()

        manager.start_stim()
        manager.start_corner_square()
        manager()

        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)

        sleep(TEST_DUR)
        
        manager()

        try:
            p.terminate()
        except:
            pass

        sleep(INTERVAL)

        del wn,p
if __name__ == '__main__':
    main()

