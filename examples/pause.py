#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

import logging

from flystim.draw import draw_screens
from flystim.trajectory import RectangleTrajectory, RectangleAnyTrajectory, SinusoidalTrajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server
from flystim.util import latency_report

import sys
from time import sleep, time, strftime, localtime
import numpy as np
from scipy.stats import zscore
import math
from math import degrees
import itertools
import os, subprocess
import h5py
import socket
import select
from collections import deque

import matplotlib.pyplot as plt

from ballrig_analysis.utils import fictrac_utils

def main():
    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: User defined parameters
    #####################################################

    if len(sys.argv) > 1 and sys.argv[1] == "run":
        save_history = True
    else:
        save_history = False

    if save_history:
        genotype = input("Enter genotype (e.g. isoD1-F-thirsty): ")#"isoD1-F"
        if genotype=="":
            genotype = "isoD1-F-thirsty"
        print(genotype)
        age = input("Enter age in dpe (e.g. 4): ") #4
        if age=="":
            age = 4
        print(age)
        temperature = input("Enter temperature (e.g. 36.0): ") #36.0 #6.30=36.2  6.36=36  6.90=34 6.82=34.3  6.75=34.5(33.7) no hum   #7.10=34  7.00=34.2  6.97=34.5 @ 44%
        if temperature=="":
            temperature = 36.0
        print(temperature)
        humidity = input("Enter humidity (e.g. 28): ")#26
        if humidity=="":
            humidity = 28
        print(humidity)
        airflow = input("Enter airflow (e.g. 0.8): ")#26
        if airflow=="":
            airflow = 0.8
        print(airflow)

    n_repeats = input("Enter number of repeats (e.g. 35): ")#26
    if n_repeats=="":
        n_repeats = 35
    print(n_repeats)

    _ = input("Press enter to continue.")#26

    parent_path = os.getcwd()
    save_prefix = strftime('%Y%m%d_%H%M%S', localtime())
    save_path = os.path.join(parent_path, save_prefix)
    if save_history:
        os.mkdir(save_path)

    rgb_power = [0, 0.9, 0.9]

    fs_frame_rate = 120

    current_time = strftime('%Y%m%d_%H%M%S', localtime())

    #####################################################
    # part 3: stimulus definitions
    #####################################################

    # Trial structure
    trial_labels = np.array(["inc_r","inc_l","con_r","con_l"]) # visible, consistent. 00, 01, 10, 11
    trial_structure = np.random.permutation(np.repeat(trial_labels, n_repeats))
    n_trials = len(trial_structure)

    # Stimulus parameters
    stim_name = "pause"
    prime_speed = 30 #degrees per sec
    probe_speed = 30 #degrees per sec
    preprime_duration = 1 #seconds
    prime_duration = 4 #seconds
    occlusion_duration = 0.5 #seconds
    pause_duration = 1 #seconds
    probe_duration = 2 #seconds
    iti = 2 #seconds

    con_stim_duration = preprime_duration + prime_duration + occlusion_duration + probe_duration
    inc_stim_duration = con_stim_duration + pause_duration

    background_color = 0

    bar_width = 15
    bar_height = 150
    bar_color = 1
    #bar_angle = 0

    occluder_height = 150
    occluder_color = 0.5

    fix_score_threshold = .8
    fix_sine_amplitude = 15
    fix_sine_period = 1
    fix_window = 2 #seconds
    fix_max_duration = 45

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


    if save_history:
        params = {'genotype':genotype, 'age':age, \
            'save_path':save_path, 'save_prefix': save_prefix, \
            'fs_frame_rate':fs_frame_rate, \
            'rgb_power':rgb_power, 'current_time':current_time, \
            'temperature':temperature, 'humidity':humidity, 'airflow':airflow, \
            'trial_labels':trial_labels.tolist(), 'trial_structure':trial_structure.tolist(), \
            'n_repeats':n_repeats, 'n_trials':n_trials, \
            'stim_name':stim_name, 'prime_speed':prime_speed, 'probe_speed':probe_speed, 'preprime_duration':preprime_duration, 'prime_duration':prime_duration, 'occlusion_duration':occlusion_duration, 'pause_duration':pause_duration, 'probe_duration':probe_duration, 'iti':iti, 'con_stim_duration':con_stim_duration, 'inc_stim_duration':inc_stim_duration, 'background_color':background_color, \
            'bar_width':bar_width, 'bar_height':bar_height, 'bar_color':bar_color, \
            'occluder_height':occluder_height, \
            'occluder_color':occluder_color, 'start_theta':start_theta}
        params['con_bar_traj_r'] = con_bar_traj_r
        params['con_bar_traj_l'] = con_bar_traj_l
        params['inc_bar_traj_r'] = inc_bar_traj_r
        params['inc_bar_traj_l'] = inc_bar_traj_l
        params['occluder_traj_r'] = occluder_traj_r
        params['occluder_traj_l'] = occluder_traj_l

    #####################################################################

    # Set up logging
    if save_history:
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename="{}/{}.log".format(save_path, save_prefix),
            level=logging.DEBUG
        )

    # Set lightcrafter and GL environment settings
    os.system('/home/clandinin/miniconda3/bin/lcr_ctl --fps 120 --red_current ' + str(rgb_power[0]) + ' --blue_current ' + str(rgb_power[2]) + ' --green_current ' + str(rgb_power[1]))

    # Create screen object
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=0.01, square_loc=(0.59,0.74))#square_side=0.08,coh_bar_traj_r square_loc='ur')
    #print(screen)

    # Start stim server
    manager = launch_stim_server(screen)
    if save_history:
        manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=inc_stim_duration+fix_max_duration)
    manager.set_idle_background(background_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    if save_history:
        fix_scores_all = []
        fix_ft_frames_all = []
        trial_start_times = []
        trial_start_ft_frames = []
        trial_end_times = []
        trial_end_ft_frames = []
    fix_start_times = []
    fix_end_times = []
    fix_success_all = []

    # Pretend previous trial ended here before trial 0
    t_iti_start = time()
    t_exp_start = t_iti_start
    trial_end_time_neg1 = t_iti_start #timestamp of ITI before first trial

    # Loop through trials
    for t in range(n_trials):
        # begin trial

        if trial_structure[t] == "inc_r": # invisible, inconsistent_r. 00, 01, 10, 11
            bar_traj = inc_bar_r
            occ_traj = occluder_r_invisible
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_r": # invisible, consistent_r. 00, 01, 10, 11
            bar_traj = con_bar_r
            occ_traj = occluder_r_invisible
            stim_duration = con_stim_duration
        elif trial_structure[t] == "inc_l": # invisible, inconsistent_l. 00, 01, 10, 11
            bar_traj = inc_bar_l
            occ_traj = occluder_l_invisible
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_l": # invisible, consistent_l. 00, 01, 10, 11
            bar_traj = con_bar_l
            occ_traj = occluder_l_invisible
            stim_duration = con_stim_duration

        if save_history:
            manager.start_saving_history()

        print(f"===== Trial {t}; type {trial_structure[t]} ======")

        #manager.set_global_theta_offset(0)
        manager.load_stim('MovingPatch', trajectory=bar_traj.to_dict(), background=background_color, hold=True)
        manager.load_stim('MovingPatch', trajectory=occ_traj.to_dict(), background=None, hold=True)

        first_msg = True

        t_start = time()
        manager.start_stim()
        while (time() -  t_start) < stim_duration:
            continue
        manager.stop_stim()
        t_end = time()
        t_iti_start = t_end

        print(f"===== Trial end (FT dur: {(ts-ts_0)/1000:.{5}}s)======")

        # Save things
        if save_history:
            manager.stop_saving_history()
            manager.set_save_prefix(save_prefix+"_t"+f'{t:03}')
            manager.save_history()

            trial_start_times.append(t_start)
            trial_start_ft_frames.append(ft_frame_num_0)
            trial_end_times.append(t_end)
            trial_end_ft_frames.append(ft_frame_num_end)


    t_exp_end = time()

    print(f"===== Experiment duration: {(t_exp_end-t_exp_start)/60:.{5}} min =====")



if __name__ == '__main__':
    main()
