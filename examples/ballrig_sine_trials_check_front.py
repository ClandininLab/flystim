#!/usr/bin/env python3

import sys, os
import numpy as np
import matplotlib.pyplot as plt
import h5py
import logging
from time import time, strftime, localtime

#from flystim.draw import draw_screens
from flystim1.dlpc350 import make_dlpc350_objects
from flystim1.trajectory import RectangleAnyTrajectory, SinusoidalTrajectory
from flystim1.screen import Screen
from flystim1.stim_server import launch_stim_server
from flystim1.ballrig_util import latency_report, make_tri_list
from ftutil.ft_managers import FtClosedLoopManager

from ballrig_analysis.utils import fictrac_utils

FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
FICTRAC_PORT = 33334         # The port used by the server
FICTRAC_BIN =    "/home/clandinin/lib/fictrac211/bin/fictrac"
FICTRAC_CONFIG = "/home/clandinin/lib/fictrac211/config_MC.txt"
FT_FRAME_NUM_IDX = 0
FT_X_IDX = 14
FT_Y_IDX = 15
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

def modulo_degrees_between_m180_p180(angle_degrees):
    '''
    Convert arbitrary angle in degrees (any real number) to that between -180
    and +180 degrees.
    '''
    angle_new = angle_degrees % 360.0
    if angle_new > 180.0:
        angle_new = angle_new - 360.0
    return angle_new

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
        genotype = input("Enter genotype (default isoD1-F): ")#"isoD1-F"
        if genotype=="":
            genotype = "isoD1-F"
        print(genotype)
        age = input("Enter age in dpe (default 5): ") #4
        if age=="":
            age = 5
        print(age)
        temperature = input("Enter temperature (default 33.7): ") #36.0 #6.30=36.2  6.36=36  6.90=34 6.82=34.3  6.75=34.5(33.7) no hum   #7.10=34  7.00=34.2  6.97=34.5 @ 44%
        if temperature=="":
            temperature = 33.7
        print(temperature)
        humidity = input("Enter humidity (default 28): ")#26
        if humidity=="":
            humidity = 28
        print(humidity)
        airflow = input("Enter airflow (default 0.8): ")#26
        if airflow=="":
            airflow = 0.8
        print(airflow)

    n_trials = input("Enter number of trials (default 160): ")#26
    if n_trials=="":
        n_trials = 160
    n_trials = int(n_trials)
    print(n_trials)

    n_trials_fp_beginning = input("Enter number of trials (default 10): ")#26
    if n_trials_fp_beginning=="":
        n_trials_fp_beginning = 10
    n_trials_fp_beginning = int(n_trials_fp_beginning)
    print(n_trials_fp_beginning)

    n_trials_fp_end = input("Enter number of trials (default 10): ")#26
    if n_trials_fp_end=="":
        n_trials_fp_end = 10
    n_trials_fp_end = int(n_trials_fp_end)
    print(n_trials_fp_end)

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
    stim_name = "sine_trials"

    background_color = 0

    bar_width = 15
    bar_height = 150
    bar_color = 1
    #bar_angle = 0

    fix_score_threshold = .9
    fix_sine_amplitude = 15
    fix_sine_period = 1
    fix_window = 2 #seconds
    fix_min_duration = 2
    fix_max_duration = 25

    fix_front_region = [-60, 60]
    fix_front_threshold = .9

    iti = 2

    #######################
    # Stimulus construction
    
    n_trials_total = n_trials + n_trials_fp_beginning + n_trials_fp_end

    # Bar start location
    start_theta = 0

    # Fix bar trajectory
    sin_traj = SinusoidalTrajectory(amplitude=fix_sine_amplitude, period=fix_sine_period) # period of 1 second
    fixbar_traj = RectangleAnyTrajectory(x=sin_traj, y=90, w=bar_width, h=bar_height, color=bar_color)
    fixbar_fp_traj = RectangleAnyTrajectory(x=sin_traj, y=90, w=bar_width, h=bar_height, color=background_color)
    fix_sine_template = sin_traj.eval_at(np.arange(0, fix_window + fix_sine_period, 1/ft_frame_rate))
    fix_q_len = ft_frame_rate*fix_window
    fix_q_theta_rad = [0] * fix_q_len
    fix_q_front = [False] * fix_q_len

    if save_history:
        params = {'genotype':genotype, 'age':age, \
            'save_path':save_path, 'save_prefix': save_prefix, \
            'ft_frame_rate': ft_frame_rate, 'fs_frame_rate':fs_frame_rate, \
            'rgb_power':rgb_power, 'current_time':current_time, \
            'temperature':temperature, 'humidity':humidity, 'airflow':airflow, \
            'n_trials':n_trials, 'n_trials_fp_beginning':n_trials_fp_beginning, \
            'n_trials_fp_end':n_trials_fp_end, 'start_theta':start_theta, \
            'stim_name':stim_name, 'background_color':background_color, \
            'bar_width':bar_width, 'bar_height':bar_height, 'bar_color':bar_color, \
            'fix_score_threshold':fix_score_threshold, 'fix_sine_amplitude':fix_sine_amplitude, \
            'fix_sine_period':fix_sine_period, 'fix_window':fix_window, \
            'fix_min_duration':fix_min_duration, 'fix_max_duration':fix_max_duration, \
            'fix_front_region':fix_front_region, 'fix_front_threshold':fix_front_threshold,
            }

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
         dlpc350_object.set_current(red=rgb_power[0], green = rgb_power[1], blue = rgb_power[2])
         dlpc350_object.pattern_mode(fps=120, red=True if rgb_power[0]>0 else False, green=True if rgb_power[1]>0 else False, blue=True if rgb_power[2]>0 else False)
         dlpc350_object.pattern_mode(fps=120, red=True if rgb_power[0]>0 else False, green=True if rgb_power[1]>0 else False, blue=True if rgb_power[2]>0 else False)

    # Create screen object
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=0.01, square_loc=(0.59,0.74), square_pattern='random')#square_side=0.08,coh_bar_traj_r square_loc='ur')
    #print(screen)

    # Start stim server
    fs_manager = launch_stim_server(screen)
    if save_history:
        fs_manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=fix_max_duration+iti)
    fs_manager.set_idle_background(background_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    ft_manager = FtClosedLoopManager(fs_manager=fs_manager, ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG, ft_host=FICTRAC_HOST, ft_port=FICTRAC_PORT, ft_theta_idx=FT_THETA_IDX, ft_frame_num_idx=FT_FRAME_NUM_IDX, ft_timestamp_idx=FT_TIMESTAMP_IDX)
    ft_manager.sleep(8) #allow fictrac to gather data


    fix_scores_all = []
    fix_front_passes_all = []
    fix_ft_frames_all = []
    fix_start_times = []
    fix_end_times = []
    fix_success_all = []

    # Pretend previous trial ended here before trial 0
    t_exp_start = time()
    trial_end_time_neg1 = t_exp_start #timestamp of ITI before first trial

    print("===== Start ITI =====")
    ft_manager.sleep(iti)
    print("===== End ITI =====")

    # Loop through trials
    for t in range(n_trials_total):

        # Fixation variables and queues
        fix_estimated_n_frames = int(np.ceil(ft_frame_rate * fix_max_duration * 1.1))
        fix_score = 0
        fix_frame_cnt = 0
        fix_ft_frames = np.empty(fix_estimated_n_frames)
        fix_scores = np.empty(fix_estimated_n_frames)
        fix_front_passes = np.empty(fix_estimated_n_frames, dtype=bool)
        fix_success = True

        if save_history:
            fs_manager.start_saving_history()


        ft_manager.set_pos_0(theta_0=None, x_0=0, y_0=0)

        print(f"===== Trial {t} ======")

        if t < n_trials_fp_beginning or t >= n_trials_fp_beginning + n_trials:
            fs_manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_fp_traj.to_dict(), background=background_color)
        else:
            fs_manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_traj.to_dict(), background=background_color)
        fs_manager.start_stim()
        t_start_fix = time()

        # Fill the queue of t and theta with initial 2 seconds then continue until fix_min_duration is up
        while time()-t_start_fix < fix_min_duration or fix_score < fix_score_threshold or not fix_front_pass: #while the fly is not fixating or witin fix_min_duration or wasn't facing forward
            ft_frame_num, _, [theta_rad] = ft_manager.update_pos()
            fix_ft_frames[fix_frame_cnt] = ft_frame_num

            fix_q_theta_rad.pop(0)
            fix_q_theta_rad.append(theta_rad)
            fix_score = fixation_score(fix_q_theta_rad, fix_sine_template)
            fix_scores[fix_frame_cnt] = fix_score

            # Check whether bar is in the front. TODO: wraparound.
            #np.rad2deg(thera_rad)
            theta_deg = np.rad2deg(theta_rad)
            theta_wrapped = modulo_degrees_between_m180_p180(theta_deg)
            fix_q_front.pop(0)
            fix_q_front.append(theta_wrapped > fix_front_region[0] and theta_wrapped <= fix_front_region[1])
            fix_front_pass = np.mean(fix_q_front) > fix_front_threshold
            fix_front_passes[fix_frame_cnt] = fix_front_pass

            fix_frame_cnt += 1

            if time() - t_start_fix > fix_max_duration: #If fixation threshold was not met within max duration, quit and enter
                fix_success = False
                break

        t_end_fix = time()
        while abs((time()-t_start_fix)%(fix_sine_period/2)) > 0.1: #100 ms within hitting theta 0
            _,_,[theta_rad] = ft_manager.update_pos(update_theta=True)

        fs_manager.stop_stim()

        print(f"===== Fixation {'success' if fix_success else 'fail'} (dur: {(t_end_fix-t_start_fix):.{5}}s)======")

        print("===== Start ITI =====")
        ft_manager.sleep(iti)
        print("===== End ITI =====")

        fix_start_times.append(t_start_fix)
        fix_end_times.append(t_end_fix)
        fix_success_all.append(fix_success)
        fix_scores_all.append(fix_scores[:fix_frame_cnt])
        fix_front_passes_all.append(fix_front_passes[:fix_frame_cnt])

        # Save things
        if save_history:
            fs_manager.stop_saving_history()
            fs_manager.set_save_prefix(save_prefix+"_t"+f'{t:03}')
            fs_manager.save_history()


            fix_ft_frames_all.append(fix_ft_frames[:fix_frame_cnt])

    # close fictrac
    ft_manager.close()

    t_exp_end = time()

    fix_mean_duration = np.mean((np.asarray(fix_end_times) - np.asarray(fix_start_times))[fix_success_all])
    fix_success_rate = np.sum(fix_success_all) / len(fix_success_all)
    print(f"===== Fixation success: {np.sum(fix_success_all)}/{len(fix_success_all)} ({fix_success_rate*100:.{5}}%) =====")
    print(f"===== Fixation mean duration: {fix_mean_duration:.{5}} sec =====")
    print(f"===== Experiment duration: {(t_exp_end-t_exp_start)/60:.{5}} min =====")

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
        start_time_next_trial = fix_start_times[0]
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
                start_time_next_trial = fix_start_times[t+1]
            else: #t == n_trials-1
                start_time_next_trial = np.infty

            while ft_line!="" and curr_time < start_time_next_trial:
                ft_toks = ft_line.split(", ")
                curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3
                ft_frame.append(int(ft_toks[FT_FRAME_NUM_IDX]))
                ft_theta.append(float(ft_toks[FT_THETA_IDX]))
                ft_timestamps.append(float(ft_toks[FT_TIMESTAMP_IDX]))
                ft_square.append(float(ft_toks[FT_SQURE_IDX]))
                if curr_time >= fix_end_times[t]:
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
            trial.create_dataset("fix_scores", data=fix_scores_all[t])
            trial.create_dataset("fix_front_passes", data=fix_front_passes_all[t])
            trial.create_dataset("fix_ft_frames", data=fix_ft_frames_all[t])

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
                latency_report(fs_timestamps, fs_square, ft_timestamps, ft_square, window_size=3)

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
