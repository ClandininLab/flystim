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

def dir_to_tri_list(dir):

    north_w = 2.956e-2
    side_w = 2.96e-2

    # set coordinates as a function of direction
    if dir == 'w':
       # set screen width and height
       h = 3.10e-2
       pts = [
            ((+0.4900, -0.3400), (-north_w/2, -side_w/2, -h/2)),
            ((+0.4900, -0.6550), (-north_w/2, +side_w/2, -h/2)),
            ((+0.2850, -0.6550), (-north_w/2, +side_w/2, +h/2)),
            ((+0.2850, -0.3400), (-north_w/2, -side_w/2, +h/2))
        ]
    elif dir == 'n':
       # set screen width and height
       h = 3.29e-2
       pts = [
            ((+0.1850, +0.5850), (-north_w/2, +side_w/2, -h/2)),
            ((+0.1850, +0.2800), (+north_w/2, +side_w/2, -h/2)),
            ((-0.0200, +0.2800), (+north_w/2, +side_w/2, +h/2)),
            ((-0.0200, +0.5850), (-north_w/2, +side_w/2, +h/2))
        ]

    elif dir == 'e':
        # set screen width and height
        h = 3.40e-2
        pts = [
            ((-0.1350, -0.3550), (+north_w/2, +side_w/2, -h/2)),
            ((-0.1350, -0.6550), (+north_w/2, -side_w/2, -h/2)),
            ((-0.3500, -0.6550), (+north_w/2, -side_w/2, +h/2)),
            ((-0.3500, -0.3550), (+north_w/2, +side_w/2, +h/2))
        ]
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(*pts)

def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

ft_buffer = ""
def fictrac_get_data(sock):
    global ft_buffer

    # if not select.select([sock], [], [])[0]:
    #     return fictrac_get_data(sock)
    ready = select.select([sock], [], [])[0]
    if ready:
        data = sock.recv(4098)
    else:
        return fictrac_get_data(sock)

    # Decode received data
    ogline = data.decode('UTF-8')
    line = ft_buffer + ogline
    endline = line.rfind("\n")
    if endline == -1: # there is no linebreak
        startline = line.rfind("FT")
        if startline != -1: #there is line start
            line = line[startline:]
        ft_buffer += line # add (perhaps) trimmed line to buffer
        logging.warning("No line end: %s", line)
        return fictrac_get_data(sock)
    else: # there is a linebreak
        ft_buffer = line[endline:] # write everything after linebreak to the buffer
        line = line[:endline]
        startline = line.rfind("FT")
        if startline == -1: #there is no line start... this shouldn't happen bc we have a buffer
            logging.warning("No line start: %s", line)
            return fictrac_get_data(sock)
        else: # start line exists as well as a linebreak, so trim to the start
            line = line[startline:]

    # There is a complete line!
    toks = line.split(", ")

    if len(toks) != 27:
        logging.warning("This should not happen: %s", str(len(toks)) + ' ' + line)
        return fictrac_get_data(sock)

    frame_num = int(toks[FT_FRAME_NUM_IDX+1])
    heading = float(toks[FT_THETA_IDX+1])
    ts = float(toks[FT_TIMESTAMP_IDX+1])#

    return (frame_num, heading, ts)#

def handle_fictrac_data(fictrac_sock, manager, theta_rad_0):
    frame_num, theta_rad_1, ts = fictrac_get_data(fictrac_sock)#
    theta_rad = theta_rad_1 - theta_rad_0 if theta_rad_0 is not None else 0
    theta_deg = degrees(theta_rad)
    manager.set_global_theta_offset(theta_deg)
    return frame_num, theta_rad_1, ts#

def load_txt(fpath):
    with open(fpath, 'r') as handler:
        return np.array([float(line) for line in handler])

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
        closed_loop = input("Closed loop? (default: True): ")#"isoD1-F"
        if closed_loop=="":
            closed_loop = True
        else:
            closed_loop = closed_loop.lower() in ['true', '1', 't', 'y', 'yes']
        print(closed_loop)
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
    duration_in_min = input("Enter duration in minutes (e.g. 40): ")#26
    if duration_in_min=="":
        duration_in_min = 40
    duration_in_min = float(duration_in_min)
    print(duration_in_min)

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
    manager = launch_stim_server(screen)
    if save_history:
        manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=inc_stim_duration+fix_max_duration)
    manager.set_idle_background(background_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    p = subprocess.Popen([FICTRAC_BIN, FICTRAC_CONFIG, "-v","ERR"], start_new_session=True)
    sleep(2)

    if closed_loop:
        fictrac_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fictrac_sock.bind((FICTRAC_HOST, FICTRAC_PORT))
        fictrac_sock.setblocking(0)

    if save_history:
        manager.start_saving_history()

    ####################### Confirm Fixation here #########################

    print("===== Start fixation ======")


    manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_traj.to_dict(), background=background_color)
    if closed_loop:
        _,theta_rad_0,_ = handle_fictrac_data(fictrac_sock, manager, None)
    manager.start_stim()
    t_start = time()

    # Fill the queue of t and theta with initial 2 seconds then continue until iti is up
    if closed_loop:
        while time()-t_start < duration:
            _ = handle_fictrac_data(fictrac_sock, manager, theta_rad_0)
    else:
        sleep(duration)

    manager.stop_stim()
    t_end = time()

    # Save things
    if save_history:
        manager.stop_saving_history()
        manager.set_save_prefix(save_prefix)
        manager.save_history()

    # close fictrac
    if closed_loop:
        fictrac_sock.close()
    p.terminate()
    p.kill()

    fix_mean_score = np.mean(fix_scores)
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

        while curr_time < t_end:
            save_dir_prefix = os.path.join(save_path, save_prefix)
            fs_square = load_txt(save_dir_prefix+'_fs_square.txt')
            fs_timestamps = load_txt(save_dir_prefix+'_fs_timestamps.txt')

            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_TIMESTAMP_IDX])/1e3
            ft_frame.append(int(ft_toks[FT_FRAME_NUM_IDX]))
            ft_theta.append(float(ft_toks[FT_THETA_IDX]))
            ft_timestamps.append(float(ft_toks[FT_TIMESTAMP_IDX]))
            ft_square.append(float(ft_toks[FT_SQURE_IDX]))

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
