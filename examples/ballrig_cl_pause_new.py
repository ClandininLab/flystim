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

FT_FRAME_NUM_IDX = 0
FT_THETA_IDX = 16
FT_TIMESTAMP_IDX = 21
FT_SQURE_IDX = 25

def fixation_score(q_theta, template_theta):
    '''
    Pearson Correlation scoring
    Equivalent to zscoring both theta and template then summing elementwise multiplication and normalizing.
    '''
    q_theta = np.unwrap(q_theta)

    lag = np.argmax(np.correlate(template_theta, q_theta, mode='valid'))
    template_shifted_trimmed = template_theta[lag:lag+len(q_theta)]

    score = np.corrcoef(q_theta, template_shifted_trimmed)[0,1]
    return score

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

    ft_frame_rate = 308 #Hz, higher
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
    preprime_duration = 2 #seconds
    prime_duration = 2 #seconds
    occlusion_duration = 0.5 #seconds
    pause_duration = 1 #seconds
    probe_duration = 1 #seconds
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


    # Fix bar trajectory
    sin_traj = SinusoidalTrajectory(amplitude=fix_sine_amplitude, period=fix_sine_period) # period of 1 second
    fixbar_traj = RectangleAnyTrajectory(x=sin_traj, y=90, w=bar_width, h=bar_height, color=bar_color)
    fix_sine_template = sin_traj.eval_at(np.arange(0, fix_window + fix_sine_period, 1/ft_frame_rate))
    fix_q_len = ft_frame_rate*fix_window
    fix_q_theta_rad = [0] * fix_q_len

    if save_history:
        params = {'genotype':genotype, 'age':age, \
            'save_path':save_path, 'save_prefix': save_prefix, \
            'ft_frame_rate': ft_frame_rate, 'fs_frame_rate':fs_frame_rate, \
            'rgb_power':rgb_power, 'current_time':current_time, \
            'temperature':temperature, 'humidity':humidity, 'airflow':airflow, \
            'trial_labels':trial_labels.tolist(), 'trial_structure':trial_structure.tolist(), \
            'n_repeats':n_repeats, 'n_trials':n_trials, \
            'stim_name':stim_name, 'prime_speed':prime_speed, 'probe_speed':probe_speed, 'preprime_duration':preprime_duration, 'prime_duration':prime_duration, 'occlusion_duration':occlusion_duration, 'pause_duration':pause_duration, 'probe_duration':probe_duration, 'iti':iti, 'con_stim_duration':con_stim_duration, 'inc_stim_duration':inc_stim_duration, 'background_color':background_color, \
            'bar_width':bar_width, 'bar_height':bar_height, 'bar_color':bar_color, \
            'occluder_height':occluder_height, \
            'occluder_color':occluder_color, 'start_theta':start_theta, \
            'fix_score_threshold':fix_score_threshold, 'fix_sine_amplitude':fix_sine_amplitude, \
            'fix_sine_period':fix_sine_period, 'fix_window':fix_window, 'fix_max_duration':fix_max_duration}
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

    FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
    FICTRAC_PORT = 33334         # The port used by the server
    FICTRAC_BIN =    "/home/clandinin/lib/fictrac211/bin/fictrac"
    FICTRAC_CONFIG = "/home/clandinin/lib/fictrac211/config_MC.txt"

    # Start stim server
    fs_manager = launch_stim_server(screen)
    if save_history:
        fs_manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=inc_stim_duration+fix_max_duration)
    fs_manager.set_idle_background(background_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    ft_manager = ftu.FtClosedLoopManager(fs_manager=fs_manager, ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG, ft_host=FICTRAC_HOST, ft_port=FICTRAC_PORT)
    ft_manager.sleep(8) #allow fictrac to gather data

    if save_history:
        fix_scores_all = []
        fix_ft_frames_all = []
        trial_start_times = []
        trial_end_times = []
    fix_start_times = []
    fix_end_times = []
    fix_success_all = []

    # Pretend previous trial ended here before trial 0
    t_exp_start = time()
    trial_end_time_neg1 = t_exp_start #timestamp of ITI before first trial

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

        # Fixation variables and queues
        fix_estimated_n_frames = int(np.ceil(ft_frame_rate * fix_max_duration * 1.1))
        fix_score = 0
        fix_frame_cnt = 0
        fix_ft_frames = np.empty(fix_estimated_n_frames)
        fix_scores = np.empty(fix_estimated_n_frames)
        fix_success = True

        if save_history:
            fs_manager.start_saving_history()

        ####################### Confirm Fixation here #########################

        print("===== Start fixation ======")

        ft_manager.set_theta_0()

        fs_manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_traj.to_dict(), background=background_color)
        fs_manager.start_stim()
        t_start_fix = time()

        # Fill the queue of t and theta with initial 2 seconds then continue until iti is up
        while fix_score < fix_score_threshold or time()-t_start_fix < iti: #while the fly is not fixating or witin iti
            ft_frame_num, _, theta_rad = ft_manager.update_theta()
            fix_q_theta_rad.pop(0)
            fix_q_theta_rad.append(theta_rad)

            fix_score = fixation_score(fix_q_theta_rad, fix_sine_template)

            fix_ft_frames[fix_frame_cnt] = ft_frame_num
            fix_scores[fix_frame_cnt] = fix_score

            fix_frame_cnt += 1

            if time() - t_start_fix > fix_max_duration: #If fixation threshold was not met within max duration, quit and enter
                fix_success = False
                break

        t_end_fix = time()
        while abs((time()-t_start_fix)%(fix_sine_period/2)) > 0.1: #100 ms within hitting theta 0
            _ = ft_manager.update_theta()

        fs_manager.stop_stim()

        print(f"===== Fixation {'success' if fix_success else 'fail'} (dur: {(t_end_fix-t_start_fix):.{5}}s)======")

        ####################### End Confirm Fixation #########################

        print(f"===== Trial {t}; type {trial_structure[t]} ======")

        #fs_manager.set_global_theta_offset(0)
        fs_manager.load_stim('MovingPatch', trajectory=bar_traj.to_dict(), background=background_color, hold=True)
        fs_manager.load_stim('MovingPatch', trajectory=occ_traj.to_dict(), background=None, hold=True)

        first_msg = True

        fs_manager.start_stim()
        t_start = time()
        ft_manager.update_theta_for(stim_duration)
        fs_manager.stop_stim()
        t_end = time()

        print(f"===== Trial end (FT dur: {(ts-ts_0)/1000:.{5}}s)======")

        # Save things
        if save_history:
            fs_manager.stop_saving_history()
            fs_manager.set_save_prefix(save_prefix+"_t"+f'{t:03}')
            fs_manager.save_history()

            trial_start_times.append(t_start)
            trial_end_times.append(t_end)

            fix_scores_all.append(fix_scores[:fix_frame_cnt])
            fix_ft_frames_all.append(fix_ft_frames[:fix_frame_cnt])
        fix_start_times.append(t_start_fix)
        fix_end_times.append(t_end_fix)
        fix_success_all.append(fix_success)


    # Burn off the second half of last ITI
    print("===== Start fixation ======")

    _,theta_rad_0,_ = handle_fictrac_data(fictrac_sock, fs_manager, None)

    fs_manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_traj.to_dict(), background=background_color)
    fs_manager.start_stim()
    ft_manager.update_theta_for(iti)

    # close fictrac
    ft_manager.close()

    t_exp_end = time()

    fix_mean_duration = np.mean((np.asarray(fix_end_times) - np.asarray(fix_start_times))[fix_success_all])
    fix_success_rate = np.sum(fix_success_all) / len(fix_success_all)
    print(f"===== Experiment duration: {(t_exp_end-t_exp_start)/60:.{5}} min =====")
    print(f"===== Fixation success: {np.sum(fix_success_all)}/{len(fix_success_all)} ({fix_success_rate*100:.{5}}%) =====")
    print(f"===== Fixation mean duration: {fix_mean_duration:.{5}} sec =====")

    # Plot fictrac summary and save png
    fictrac_files = sorted([x for x in os.listdir(parent_path) if x[0:7]=='fictrac'])[-2:]
    ft_summary_save_fn = os.path.join(parent_path, save_prefix+".png") if save_history else None
    fictrac_utils.plot_ft_session_summary(os.path.join(parent_path, fictrac_files[0]), label=save_prefix, show=(not save_history), save=ft_summary_save_fn, window_size=5)

    if save_history:
        # Move fictrac files
        print ("Moving " + str(len(fictrac_files)) + " fictrac files.")
        for i in range(len(fictrac_files)):
            os.rename(os.path.join(parent_path, fictrac_files[i]), os.path.join(save_path, fictrac_files[i]))

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
        h5f.attrs['experiment_duration'] = t_exp_end-t_exp_start
        h5f.attrs['fix_success_rate'] = fix_success_rate
        h5f.attrs['fix_mean_duration'] = fix_mean_duration
        # trials group
        trials = h5f.require_group('trials')

        # Process through ft_data_handler until it gets to the frame iti before first trial
        start_time_next_trial = trial_start_times[0]
        ft_frame_next = []
        ft_theta_next = []
        ft_timestamps_next = []
        ft_square_next = []

        curr_time = 0
        while curr_time < trial_end_time_neg1:
            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3

        while curr_time < start_time_next_trial:
            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3
            ft_frame_next.append(int(ft_toks[FT_FRAME_NUM_IDX]))
            ft_theta_next.append(float(ft_toks[FT_THETA_IDX]))
            ft_timestamps_next.append(float(ft_toks[FT_TIMESTAMP_IDX]))
            ft_square_next.append(float(ft_toks[FT_SQURE_IDX]))

        # Loop through trials and create trial groups and datasets
        ft_line = ft_data_handler.readline()
        for t in range(n_trials):
            save_dir_prefix = os.path.join(save_path, save_prefix+"_t"+f'{t:03}')

            fs_square = np.loadtxt(save_dir_prefix+'_fs_square.txt')
            fs_timestamps = np.loadtxt(save_dir_prefix+'_fs_timestamps.txt')

            ft_frame = ft_frame_next
            ft_theta = ft_theta_next
            ft_timestamps = ft_timestamps_next
            ft_square = ft_square_next
            ft_frame_next = []
            ft_theta_next = []
            ft_timestamps_next = []
            ft_square_next = []

            if t < n_trials-1:
                start_time_next_trial = trial_start_times[t+1]
            else: #t == n_trials-1
                start_time_next_trial = np.infty

            while ft_line!="" and curr_time < start_time_next_trial:
                ft_toks = ft_line.split(", ")
                curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3
                ft_frame.append(int(ft_toks[FT_FRAME_NUM_IDX]))
                ft_theta.append(float(ft_toks[FT_THETA_IDX]))
                ft_timestamps.append(float(ft_toks[FT_TIMESTAMP_IDX]))
                ft_square.append(float(ft_toks[FT_SQURE_IDX]))
                if curr_time >= trial_end_times[t]:
                    ft_frame_next.append(int(ft_toks[FT_FRAME_NUM_IDX]))
                    ft_theta_next.append(float(ft_toks[FT_THETA_IDX]))
                    ft_timestamps_next.append(float(ft_toks[FT_TIMESTAMP_IDX]))
                    ft_square_next.append(float(ft_toks[FT_SQURE_IDX]))
                ft_line = ft_data_handler.readline()

            # trial
            trial = trials.require_group(f'{t:03}')

            # start time for trial
            trial.attrs['fix_start_time'] = fix_start_times[t]
            trial.attrs['fix_end_time'] = fix_end_times[t]
            trial.attrs['fix_duration'] = fix_end_times[t] - fix_start_times[t]
            trial.attrs['fix_success'] = fix_success_all[t]
            trial.attrs['start_time'] = trial_start_times[t]
            trial.attrs['end_time'] = trial_end_times[t]
            trial.attrs['trial_type'] = str(trial_structure[t])
            trial.create_dataset("fs_square", data=fs_square)
            trial.create_dataset("fs_timestamps", data=fs_timestamps)
            trial.create_dataset("ft_frame", data=ft_frame)
            trial.create_dataset("ft_square", data=ft_square)
            trial.create_dataset("ft_timestamps", data=np.array(ft_timestamps)/1e3)
            trial.create_dataset("ft_theta", data=ft_theta)
            trial.create_dataset("fix_scores", data=fix_scores_all[t])
            trial.create_dataset("fix_ft_frames", data=fix_ft_frames_all[t])

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
            for t in range(0,n_trials,int(np.ceil(n_trials/5))):
                trial = h5f['trials'][f'{t:03}']
                fs_square = trial['fs_square'][()]
                fs_timestamps = trial['fs_timestamps'][()]
                ft_square = trial['ft_square'][()]
                ft_timestamps = trial['ft_timestamps'][()]
                print ("===== Trial " + str(t) + " ======")
                latency_report(fs_timestamps, fs_square, ft_timestamps, ft_square, window_size=1)

        # #Plot sync means
        # fig_square = plt.figure()
        # plt.plot(ft_square)
        # fig_square.show()

    else: #not saving history
        # Delete fictrac files
        print ("Deleting " + str(len(fictrac_files)) + " fictrac files.")
        for i in range(len(fictrac_files)):
            os.remove(os.path.join(parent_path, fictrac_files[i]))


if __name__ == '__main__':
    main()
