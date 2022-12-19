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
    experiment_name = __file__.split('.')[0]                                                         
 22                                                                                 
 23     if os.path.exists('/home/baccuslab/logs/{}_log.txt'.format(experiment_name)):
 24         resp = input('WARNING: {} log already exists. Delete it and continue? (y/n)'.format(experimen    t_name))
 25         if resp == 'y':                                                         
 26             os.remove('/home/baccuslab/logs/{}_log.txt'.format(experiment_name))
 27         if resp == 'n':                                                         
 28             sys.exit()                                                          
 29                                                                                 
 30     logfile_path = '/home/baccuslab/logs/{}_log.txt'.format(experiment_name)

    INTERVAL=1
    N_TEST=10

    N_TRAIN=1

    TRAIN_DUR= 20*60
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
    sleep(60*5)
    #### TEST WHITENOISE
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (WN_NPIX,int(800/1920*WN_NPIX)), 20, TEST_DUR, seed=37)
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

    #### TEST BAKER
    path = test_baker_path
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(path)
        dim2 = [dim[0]-120, dim[1], dim[2]]
        dim = dim2
        nm = NaturalMovie(memname, path, 60, TEST_DUR)
        p = threading.Thread(target=nm.stream)
        p.start()
        
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
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

        del nm, p
    
    #### TEST NYC
    path = test_nyc_path
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(path)
        dim2 = [dim[0]-120, dim[1], dim[2]]
        dim = dim2
        nm = NaturalMovie(memname, path, 60, TEST_DUR)
        p = threading.Thread(target=nm.stream)
        p.start()
        
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
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

        del nm, p

    #### TRAIN WN
    for i in range(N_TRAIN):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (WN_NPIX,int(800/1920*WN_NPIX)), 20, TRAIN_DUR, seed=17)
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

    ### TRAIN BAKER
    path = train_baker_path
    for i in range(N_TRAIN):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(path)
        dim2 = [dim[0]-120, dim[1], dim[2]]
        dim = dim2
        nm = NaturalMovie(memname, path, 60, TRAIN_DUR)
        p = threading.Thread(target=nm.stream)
        p.start()
        
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
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

        del nm, p
    ### TRAIN NYC
    path = train_nyc_path
    for i in range(N_TRAIN):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(path)
        dim2 = [dim[0]-120, dim[1], dim[2]]
        dim = dim2
        nm = NaturalMovie(memname, path, 60, TRAIN_DUR)
        p = threading.Thread(target=nm.stream)
        p.start()
        
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
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

        del nm, p

    #### TEST WHITENOISE
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)
        
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (WN_NPIX,int(800/1920*WN_NPIX)), 20, TEST_DUR, seed=37)
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

    #### TEST BAKER
    path = test_baker_path
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(path)
        dim2 = [dim[0]-120, dim[1], dim[2]]
        dim = dim2
        nm = NaturalMovie(memname, path, 60, TEST_DUR)
        p = threading.Thread(target=nm.stream)
        p.start()
        
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
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

        del nm, p
    
    #### TEST NYC
    path = test_nyc_path
    for i in range(N_TEST):
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(INTERVAL)

        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(path)
        dim2 = [dim[0]-120, dim[1], dim[2]]
        dim = dim2
        nm = NaturalMovie(memname, path, 60, TEST_DUR)
        p = threading.Thread(target=nm.stream)
        p.start()
        
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
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
        
        del nm, p

if __name__ == '__main__':
    main()

