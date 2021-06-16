#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

import logging

from flystim1.draw import draw_screens
from flystim1.trajectory import RectangleTrajectory, RectangleAnyTrajectory, SinusoidalTrajectory
from flystim1.screen import Screen
from flystim1.stim_server import launch_stim_server

import sys
from time import sleep, time, strftime, localtime
import numpy as np
from scipy.stats import zscore
import math
from math import degrees
import itertools
import os, subprocess
import socket
import select
from collections import deque

import matplotlib.pyplot as plt


def main():
    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: User defined parameters
    #####################################################


    n_repeats = input("Enter number of repeats (e.g. 35): ")#26
    if n_repeats=="":
        n_repeats = 35
    print(n_repeats)

    _ = input("Press enter to continue.")#26

    parent_path = os.getcwd()

    #####################################################
    # part 3: stimulus definitions
    #####################################################

    # Trial structure
    trial_labels = np.array(["inc_r","inc_l","con_r","con_l"]) # visible, consistent. 00, 01, 10, 11
    trial_structure = np.random.permutation(np.repeat(trial_labels, n_repeats))
    n_trials = len(trial_structure)

    # Stimulus parameters
    stim_name = "pause"
    prime_speed = 5 #degrees per sec
    probe_speed = 5 #degrees per sec
    preprime_duration = 1 #seconds
    prime_duration = 2 #seconds
    occlusion_duration = 0.5 #seconds
    pause_duration = 1 #seconds
    probe_duration = 2 #seconds
    iti = 2 #seconds

    con_stim_duration = preprime_duration + prime_duration + occlusion_duration + probe_duration
    inc_stim_duration = con_stim_duration + pause_duration

    background_color = 0

    bar_width = 5
    bar_height = 150
    bar_color = 1
    #bar_angle = 0

    occluder_height = 150
    occluder_color = 0.5

    #######################
    # Stimulus construction

    # Bar start location
    start_theta = 0

    # consistent bar trajectory
    con_time = [0, preprime_duration]
    con_x = [0, 0]
    inc_time = [0, preprime_duration]
    inc_x = [0, 0]

    prime_movement = prime_speed * (prime_duration + occlusion_duration)
    prime_end_theta = prime_movement
    prime_end_time = preprime_duration + prime_duration + occlusion_duration

    con_time.append(prime_end_time)
    con_x.append(prime_end_theta)
    inc_time.append(prime_end_time)
    inc_x.append(prime_end_theta)

    pause_end_theta = prime_end_theta
    pause_end_time = prime_end_time + pause_duration

    inc_time.append(pause_end_time)
    inc_x.append(pause_end_theta)

    probe_movement = probe_speed * probe_duration
    probe_end_theta = prime_end_theta + probe_movement
    con_probe_end_time = prime_end_time + probe_duration
    inc_probe_end_time = pause_end_time + probe_duration

    con_time.append(con_probe_end_time)
    con_x.append(probe_end_theta)
    inc_time.append(inc_probe_end_time)
    inc_x.append(probe_end_theta)

    # Compute location and width of the occluder per specification
    occlusion_start_theta = prime_speed * prime_duration
    occluder_width = prime_speed * occlusion_duration + bar_width # the last term ensures that the bar is completely hidden during the occlusion period
    occluder_loc = occlusion_start_theta + occluder_width/2 - bar_width/2 # the last two terms account for widths of the bar and the occluder, such that the bar is completely hidden during occlusion period
    occluder_time = [0, con_stim_duration]
    occluder_x = [occluder_loc, occluder_loc]

    con_bar_traj_r = list(zip(con_time, (start_theta - np.array(con_x)).tolist()))
    con_bar_traj_l = list(zip(con_time, (start_theta + np.array(con_x)).tolist()))
    inc_bar_traj_r = list(zip(inc_time, (start_theta - np.array(inc_x)).tolist()))
    inc_bar_traj_l = list(zip(inc_time, (start_theta + np.array(inc_x)).tolist()))
    occluder_traj_r = list(zip(occluder_time, (start_theta - np.array(occluder_x)).tolist()))
    occluder_traj_l = list(zip(occluder_time, (start_theta + np.array(occluder_x)).tolist()))

    # Create flystim trajectory objects
    con_bar_r = RectangleTrajectory(x=con_bar_traj_r, y=90, w=bar_width, h=bar_height, color=bar_color)
    con_bar_l = RectangleTrajectory(x=con_bar_traj_l, y=90, w=bar_width, h=bar_height, color=bar_color)
    inc_bar_r = RectangleTrajectory(x=inc_bar_traj_r, y=90, w=bar_width, h=bar_height, color=bar_color)
    inc_bar_l = RectangleTrajectory(x=inc_bar_traj_l, y=90, w=bar_width, h=bar_height, color=bar_color)
    occluder_r_visible = RectangleTrajectory(x=occluder_traj_r, y=90, w=occluder_width, h=occluder_height, color=occluder_color)
    occluder_r_invisible = RectangleTrajectory(x=occluder_traj_r, y=90, w=occluder_width, h=occluder_height, color=background_color)
    occluder_l_visible = RectangleTrajectory(x=occluder_traj_l, y=90, w=occluder_width, h=occluder_height, color=occluder_color)
    occluder_l_invisible = RectangleTrajectory(x=occluder_traj_l, y=90, w=occluder_width, h=occluder_height, color=background_color)


    #####################################################################


    # Create screen object
    screen = Screen(server_number=1, id=1, fullscreen=True)#square_side=0.08,coh_bar_traj_r square_loc='ur')
    #print(screen)

    # Start stim server
    manager = launch_stim_server(screen)
    manager.set_idle_background(background_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    # Loop through trials
    for t in range(n_trials):
        # begin trial
        if trial_structure[t] == "inc_r": # invisible, inconsistent_r. 00, 01, 10, 11
            bar_traj = inc_bar_r
            occ_traj = occluder_r_visible
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_r": # invisible, consistent_r. 00, 01, 10, 11
            bar_traj = con_bar_r
            occ_traj = occluder_r_visible
            stim_duration = con_stim_duration
        elif trial_structure[t] == "inc_l": # invisible, inconsistent_l. 00, 01, 10, 11
            bar_traj = inc_bar_l
            occ_traj = occluder_l_visible
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_l": # invisible, consistent_l. 00, 01, 10, 11
            bar_traj = con_bar_l
            occ_traj = occluder_l_visible
            stim_duration = con_stim_duration
 
        print(f"===== Trial {t}; type {trial_structure[t]} ======")

        #manager.set_global_theta_offset(0)
        manager.load_stim('MovingPatch', trajectory=bar_traj.to_dict(), background=background_color, hold=True)
        manager.load_stim('MovingPatch', trajectory=occ_traj.to_dict(), background=None, hold=True)

        manager.start_stim()
        sleep(stim_duration)
        manager.stop_stim()
        sleep(iti)


if __name__ == '__main__':
    main()
