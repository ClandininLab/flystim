#!/usr/bin/env python3

#!/usr/bin/env python3

# Example client program that walks through all available stimuli.
import sys, os
import numpy as np
import matplotlib.pyplot as plt
import h5py
import logging
from time import sleep, time, strftime, localtime
import math
import random

from flystim1.dlpc350 import make_dlpc350_objects
from flystim1.trajectory import RectangleAnyTrajectory
from flystim1.screen import Screen
from flystim1.stim_server import launch_stim_server
from flystim1.ballrig_util import latency_report, make_tri_list, shortest_deg_to_0
from ftutil.ft_managers import FtManager

from ballrig_analysis.utils import fictrac_utils

#from multi_sensory_traj import loomingList, loomingEdge #Note: loomingList is for randomizing the stimulus projection, loomingEdge is for designing looming patch with parameters
# loomtraj = loomingEdge(cx=0, cy=90, wStart=loom_diam_start, hStart=loom_diam_start, wEnd=loom_diam_end, hEnd=loom_diam_end, T=loom_duration, c=lm)
# cx, cy: center of looming patch; wStart, hStart: width and height of the looming patch when starting
# wEnd, hEnd: width and height of the looming patch at the end
# T: length of looming presentation, in seconds
# c: brightness of the patch

##### TODO:
# 3. Make usable on the downstairs screens
# 4. Add initial just loom w/o friends stimulus
##########

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

friend_traj_dir = '/home/clandinin/ilana/Trajectories'


class Friend:
    def __init__(self, theta_zone, phi_zone, rad_mean, rad_std, traj_fn, exp_duration, color, dist_window, c_bg=1, speed_factor=1):
        self.theta_zone = theta_zone # Tuple of theta boundaries. e.g. (-45, 45)
        self.phi_zone = phi_zone # Tuple of phi boundaries.

        spawn_theta = np.random.uniform(*theta_zone)
        spawn_phi = np.random.uniform(*phi_zone)
        radius = np.random.normal(rad_mean, rad_std)
        self.spawn_theta = spawn_theta
        self.spawn_phi = spawn_phi
        self.radius = radius

        traj_np = np.genfromtxt(traj_fn, delimiter=',')

        traj_duration = traj_np[-1, 0]
        n_repeat_traj = int(np.ceil(exp_duration / traj_duration))

        n_traj_ts = traj_np.shape[0]
        friend_t = np.zeros(n_traj_ts * n_repeat_traj)
        friend_x = np.zeros(n_traj_ts * n_repeat_traj) # using zeros here instead of empty is important bv of 5 lines below.
        friend_y = np.zeros(n_traj_ts * n_repeat_traj)
        friend_a = np.zeros(n_traj_ts * n_repeat_traj)
        friend_c =  np.ones(n_traj_ts * n_repeat_traj) * color
        for i in range(n_repeat_traj):
            friend_t[i * n_traj_ts: (i + 1) * n_traj_ts] = traj_np[:, 0] + traj_np[-1, 0] * i  # in seconds
            friend_x[i * n_traj_ts: (i + 1) * n_traj_ts] = np.rad2deg(np.arctan((traj_np[:, 1] + friend_x[i * n_traj_ts]) / dist_window))
            friend_y[i * n_traj_ts: (i + 1) * n_traj_ts] = np.rad2deg(np.arctan((traj_np[:, 2] + friend_y[i * n_traj_ts]) / dist_window))
            friend_a[i * n_traj_ts: (i + 1) * n_traj_ts] = np.mod(traj_np[:, 3], 360)  # in degrees

        friend_x += spawn_theta
        friend_y += spawn_phi

        ##### Wrap around walls
        theta_zone_width = np.abs(theta_zone[1] - theta_zone[0])
        for i in range(len(friend_x)):
            if friend_x[i] > np.max(theta_zone):
                friend_x[i:] -= theta_zone_width
                friend_c[i-1:i+1] = c_bg
            elif friend_x[i] < np.min(theta_zone):
                friend_x[i:] += theta_zone_width
                friend_c[i-1:i+1] = c_bg

        phi_zone_height = np.abs(phi_zone[1] - phi_zone[0])
        for i in range(len(friend_y)):
            if friend_y[i] > np.max(phi_zone):
                friend_y[i:] -= phi_zone_height
                friend_c[i-1:i+1] = c_bg
            elif friend_y[i] < np.min(phi_zone):
                friend_y[i:] += phi_zone_height
                friend_c[i-1:i+1] = c_bg
        #####

        friend_t *= speed_factor

        theta_traj = list(zip(friend_t, friend_x))
        phi_traj = list(zip(friend_t, friend_y))
        angle_traj = list(zip(friend_t, friend_a))
        color_traj = list(zip(friend_t, friend_c))

        width = np.rad2deg(np.arctan(radius/dist_window))
        height = np.rad2deg(np.arctan(radius*1.5/dist_window))

        self.flystim_traj = RectangleAnyTrajectory(x=theta_traj, y=phi_traj, w=width, h=height,
                                                   angle=angle_traj, color=color_traj)


def pol2cart(amp, angle):
    theta = amp * np.cos(angle)
    phi = amp * np.sin(angle)
    return(list(zip(theta.tolist(), phi.tolist())))


def main():

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

    n_trials = input("Enter number of trials (default 20): ")#26
    if n_trials=="":
        n_trials = 20
    n_trials = int(n_trials)
    print(n_trials)

    n_friends = input("Enter number of friends (default 10): ")#26
    if n_friends=="":
        n_friends = 10
    n_friends = int(n_friends)
    print(n_friends)

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
    # part 2: stimulus definitions
    #####################################################

    ##### User defined inputs:
    dist_window = 0.015 # meters # do 0.02 on the rig

    c_bg =1.0  # background brightness
    c_lm=0 # brightness of the looming patch

    iti_uniform_lo = 13
    ini_uniform_hi = 16
    loom_duration = 0.5
    loom_diam_start = 10
    loom_diam_end = 150
    loom_dt = 0.00001

    friends_duration = 5   #duration in which only friends are shown

    c_friends = 0.2  #brightness of friends
    n_friends_per_zone = n_friends ### TODO: maybe change this
    friends_rad_mean = 0.002
    friends_rad_std = 0

    friends_theta_zones = [(-135, 135)] #[(10, 45), (-45, -10)]
    friends_phi_zone = (45, 135)
    n_zones = len(friends_theta_zones)
    n_friends = n_friends_per_zone * n_zones


    ##### Calculate stuff based on inputs

    # 0. Sample ITIs
    itis = np.random.uniform(iti_uniform_lo, ini_uniform_hi, n_trials)
    exp_duration = friends_duration + np.sum(itis) + loom_duration * n_trials

    # 1. Make friends
    # paths
    friend_traj_paths = [os.path.join(friend_traj_dir, x) for x in os.listdir(friend_traj_dir) if x.endswith('.csv')]
    n_paths = len(friend_traj_paths)
    friend_traj_paths *= int(np.ceil(n_friends / n_paths))
    #random.shuffle(friend_traj_paths)

    # zone assignments
    theta_zone_assignments = friends_theta_zones * n_friends_per_zone

    friends = []
    for i in range(n_friends):
        friend = Friend(theta_zone=theta_zone_assignments[i], phi_zone=friends_phi_zone, rad_mean=friends_rad_mean,
                        rad_std=friends_rad_std, traj_fn=friend_traj_paths[i], exp_duration=exp_duration, color=c_friends,
                        dist_window=dist_window, c_bg=c_bg)
        friends.append(friend)

    # 2 Make looms
    fs_trial_start_times = []
    fs_trial_end_times   = []
    diam_traj = [(0,0), (friends_duration,0)]
    last_t = friends_duration
    for t in range(n_trials):
        fs_trial_start_times.append(last_t)
        diam_traj.extend([(last_t-loom_dt, 0), (last_t, loom_diam_start)])
        last_t += loom_duration
        diam_traj.extend([(last_t, loom_diam_end), (last_t+loom_dt, 0)])
        fs_trial_end_times.append(last_t)
        last_t += itis[t]
    diam_traj.append((last_t, 0))
    loomtraj = RectangleAnyTrajectory(x=0, y=90, angle=0, color=c_lm, w=diam_traj)


    if save_history:
        params = {'genotype':genotype, 'age':age, \
            'save_path':save_path, 'save_prefix': save_prefix, \
            'ft_frame_rate': ft_frame_rate, 'fs_frame_rate':fs_frame_rate, \
            'rgb_power':rgb_power, 'current_time':current_time, \
            'temperature':temperature, 'humidity':humidity, 'airflow':airflow, \
            'n_trials':n_trials} ### TODO: Fill this out

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
        fs_manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=exp_duration)
    fs_manager.set_idle_background(c_bg)

    #####################################################
    # part 3: start the loop
    #####################################################

    ft_manager = FtManager(ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG)
    ft_manager.sleep(8) #allow fictrac to gather data

    for f in range(n_friends):
        bg_color = c_bg if f==0 else None
        fs_manager.load_stim('MovingEllipseAnyTrajectory', trajectory=friends[f].flystim_traj.to_dict(), background=bg_color, hold=True)

    fs_manager.load_stim('MovingEllipseAnyTrajectory', trajectory=loomtraj.to_dict(), background=None, hold=True)

    # 7. Start experiment
    t_exp_start = time()
    print("===== Start experiment ======")
    fs_manager.start_stim()
    ft_manager.sleep(exp_duration)
    fs_manager.stop_stim()
    print("===== End experiment ======")

    # close fictrac
    ft_manager.close()

    t_exp_end = time()

    # Plot fictrac summary and save png
    fictrac_files = sorted([x for x in os.listdir(parent_path) if x[0:7]=='fictrac'])[-2:]
    ft_summary_save_fn = os.path.join(parent_path, save_prefix+".png") if save_history else None
    fictrac_utils.plot_ft_session_summary(os.path.join(parent_path, fictrac_files[0]), label=save_prefix, show=(not save_history), save=ft_summary_save_fn, window_size=5)

    if save_history:
        # Compute epoch times for trial starts and ends
        trial_start_times = t_exp_start + np.asarray(fs_trial_start_times)
        trial_end_times = t_exp_start + np.asarray(fs_trial_end_times)

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
        h5f.attrs['experiment_duration'] = t_exp_end-t_exp_start
        # trials group
        trials = h5f.require_group('trials')

        # Process through ft_data_handler until it gets to the frame iti before first trial
        start_time_next_trial = trial_start_times[0]
        ft_frame_next = []
        ft_theta_next = []
        ft_x_next = []
        ft_y_next = []
        ft_timestamps_next = []
        ft_square_next = []

        curr_time = 0
        while curr_time < t_exp_start:
            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3

        while curr_time < start_time_next_trial:
            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3
            ft_frame_next.append(int(ft_toks[FT_FRAME_NUM_IDX]))
            ft_theta_next.append(float(ft_toks[FT_THETA_IDX]))
            ft_x_next.append(float(ft_toks[FT_X_IDX]))
            ft_y_next.append(float(ft_toks[FT_Y_IDX]))
            ft_timestamps_next.append(float(ft_toks[FT_TIMESTAMP_IDX]))
            ft_square_next.append(float(ft_toks[FT_SQURE_IDX]))

        # Loop through trials and create trial groups and datasets
        ft_line = ft_data_handler.readline()
        for t in range(n_trials):
            save_dir_prefix = os.path.join(save_path, save_prefix+"_t"+f'{t:03}')

            # fs_square = np.loadtxt(save_dir_prefix+'_fs_square.txt')
            # fs_timestamps = np.loadtxt(save_dir_prefix+'_fs_timestamps.txt')

            ft_frame = ft_frame_next
            ft_theta = ft_theta_next
            ft_x = ft_x_next
            ft_y = ft_y_next
            ft_timestamps = ft_timestamps_next
            ft_square = ft_square_next
            ft_frame_next = []
            ft_theta_next = []
            ft_x_next = []
            ft_y_next = []
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
                ft_x.append(float(ft_toks[FT_X_IDX]))
                ft_y.append(float(ft_toks[FT_Y_IDX]))
                ft_timestamps.append(float(ft_toks[FT_TIMESTAMP_IDX]))
                ft_square.append(float(ft_toks[FT_SQURE_IDX]))
                if curr_time >= trial_end_times[t]:
                    ft_frame_next.append(int(ft_toks[FT_FRAME_NUM_IDX]))
                    ft_theta_next.append(float(ft_toks[FT_THETA_IDX]))
                    ft_x_next.append(float(ft_toks[FT_X_IDX]))
                    ft_y_next.append(float(ft_toks[FT_Y_IDX]))
                    ft_timestamps_next.append(float(ft_toks[FT_TIMESTAMP_IDX]))
                    ft_square_next.append(float(ft_toks[FT_SQURE_IDX]))
                ft_line = ft_data_handler.readline()

            # trial
            trial = trials.require_group(f'{t:03}')

            trial.attrs['start_time'] = trial_start_times[t]
            trial.attrs['end_time'] = trial_end_times[t]
            trial.create_dataset("ft_frame", data=ft_frame)
            trial.create_dataset("ft_square", data=ft_square)
            trial.create_dataset("ft_timestamps", data=np.array(ft_timestamps)/1e3)
            trial.create_dataset("ft_theta", data=ft_theta)
            # trial.create_dataset("fs_square", data=fs_square)
            # trial.create_dataset("fs_timestamps", data=fs_timestamps)

        ft_data_handler.close()
        h5f.close()

        # Delete flystim txt output files
        fs_txt_files = [x for x in os.listdir(save_path) if x.startswith(save_prefix) and x.endswith('.txt')]
        for txt_fn in fs_txt_files:
            os.remove(os.path.join(save_path, txt_fn))

        # Move hdf5 file out to parent path
        os.rename(os.path.join(save_path, save_prefix + '.h5'), os.path.join(parent_path, save_prefix + '.h5'))

    else: #not saving history
        # Delete fictrac files
        print ("Deleting " + str(len(fictrac_files)) + " fictrac files.")
        for i in range(len(fictrac_files)):
            os.remove(os.path.join(parent_path, fictrac_files[i]))



if __name__ == '__main__':
    main()
