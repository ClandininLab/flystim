#!/usr/bin/env python3

import sys, os
import numpy as np
import matplotlib.pyplot as plt
import h5py
import logging
from time import sleep, time, strftime, localtime
import itertools

#from flystim1.draw import draw_screens
from flystim1.dlpc350 import make_dlpc350_objects
from flystim1.screen import Screen
from flystim1.stim_server import launch_stim_server
from flystim1.ballrig_util import latency_report, make_tri_list

from ftutil.ft_managers import FtManager

from ballrig_analysis.utils import fictrac_utils

FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
FICTRAC_PORT = 33334         # The port used by the server
FICTRAC_BIN =    "/home/clandinin/lib/fictrac211/bin/fictrac"
FICTRAC_CONFIG = "/home/clandinin/lib/fictrac211/config_MC.txt"
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
        do_fictrac = True
        save_history = True
    elif len(sys.argv) > 1 and sys.argv[1] == "ft":
        do_fictrac = True
        save_history = False
    else:
        do_fictrac = False
        save_history = False

    if save_history:
        genotype = input("Enter genotype (e.g. isoD1-F): ")#"isoD1-F"
        if genotype=="":
            genotype = "isoD1-F"
        print(genotype)
        age = input("Enter age in dpe (e.g. 4): ") #4
        if age=="":
            age = 4
        print(age)
        temperature = input("Enter temperature (e.g. 35.0): ") #36.0 #6.30=36.2  6.36=36  6.90=34 6.82=34.3  6.75=34.5(33.7) no hum   #7.10=34  7.00=34.2  6.97=34.5 @ 44%
        if temperature=="":
            temperature = 35.0
        print(temperature)
        humidity = input("Enter humidity (e.g. 26): ")#26
        if humidity=="":
            humidity = 26
        print(humidity)
        airflow = input("Enter airflow (e.g. 0.8): ")#26
        if airflow=="":
            airflow = 0.8
        print(airflow)

    n_repeats = input("Enter number of repeats (e.g. 40): ")#26
    if n_repeats=="":
        n_repeats = 40
    else:
        n_repeats = int(n_repeats)
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

    random_offset = True
    duration_1 = 5
    duration_2 = 5
    iti = 5
    iti_color = 0.5
    temporal_frequency = 1 #Hz
    spatial_period = 60 #degrees
    rate = temporal_frequency * spatial_period
    stim_duration = duration_1 + duration_2

    high_max_lum = 1
    high_min_lum = 0
    low_max_lum = 0.625
    low_min_lum = 0.375
    signs = [-1, 1]
    high_contrast_firsts = [False, True]
    trial_types = list(itertools.product(signs, high_contrast_firsts))
    n_trial_types = len(trial_types)
    trial_sample_idxes = np.random.permutation(np.repeat(np.arange(n_trial_types), n_repeats))
    n_trials = n_trial_types * n_repeats
    #offsets = np.random.uniform(0,spatial_period,n_trials) if random_offset else np.zeros(n_trials) #complete random uniform sampling
    offsets = np.random.permutation(np.linspace(0, spatial_period, n_trials, False)) + np.random.uniform(0, spatial_period/n_trials) #even spacing + random sub-offset, randomly ordered

    current_time = strftime('%Y%m%d_%H%M%S', localtime())

    if save_history:
        params = {'genotype':genotype, 'age':age, 'temperature':temperature, \
        'humidity':humidity, 'airflow':airflow, 'n_repeats':n_repeats, \
        'save_path':save_path, 'save_prefix': save_prefix, \
        'ft_frame_rate': ft_frame_rate, 'fs_frame_rate':fs_frame_rate, \
        'rgb_power':rgb_power, 'duration_1':duration_1,'duration_2':duration_2, \
        'iti':iti,'iti_color':iti_color,'temporal_frequency':temporal_frequency, \
        'spatial_period':spatial_period,'high_max_lum':high_max_lum, \
        'high_min_lum':high_min_lum,'low_max_lum':low_max_lum, \
        'low_min_lum':low_min_lum,'signs':signs, \
        'high_contrast_firsts':high_contrast_firsts,'trial_types':trial_types, \
        'n_trial_types':n_trial_types,'trial_sample_idxes':trial_sample_idxes.tolist(),\
        'n_trials':n_trials, 'offsets':offsets.tolist(), \
        'current_time':current_time, 'temperature':temperature, 'humidity':humidity}


    #####################################################################

    # Set up logging
    if save_history:
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename="{}/{}.log".format(save_path, save_prefix),
            level=logging.DEBUG
        )

    # Set lightcrafter and GL environment settings
    # os.system('/home/clandinin/miniconda3/bin/lcr_ctl --fps 120 --red_current ' + str(rgb_power[0]) + ' --blue_current ' + str(rgb_power[2]) + ' --green_current ' + str(rgb_power[1]))
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.set_current(red=0, green = 0, blue = 1.0)
         dlpc350_object.pattern_mode(fps=120)
         dlpc350_object.pattern_mode(fps=120)

    # Create screen object
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=0.01, square_loc=(0.59,0.74))#square_side=0.08, square_loc='ur')
    #print(screen)

    # Start stim server
    fs_manager = launch_stim_server(screen)
    if save_history:
        fs_manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=stim_duration+iti*2)
    fs_manager.set_idle_background(iti_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    if do_fictrac:
        ft_manager = FtManager(ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG)
        ft_manager.sleep(8) #allow fictrac to gather data

    if save_history:
        trial_start_times = []
        trial_start_ft_frames = []
        trial_end_times = []
        trial_end_ft_frames = []

    # Pretend previous trial ended here before trial 0
    trial_end_time_neg1 = time() #timestamp of ITI before first trial
    sleep(iti/2)

    # Loop through trials
    for t in range(n_trials):
        # begin trial

        sign, high_contrast_first = trial_types[trial_sample_idxes[t]]
        signed_rate = sign*rate
        if high_contrast_first:
            max_lum_1,min_lum_1 = high_max_lum,high_min_lum
            max_lum_2,min_lum_2 = low_max_lum,low_min_lum
        else:
            max_lum_1,min_lum_1 = low_max_lum,low_min_lum
            max_lum_2,min_lum_2 = high_max_lum,high_min_lum

        if save_history:
            fs_manager.start_saving_history()

        sleep(iti/2)

        print(f"===== Trial {t}; {'<-' if sign==1 else '->'} {'High First' if high_contrast_first else 'Low First'} ======")
        fs_manager.load_stim(name='SineGrating', period=spatial_period, rate=sign*rate, color=max_lum_1, background=min_lum_1, angle=0, offset=offsets[t]) #RotatingBars for square grating
        fs_manager.start_stim()
        t_start = time()
        sleep(duration_1)
        fs_manager.update_stim(color=max_lum_2, background=min_lum_2)
        sleep(duration_2)
        fs_manager.stop_stim()
        t_end = time()

        print(f"===== Trial end (dur: {t_end-t_start:.{5}}s)======")
        sleep(iti/2)
        if save_history:
            fs_manager.stop_saving_history()
            fs_manager.set_save_prefix(save_prefix+"_t"+f'{t:03}')
            fs_manager.save_history()

            trial_start_times.append(t_start)
            trial_end_times.append(t_end)

    # Burn off the second half of last ITI
    sleep(iti/2)

    if do_fictrac:
        # close fictrac
        ft_manager.close()

        # Plot fictrac summary and save png
        fictrac_files = sorted([x for x in os.listdir(parent_path) if x[0:7]=='fictrac'])[-2:]
        ft_summary_save_fn = os.path.join(parent_path, save_prefix+".png") if save_history else None
        fictrac_utils.plot_ft_session_summary(os.path.join(parent_path, fictrac_files[0]), label=save_prefix, show=False, save=ft_summary_save_fn, window_size=5)

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
            # trials group
            trials = h5f.require_group('trials')

            # Process through ft_data_handler until it gets to the first trial's start frame
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
                save_prefix_with_trial = save_prefix+"_t"+f'{t:03}'
                save_dir_prefix = os.path.join(save_path, save_prefix_with_trial)

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
                trial.attrs['start_time'] = trial_start_times[t]
                trial.attrs['end_time'] = trial_end_times[t]
                trial.create_dataset("fs_square", data=fs_square)
                trial.create_dataset("fs_timestamps", data=fs_timestamps)
                trial.create_dataset("ft_frame", data=ft_frame)
                trial.create_dataset("ft_square", data=ft_square)
                trial.create_dataset("ft_timestamps", data=np.array(ft_timestamps)/1e3)
                trial.create_dataset("ft_theta", data=ft_theta)

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

        else: #not saving history
            # Delete fictrac files
            print ("Deleting " + str(len(fictrac_files)) + " fictrac files.")
            for i in range(len(fictrac_files)):
                os.remove(os.path.join(parent_path, fictrac_files[i]))


if __name__ == '__main__':
    main()
