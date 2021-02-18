#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

import logging

from flystim.draw import draw_screens
from flystim.trajectory import RectangleTrajectory, RectangleAnyTrajectory, SinusoidalTrajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server
from flystim.ballrig_util import latency_report, make_tri_list
from flystim import fictrac_util as ftu

import sys
from time import sleep, time, strftime, localtime
import numpy as np
import math
from math import degrees
import itertools
import os, subprocess
import h5py
import socket
import select

import matplotlib.pyplot as plt

from ballrig_analysis.utils import fictrac_utils

FT_FRAME_NUM_IDX = 0
FT_THETA_IDX = 16
FT_TIMESTAMP_IDX = 21
FT_SQURE_IDX = 25


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

    closed_loop = input("Closed loop? (default: True): ")#"isoD1-F"
    if closed_loop=="":
        closed_loop = True
    else:
        closed_loop = closed_loop.lower() in ['true', '1', 't', 'y', 'yes']
    print(closed_loop)
    duration_in_min = input("Enter duration in minutes (e.g. 40): ")#26
    if duration_in_min=="":
        duration_in_min = 40
    duration_in_min = float(duration_in_min)
    print(duration_in_min)
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

    _ = input("Press enter to continue.")#26

    parent_path = os.getcwd()
    save_prefix = strftime('%Y%m%d_%H%M%S', localtime())
    save_path = os.path.join(parent_path, save_prefix)
    if save_history:
        os.mkdir(save_path)

    rgb_power = [0, 0.9, 0.9]

    ft_frame_rate = 308 #Hz, higher
    fs_frame_rate = 120

    current_time = strftime('%Y%m%d_%H%M%S', localtime())

    #####################################################
    # part 3: stimulus definitions
    #####################################################

    # Stimulus parameters
    stim_name = "sine"
    duration = duration_in_min*60 #sec

    background_color = 0

    bar_width = 15
    bar_height = 150
    bar_color = 1
    #bar_angle = 0

    fix_sine_amplitude = 15
    fix_sine_period = 2

    #######################
    # Stimulus construction

    # Bar start location
    start_theta = 0

    # Fix bar trajectory
    sin_traj = SinusoidalTrajectory(amplitude=fix_sine_amplitude, period=fix_sine_period) # period of 1 second
    fixbar_traj = RectangleAnyTrajectory(x=sin_traj, y=90, w=bar_width, h=bar_height, color=bar_color)
    # fix_sine_template = sin_traj.eval_at(np.arange(0, fix_window + fix_sine_period, 1/ft_frame_rate))

    if save_history:
        params = {'closed_loop':closed_loop, 'genotype':genotype, 'age':age, \
            'save_path':save_path, 'save_prefix': save_prefix, \
            'ft_frame_rate': ft_frame_rate, 'fs_frame_rate':fs_frame_rate, \
            'rgb_power':rgb_power, 'current_time':current_time, \
            'temperature':temperature, 'humidity':humidity, 'airflow':airflow, \
            'stim_name':stim_name, 'duration':duration, 'background_color':background_color, \
            'bar_width':bar_width, 'bar_height':bar_height, 'bar_color':bar_color, \
            'start_theta':start_theta, \
            'fix_sine_amplitude':fix_sine_amplitude, \
            'fix_sine_period':fix_sine_period}

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

    FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
    FICTRAC_PORT = 33334         # The port used by the server
    FICTRAC_BIN =    "/home/clandinin/lib/fictrac211/bin/fictrac"
    FICTRAC_CONFIG = "/home/clandinin/lib/fictrac211/config_MC.txt"

    # Start stim server
    fs_manager = launch_stim_server(screen)
    if save_history:
        fs_manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=duration)
    fs_manager.set_idle_background(background_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    if closed_loop:
        ft_manager = ftu.FtClosedLoopManager(fs_manager=fs_manager, ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG, ft_host=FICTRAC_HOST, ft_port=FICTRAC_PORT)
    else:
        ft_manager = ftu.FtManager(ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG)
    ft_manager.sleep(8) #allow fictrac to gather data

    if save_history:
        fs_manager.start_saving_history()

    ####################### Confirm Fixation here #########################

    print("===== Start fixation ======")

    fs_manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_traj.to_dict(), background=background_color)
    if closed_loop:
        ft_manager.set_theta_0()
    fs_manager.start_stim()
    t_start = time()

    ft_manager.update_theta_for(duration) if closed_loop else ft_manager.sleep(duration)

    fs_manager.stop_stim()
    t_end = time()

    # Save things
    if save_history:
        fs_manager.stop_saving_history()
        fs_manager.set_save_prefix(save_prefix)
        fs_manager.save_history()

    # close fictrac
    ft_manager.close()

    print(f"===== Experiment duration: {(t_end-t_start)/60:.{5}} min =====")

    # Plot fictrac summary and save png
    fictrac_files = sorted([x for x in os.listdir(parent_path) if x[0:7]=='fictrac'])[-2:]
    ft_summary_save_fn = os.path.join(parent_path, save_prefix+".png") if save_history else None
    fictrac_utils.plot_ft_session_summary(os.path.join(parent_path, fictrac_files[0]), label=save_prefix, show=(not save_history), save=ft_summary_save_fn, window_size=5)

    if save_history:
        # Move fictrac files
        print ("Moving/removing fictrac files.")
        os.rename(os.path.join(parent_path, fictrac_files[0]), os.path.join(save_path, fictrac_files[0]))
        os.remove(os.path.join(parent_path, fictrac_files[1]))

        # Move Fictrac summary
        os.rename(os.path.join(parent_path, save_prefix+".png"), os.path.join(save_path, save_prefix+".png"))

        # Open up fictrac file
        fictrac_data_fn = fictrac_files[0]
        ft_data_handler = open(os.path.join(save_path, fictrac_data_fn), 'r')

        # Create h5f file
        h5f = h5py.File(os.path.join(save_path, save_prefix + '.h5'), 'a')
        # params
        for (k,v) in params.items():
            h5f.attrs[k] = v
        h5f.attrs['t_start'] = t_start
        h5f.attrs['t_end'] = t_end
        if closed_loop:
            h5f.attrs['theta_rad_0'] = theta_rad_0

        save_dir_prefix = os.path.join(save_path, save_prefix)
        fs_square = np.loadtxt(save_dir_prefix+'_fs_square.txt')
        fs_timestamps = np.loadtxt(save_dir_prefix+'_fs_timestamps.txt')

        # Process through ft_data_handler until it gets to the frame iti before first trial
        curr_time = 0
        while curr_time < t_start:
            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3

        ft_frame = []
        ft_theta = []
        ft_timestamps = []
        ft_square = []

        ft_line = ft_data_handler.readline()
        while ft_line!="" and curr_time < t_end:
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3
            ft_frame.append(int(ft_toks[FT_FRAME_NUM_IDX]))
            ft_theta.append(float(ft_toks[FT_THETA_IDX]))
            ft_timestamps.append(float(ft_toks[FT_TIMESTAMP_IDX]))
            ft_square.append(float(ft_toks[FT_SQURE_IDX]))
            ft_line = ft_data_handler.readline()

        h5f.create_dataset("fs_square", data=fs_square)
        h5f.create_dataset("fs_timestamps", data=fs_timestamps)
        h5f.create_dataset("ft_frame", data=ft_frame)
        h5f.create_dataset("ft_square", data=ft_square)
        h5f.create_dataset("ft_timestamps", data=np.array(ft_timestamps)/1e3)
        h5f.create_dataset("ft_theta", data=ft_theta)

        ft_data_handler.close()
        h5f.close()

        # Delete flystim txt output files
        fs_txt_files = [x for x in os.listdir(save_path) if x.startswith(save_prefix) and x.endswith('.txt')]
        for txt_fn in fs_txt_files:
            os.remove(os.path.join(save_path, txt_fn))

        # Move hdf5 file out to parent path
        os.rename(os.path.join(save_path, save_prefix + '.h5'), os.path.join(parent_path, save_prefix + '.h5'))

        # Latency report
        with h5py.File(os.path.join(parent_path, save_prefix + '.h5'), 'r') as h5f:
            fs_square = h5f['fs_square'][()]
            fs_timestamps = h5f['fs_timestamps'][()]
            ft_square = h5f['ft_square'][()]
            ft_timestamps = h5f['ft_timestamps'][()]
            latency_report(fs_timestamps, fs_square, ft_timestamps, ft_square, window_size=2)

    else: #not saving history
        # Delete fictrac files
        print ("Deleting " + str(len(fictrac_files)) + " fictrac files.")
        for i in range(len(fictrac_files)):
            os.remove(os.path.join(parent_path, fictrac_files[i]))

if __name__ == '__main__':
    main()
