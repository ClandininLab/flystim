#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

import logging

from flystim.draw import draw_screens
from flystim.trajectory import RectangleTrajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server

from time import sleep, time
import numpy as np
import math
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
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=0.01, square_loc=(0.59,0.74))#square_side=0.08, square_loc='ur')
    print(screen)

    FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
    FICTRAC_PORT = 33334         # The port used by the server
    RADIUS = 0.0045 # in meters; i.e. 4.5mm

    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: User defined parameters
    #####################################################


    trial_labels = np.array([0,1]) # visible, coherent. 00, 01, 10, 11
    n_repeats = 1
    save_history = False
    save_path = "/home/clandinin/minseung/ballrig_data"
    save_prefix = "200806a_test4"
    save_path = save_path + os.path.sep + save_prefix
    if save_history:
        os .mkdir(save_path)

    genotype = "isoA1-F"
    age = 3

    ft_frame_rate = 250 #Hz, higher
    fs_frame_rate = 120

    speed = 30 #degrees per sec
    presample_duration = 2 #seconds
    sample_duration = 5 #seconds
    preocc_duration = 1 #seconds
    occlusion_duration = 2 #seconds
    postocc_duration = 1 #seconds
    stim_duration = presample_duration + sample_duration + preocc_duration + occlusion_duration + postocc_duration
    iti = 2 #seconds

    ctrl_seed = 0
    ctrl_n_samples = 15 # how many random waypoints should there be for control
    ctrl_noise_scale = 5

    background_color = 0.1

    occluder_height = 150
    occluder_color = 1
    #occluder_angle = 0

    bar_width = 15
    bar_height = 150
    bar_color = 1
    #bar_angle = 0

    params = {'genotype':genotype, 'age':age, 'n_repeats':n_repeats, 'save_path':save_path, 'save_prefix': save_prefix, 'ft_frame_rate': ft_frame_rate, 'speed': speed, 'presample_duration': presample_duration, 'sample_duration': sample_duration, 'preocc_duration': preocc_duration, 'occlusion_duration': occlusion_duration, 'postocc_duration': postocc_duration, 'stim_duration': stim_duration, 'iti': iti, 'ctrl_seed': ctrl_seed, 'ctrl_n_samples': ctrl_n_samples, 'ctrl_noise_scale': ctrl_noise_scale, 'background_color': background_color, 'occluder_height': occluder_height, 'occluder_color': occluder_color, 'bar_width': bar_width, 'bar_height': bar_height, 'bar_color': bar_color}

    #####################################################
    # part 3: stimulus definitions
    #####################################################

    # Trial structure
    trial_structure = np.random.permutation(np.repeat(trial_labels, n_repeats))
    n_trials = len(trial_structure)
    params['n_trials'] = n_trials
    params['trial_structure'] = np.array2string(trial_structure, precision=1, separator=',')

    # Bar start location
    start_theta = 90

    # Experimental bar trajectory
    exp_traj = [(0,start_theta),(presample_duration,start_theta)]

    exp_sample_movement = speed*sample_duration
    exp_sample_end_theta = start_theta-exp_sample_movement
    exp_sample_traj = [(presample_duration+sample_duration, exp_sample_end_theta)]
    exp_traj.extend(exp_sample_traj)

    exp_postsample_movement = speed*(stim_duration-presample_duration-sample_duration)
    exp_end_theta = exp_sample_end_theta - exp_postsample_movement
    exp_postsample_traj = [(stim_duration, exp_end_theta)]
    exp_traj.extend(exp_postsample_traj)

    # Control bar trajectory
    ctrl_traj = [(0,start_theta),(presample_duration,start_theta)]

    np.random.seed(ctrl_seed)
    ctrl_sample_slow_traj = np.linspace(0, start_theta-exp_sample_movement/2, num=ctrl_n_samples-1, endpoint=True)
    ctrl_sample_noise = np.random.normal(0, scale=ctrl_noise_scale, size=ctrl_n_samples-1) # control trajectory is random gaussian noise with n_samples
    ctrl_sample_times = np.linspace(start=presample_duration, stop=presample_duration+sample_duration, num=ctrl_n_samples, endpoint=False) + presample_duration/ctrl_n_samples
    #ctrl_sample_normalizer = exp_sample_movement/np.sum(np.abs(ctrl_sample_noise)) # makes contrl movement (sum of abs) sums to total movement of exp
    #ctrl_sample_traj = list(zip(ctrl_sample_times, start_theta - ctrl_sample_noise*ctrl_sample_normalizer))
    ctrl_sample_traj = list(zip(ctrl_sample_times, start_theta - (ctrl_sample_noise + ctrl_sample_slow_traj)))
    ctrl_sample_end_theta = ctrl_sample_traj[-1][1]
    ctrl_traj.extend(ctrl_sample_traj)

    ctrl_postsample_movement = speed*(stim_duration-presample_duration-sample_duration)
    ctrl_end_theta = ctrl_sample_end_theta - ctrl_postsample_movement
    ctrl_postsample_traj = [(stim_duration, ctrl_end_theta)]
    ctrl_traj.extend(ctrl_postsample_traj)

    params['exp_traj'] = np.array2string(np.array(list(sum(exp_traj, ()))), precision=4, separator=',')
    params['ctrl_traj'] = np.array2string(np.array(list(sum(ctrl_traj, ()))), precision=4, separator=',')

    # Compute location and width of the occluder per specification
    preocc_movement = speed*preocc_duration
    exp_occ_duration_start_theta = exp_sample_end_theta - preocc_movement # of the bar
    ctrl_occ_duration_start_theta = ctrl_sample_end_theta - preocc_movement # of the bar

    occluder_width = occlusion_duration*speed + bar_width # the last term ensures that the bar is completely hidden during the occlusion period
    exp_occluder_loc = exp_occ_duration_start_theta - occluder_width/2 + bar_width/2 # the last two terms account for widths of the bar and the occluder, such that the bar is completely hidden during occlusion period
    exp_occluder_traj = [(0,exp_occluder_loc), (stim_duration,exp_occluder_loc)]
    ctrl_occluder_loc = ctrl_occ_duration_start_theta - occluder_width/2 + bar_width/2
    ctrl_occluder_traj = [(0,ctrl_occluder_loc), (stim_duration,ctrl_occluder_loc)]

    # Create flystim trajectory objects
    exp_bar = RectangleTrajectory(x=exp_traj, y=90, w=bar_width, h=bar_height, color=bar_color)
    exp_occluder_visible = RectangleTrajectory(x=exp_occluder_traj, y=90, w=occluder_width, h=occluder_height, color=occluder_color)
    exp_occluder_invisible = RectangleTrajectory(x=exp_occluder_traj, y=90, w=occluder_width, h=occluder_height, color=background_color)
    ctrl_bar = RectangleTrajectory(x=ctrl_traj, y=90, w=bar_width, h=bar_height, color=bar_color)
    ctrl_occluder_visible = RectangleTrajectory(x=ctrl_occluder_traj, y=90, w=occluder_width, h=occluder_height, color=occluder_color)
    ctrl_occluder_invisible = RectangleTrajectory(x=ctrl_occluder_traj, y=90, w=occluder_width, h=occluder_height, color=background_color)

    with open(save_path+os.path.sep+save_prefix+'_params.txt', "w") as text_file:
        print(json.dumps(params), file=text_file)

    # Set up logging
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        filename="{}/{}.log".format(save_path, save_prefix),
        level=logging.DEBUG
    )

    # Start stim server
    manager = launch_stim_server(screen)
    if save_history:
        manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, stim_duration=stim_duration)
    manager.set_idle_background(background_color)

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
            buffer_size = int(np.ceil(ft_frame_rate * stim_duration*1.1))
            ft_sync_means = np.zeros(buffer_size)
            ft_timestamps = np.zeros(buffer_size)
            ft_posx = np.zeros(buffer_size)
            ft_posy = np.zeros(buffer_size)
            ft_theta = np.zeros(buffer_size)

            while (time() - t_iti_start) < iti:
                _ = fictrac_get_data(fictrac_sock)

            if trial_structure[t] == 0: # invisible, incoherent. 00, 01, 10, 11
                bar_traj = ctrl_bar
                occ_traj = ctrl_occluder_invisible
            elif trial_structure[t] == 1: # invisible, coherent. 00, 01, 10, 11
                bar_traj = exp_bar
                occ_traj = exp_occluder_invisible
            elif trial_structure[t] == 2: # visible, incoherent. 00, 01, 10, 11
                bar_traj = ctrl_bar
                occ_traj = ctrl_occluder_visible
            else: # visible, coherent. 00, 01, 10, 11
                bar_traj = exp_bar
                occ_traj = exp_occluder_visible
            manager.load_stim('MovingPatch', trajectory=bar_traj.to_dict(), background=background_color, hold=True)
            manager.load_stim('MovingPatch', trajectory=occ_traj.to_dict(), background=None, hold=True)

            print ("===== Trial " + str(t) + "; type " + str(trial_structure[t]) + " ======")
            t_start = time()
            manager.start_stim()
            posx_0, posy_0, theta_0, _, _ = fictrac_get_data(fictrac_sock)

            cnt = 0
            while (time() -  t_start) < stim_duration:
                posx, posy, theta_rad, timestamp, sync_mean = fictrac_get_data(fictrac_sock)
                posx = posx - posx_0
                posy = posy - posy_0
                theta_rad = -(theta_rad - theta_0)

                #manager.set_global_fly_pos(posx*RADIUS, posy*RADIUS, 0)
                theta_deg = (theta_rad*180/math.pi) % 360 - 360
                manager.set_global_theta_offset(theta_deg)

                ft_sync_means[cnt] = sync_mean
                ft_timestamps[cnt] = time() #timestamp
                ft_posx[cnt] = posx
                ft_posy[cnt] = posy
                ft_theta[cnt] = theta_rad
                cnt += 1

            manager.stop_stim()
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

            #sleep(2)
            t_iti_start = time()

    p.terminate()
    p.kill()

    #plt.plot(ft_sync_means)
    #plt.show()

if __name__ == '__main__':
    main()
