#!/usr/bin/env python3
from flystim.root_stimuli import NaturalMovie, WhiteNoise
import flyrpc.multicall
import random_word
import cv2
import threading
import multiprocessing
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
    INTERVAL=1

    N_TEST=10
    N_TRAIN=1

    TRAIN_DUR=20*60
    TEST_DUR = 20

    WN_NPIX = 200


    test_baker_path = '/home/baccuslab/Videos/stimulus_videos/TEST_BAKER.avi'
    test_nyc_path = '/home/baccuslab/Videos/stimulus_videos/TEST_CITY.avi'
    train_baker_path = '/home/baccuslab/Videos/stimulus_videos/TRAIN_BAKER.avi'
    train_nyc_path = '/home/baccuslab/Videos/stimulus_videos/TRAIN_CITY.avi'
    manager = init_screens()
    
    manager.black_corner_square()
    manager.set_idle_background(0)
    manager.start_stim()
    manager()
    
    ##### TEST ####
    manager.set_global_fly_pos(0,0,-0.5)
    # WN
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (WN_NPIX,int(800/1920*WN_NPIX)), 20, seed=37)
        p = threading.Thread(target=wn.stream).start()
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=(int(800/1920*WN_NPIX),WN_NPIX,3))
        manager.start_stim()
        manager()

        sleep(TEST_DUR)
        
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        del wn,p
    
    # BAKER
    for i in range(N_TEST):
        ### NATURAL SCENE
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(test_baker_path)
        nm = NaturalMovie(memname, test_baker_path, 60)
        p = threading.Thread(target=nm.stream).start()
        sleep(INTERVAL)
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
        manager.start_stim()
        manager()
        sleep(TEST_DUR)    #     manager.set_global_fly_pos(0,0,0)
        manager.stop_stim()
        manager.set_idle_background(0)
        manager.black_corner_square()
        manager()
        sleep(INTERVAL)
        nm.saveout()
        del nm,p

    # NYC  
    for i in range(N_TEST):
        ### NATURAL SCENE
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(test_nyc_path)
        nm = NaturalMovie(memname, test_nyc_path, 60)
        nm.warmup(20)
        p = threading.Thread(target=nm.stream).start()
        sleep(INTERVAL)
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
        manager.start_stim()
        manager()
        sleep(TEST_DUR)    #     manager.set_global_fly_pos(0,0,0)
        manager.stop_stim()

        manager.black_corner_square()
        manager()
        sleep(INTERVAL)
        nm.saveout()
        del nm,p

    ##### TRAIN
    
    # WN
    for i in range(N_TRAIN):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (WN_NPIX,int(800/1920*WN_NPIX)), 20, seed=17)
        p = threading.Thread(target=wn.stream).start()
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=(int(800/1920*WN_NPIX),WN_NPIX,3))
        manager.start_stim()
        manager()

        sleep(TRAIN_DUR)
        
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        del wn,p
    # BAKER 
    for i in range(N_TRAIN):
        ### NATURAL SCENE
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(train_baker_path)
        nm = NaturalMovie(memname, train_baker_path, 60)
        p = threading.Thread(target=nm.stream).start()
        sleep(INTERVAL)
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
        manager.start_stim()
        manager()
        sleep(TRAIN_DUR)    #     manager.set_global_fly_pos(0,0,0)
        manager.stop_stim()
        manager.set_idle_background(0)
        manager.black_corner_square()
        manager()
        sleep(INTERVAL)
        nm.saveout()
        del nm,p

    #NYC 
    for i in range(N_TRAIN):
        ### NATURAL SCENE
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(train_nyc_path)
        nm = NaturalMovie(memname, train_nyc_path, 60)
        nm.warmup(20)
        p = threading.Thread(target=nm.stream).start()
        sleep(INTERVAL)
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
        manager.start_stim()
        manager()
        sleep(TRAIN_DUR)    #     manager.set_global_fly_pos(0,0,0)
        manager.stop_stim()

        manager.black_corner_square()
        manager()
        sleep(INTERVAL)
        nm.saveout()
        del nm,p


    ##### TEST ####
    manager.set_global_fly_pos(0,0,-0.5)
    # WN
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (WN_NPIX,int(800/1920*WN_NPIX)), 20, seed=37)
        p = threading.Thread(target=wn.stream).start()
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=(int(800/1920*WN_NPIX),WN_NPIX,3))
        manager.start_stim()
        manager()

        sleep(TEST_DUR)
        
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        del wn,p
    
    # BAKER
    for i in range(N_TEST):
        ### NATURAL SCENE
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(test_baker_path)
        nm = NaturalMovie(memname, test_baker_path, 60)
        p = threading.Thread(target=nm.stream).start()
        sleep(INTERVAL)
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
        manager.start_stim()
        manager()
        sleep(TEST_DUR)    #     manager.set_global_fly_pos(0,0,0)
        manager.stop_stim()
        manager.set_idle_background(0)
        manager.black_corner_square()
        manager()
        sleep(INTERVAL)
        nm.saveout()
        del nm,p

    # NYC  
    for i in range(N_TEST):
        ### NATURAL SCENE
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(test_nyc_path)
        nm = NaturalMovie(memname, test_nyc_path, 60)
        nm.warmup(20)
        p = threading.Thread(target=nm.stream).start()
        sleep(INTERVAL)
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
        manager.start_stim()
        manager()
        sleep(TEST_DUR)    #     manager.set_global_fly_pos(0,0,0)
        manager.stop_stim()

        manager.black_corner_square()
        manager()
        sleep(INTERVAL)
        nm.saveout()
        del nm,p


if __name__ == '__main__':
    main()

