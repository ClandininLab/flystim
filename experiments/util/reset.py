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

    manager = init_screens()
    
    manager.black_corner_square()
    manager.set_idle_background(0)
    manager.start_stim()
    manager()
    manager.stop_stim()
    manager()

if __name__ == '__main__':
    main()

