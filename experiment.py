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
    baker_path = '/home/baccuslab/Videos/stimulus_videos/TEST_BAKER.avi'
    nyc_path = '/home/baccuslab/Videos/stimulus_videos/TEST_CITY.avi'
    manager = init_screens()
    
    manager.black_corner_square()
    manager.set_idle_background(0)
    manager.set_global_fly_pos(0,0,-0.3)
    manager.start_stim()
    manager()
    n_pix=200
    # for i in range(3):
    #     ### INIT 
    #     # break
    #     manager.black_corner_square()
    #     manager.set_idle_background(0)
    #     manager()

    #     sleep(3)
        
    #     ### WHITE NOISE
    #     rwg = random_word.RandomWords()
        
    #     memname = rwg.get_random_word()
    #     wn = WhiteNoise(memname, (n_pix,int(800/1920*n_pix)), 20)
    #     p = threading.Thread(target=wn.stream).start()
    #     manager.start_corner_square()
    #     manager.load_stim(name='PixMap', memname=memname, frame_size=(int(800/1920*n_pix),n_pix,3))
    #     manager.start_stim()
    #     manager()

    #     sleep(3)
        
    #     manager.stop_stim()
    #     manager.black_corner_square()
    #     manager.set_idle_background(0)
    #     manager()

    #     sleep(2)

    #     del wn,p
    
    # for i in range(3):
    #     ### NATURAL SCENE
    #     rwg = random_word.RandomWords()
    #     memname = rwg.get_random_word()
    #     dim = get_video_dim(baker_path)
    #     nm = NaturalMovie(memname, baker_path, 60)
    #     nm.warmup(20)
    #     p = threading.Thread(target=nm.stream).start()
    #     sleep(2)
    #     manager.start_corner_square()
    #     manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
    #     manager.start_stim()
    #     manager()
    #     sleep(3)    #     manager.set_global_fly_pos(0,0,0)
    #     manager.stop_stim()
    #     manager.set_idle_background(0)
    #     manager.black_corner_square()
    #     manager()
    #     sleep(2)
    #     nm.saveout()
    #     del nm,p
            
    for i in range(5):
        ### NATURAL SCENE
        rwg = random_word.RandomWords()
        memname = rwg.get_random_word()
        dim = get_video_dim(nyc_path)
        nm = NaturalMovie(memname, nyc_path, 60)
        nm.warmup(20)
        p = threading.Thread(target=nm.stream).start()
        sleep(2)
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=dim)
        manager.start_stim()
        manager()
        sleep(30)    #     manager.set_global_fly_pos(0,0,0)
        manager.stop_stim()

        manager.black_corner_square()
        manager()
        sleep(2)
        nm.saveout()
        del nm,p


    for i in range(10):
        ### INIT 
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(3)
        
        ### WHITE NOISE
        rwg = random_word.RandomWords()

        memname = rwg.get_random_word()
        wn = WhiteNoise(memname, (20,60), 20)
        p = threading.Thread(target=wn.stream).start()
        manager.start_corner_square()
        manager.load_stim(name='PixMap', memname=memname, frame_size=(20,60,3))
        manager.start_stim()
        manager()

        sleep(20)
        
        manager.stop_stim()
        manager.black_corner_square()
        manager.set_idle_background(0)
        manager()

        sleep(2)

        del wn,p
if __name__ == '__main__':
    main()

