#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

import logging
#import PySpin

from flystim.draw import draw_screens
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server
from flystim.util import latency_report

from time import sleep, time, strftime, localtime
import numpy as np
import math
import itertools
import socket
import os, subprocess
import json

import matplotlib.pyplot as plt

def dir_to_tri_list(dir):

    north_w = 3.0e-2
    side_w = 2.96e-2

    # set coordinates as a function of direction
    if dir == 'w':
       # set screen width and height
       h = 2.94e-2
       pts = [
            ((+0.4925, -0.3750), (-north_w/2, -side_w/2, -h/2)),
            ((+0.4800, -0.6975), (-north_w/2, +side_w/2, -h/2)),
            ((+0.2875, -0.6800), (-north_w/2, +side_w/2, +h/2)),
            ((+0.2925, -0.3550), (-north_w/2, -side_w/2, +h/2))
        ]
    elif dir == 'n':
       # set screen width and height
       h = 3.29e-2
       pts = [
            ((+0.1700, +0.5700), (-north_w/2, +side_w/2, -h/2)),
            ((+0.1700, +0.2675), (+north_w/2, +side_w/2, -h/2)),
            ((-0.0275, +0.2675), (+north_w/2, +side_w/2, +h/2)),
            ((-0.0300, +0.5675), (-north_w/2, +side_w/2, +h/2))
        ]

    elif dir == 'e':
        # set screen width and height
        h = 3.18e-2
        pts = [
            ((-0.1600, -0.3275), (+north_w/2, +side_w/2, -h/2)),
            ((-0.1500, -0.6200), (+north_w/2, -side_w/2, -h/2)),
            ((-0.3575, -0.6500), (+north_w/2, -side_w/2, +h/2)),
            ((-0.3675, -0.3500), (+north_w/2, +side_w/2, +h/2))
        ]
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(*pts)

def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def fictrac_get_data(sock):
    data = sock.recv(1024)

    # Decode received data
    line = data.decode('UTF-8')
    endline = line.find("\n")
    line = line[:endline]
    toks = line.split(", ")

    #logging.debug("Received from fictrac socket: %s", line)

    # Fixme: sometimes we read more than one line at a time,
    # should handle that rather than just dropping extra data...
    if ((len(toks) < 7) | (toks[0] != "FT")):
        logging.warning("Bad read, too few tokens: %s", line)
        return fictrac_get_data(sock)
        #continue

    if len(toks) > 7:
        logging.warning("Bad read, too many tokens: %s", line)
        return fictrac_get_data(sock)

    posx = float(toks[1])
    posy = float(toks[2])
    heading = float(toks[3])
    timestamp = float(toks[4])
    sync_mean = float(toks[5])

    return (posx, posy, heading, timestamp, sync_mean)


def main():
    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: User defined parameters
    #####################################################

    save_history = True
    save_path = "/home/clandinin/minseung/ballrig_data/omer"
    save_prefix = "200820_test06"
    save_path = save_path + os.path.sep + save_prefix
    if save_history:
        os.mkdir(save_path)

    genotype = "isoA1-F"
    age = 3

    ft_frame_rate = 250 #Hz, higher
    fs_frame_rate = 120

    n_repeats = 1

    duration_1 = 5
    duration_2 = 5
    iti = 5
    iti_color = 0.5
    temporal_frequency = 1 #Hz
    spatial_frequency = 60 #degrees
    rate = temporal_frequency * spatial_frequency
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

    current_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())

    params = {'genotype':genotype, 'age':age, 'n_repeats':n_repeats, 'save_path':save_path, 'save_prefix': save_prefix, 'ft_frame_rate': ft_frame_rate, 'fs_frame_rate':fs_frame_rate,'duration_1':duration_1,'duration_2':duration_2,'iti':iti,'iti_color':iti_color,'temporal_frequency':temporal_frequency,'spatial_frequency':spatial_frequency,'rate':rate,'high_max_lum':high_max_lum,'high_min_lum':high_min_lum,'low_max_lum':low_max_lum,'low_min_lum':low_min_lum,'signs':signs,'high_contrast_firsts':high_contrast_firsts,'trial_types':trial_types,'n_trial_types':n_trial_types,'trial_sample_idxes':trial_sample_idxes,'n_trials':n_trials, 'current_time':current_time}
    if save_history:
        with open(save_path+os.path.sep+save_prefix+'_params.txt', "w") as text_file:
            print(json.dumps(params), file=text_file)

    #####################################################################

    # Set up logging
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        filename="{}/{}.log".format(save_path, save_prefix),
        level=logging.DEBUG
    )

    # Set lightcrafter and GL environment settings
    os.system('/home/clandinin/miniconda3/bin/lcr_ctl --fps 120 --blue_current 2.1 --green_current 2.1')
    os.system('bash /home/clandinin/flystim/src/flystim/examples/closed_loop_GL_env_set.sh')

    # Create screen object
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=True, square_side=0.01, square_loc=(0.59,0.74))#square_side=0.08, square_loc='ur')
    #print(screen)

    FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
    FICTRAC_PORT = 33334         # The port used by the server
    RADIUS = 0.0045 # in meters; i.e. 4.5mm

    # Start stim server
    manager = launch_stim_server(screen)
    if save_history:
        manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, stim_duration=stim_duration)
    manager.set_idle_background(iti_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    #p = subprocess.Popen(["/home/clandinin/fictrac_test/bin/fictrac","/home/clandinin/fictrac_test/config1.txt"], start_new_session=True)
    p = subprocess.Popen(["/home/clandinin/fictrac_test/bin/fictrac","/home/clandinin/fictrac_test/config_smaller_window.txt","-v","ERR"], start_new_session=True)
    sleep(2)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as fictrac_sock:
        fictrac_sock.connect((FICTRAC_HOST, FICTRAC_PORT))

        t_iti_start = time()
        for t in range(n_trials):
            # begin trial
            ft_sync_means = []
            ft_timestamps = []
            ft_posx = []
            ft_posy = []
            ft_theta = []

            sign, high_contrast_first = trial_types[trial_sample_idxes[t]]
            signed_rate = sign*rate
            if high_contrast_first:
                max_lum_1,min_lum_1 = high_max_lum,high_min_lum
                max_lum_2,min_lum_2 = low_max_lum,low_min_lum
            else:
                max_lum_1,min_lum_1 = low_max_lum,low_min_lum
                max_lum_2,min_lum_2 = high_max_lum,high_min_lum

            while (time() - t_iti_start) < iti:
                _ = fictrac_get_data(fictrac_sock)


            print ("===== Trial " + str(t) + "; " + ("<-" if sign==1 else "->") + (" High First" if high_contrast_first else " Low First") + " ======")
            manager.load_stim(name='SineGrating', period=spatial_frequency, rate=sign*rate, color=max_lum_1, background=min_lum_1, angle=0, offset=0)
            t_start = time()
            posx_0, posy_0, theta_0, _, _ = fictrac_get_data(fictrac_sock)

            manager.start_stim()
            while (time() -  t_start) < duration_1:
                posx, posy, theta_rad, timestamp, sync_mean = fictrac_get_data(fictrac_sock)
                ft_sync_means.append(sync_mean)
                ft_timestamps.append(time())
                ft_posx.append(posx - posx_0)
                ft_posy.append(posy - posy_0)
                ft_theta.append(-(theta_rad - theta_0))

            manager.update_stim(color=max_lum_2, background=min_lum_2)
            while (time() -  t_start) < stim_duration:
                posx, posy, theta_rad, timestamp, sync_mean = fictrac_get_data(fictrac_sock)
                ft_sync_means.append(sync_mean)
                ft_timestamps.append(time())
                ft_posx.append(posx - posx_0)
                ft_posy.append(posy - posy_0)
                ft_theta.append(-(theta_rad - theta_0))

            manager.stop_stim()
            t_iti_start = time()
            while (time() - t_iti_start) < iti:
                posx, posy, theta_rad, timestamp, sync_mean = fictrac_get_data(fictrac_sock)
                ft_sync_means.append(sync_mean)
                ft_timestamps.append(time())
                ft_posx.append(posx - posx_0)
                ft_posy.append(posy - posy_0)
                ft_theta.append(-(theta_rad - theta_0))

            # Save things
            if save_history:
                save_prefix_with_trial = save_prefix+"_t"+f'{t:03}'
                manager.set_save_prefix(save_prefix_with_trial)
                manager.save_history()
                np.savetxt(save_path+os.path.sep+save_prefix_with_trial+'_ft_square.txt', np.array(ft_sync_means), delimiter='\n')
                np.savetxt(save_path+os.path.sep+save_prefix_with_trial+'_ft_timestamps.txt', np.array(ft_timestamps), delimiter='\n')
                np.savetxt(save_path+os.path.sep+save_prefix_with_trial+'_ft_posx.txt', np.array(ft_posx), delimiter='\n')
                np.savetxt(save_path+os.path.sep+save_prefix_with_trial+'_ft_posy.txt', np.array(ft_posy), delimiter='\n')
                np.savetxt(save_path+os.path.sep+save_prefix_with_trial+'_ft_theta.txt', np.array(ft_theta), delimiter='\n')

    p.terminate()
    p.kill()

    plt.plot(ft_sync_means)
    plt.show()

    if save_history:
        def load(fpath):
            with open(fpath, 'r') as handler:
                return np.array([float(line) for line in handler])
        for t in range(0,n_trials,int(np.ceil(n_trials/5))):
            save_prefix_with_trial = save_prefix+"_t"+f'{t:03}'
            fs_square = load(save_path+os.path.sep+save_prefix_with_trial+'_fs_square.txt')
            fs_timestamp = load(save_path+os.path.sep+save_prefix_with_trial+'_fs_timestamps.txt')
            ft_square = load(save_path+os.path.sep+save_prefix_with_trial+'_ft_square.txt')
            ft_timestamp = load(save_path+os.path.sep+save_prefix_with_trial+'_ft_timestamps.txt')
            print ("===== Trial " + str(t) + " ======")
            latency_report(fs_timestamp, fs_square, ft_timestamp, ft_square, window_size=1)


if __name__ == '__main__':
    main()
