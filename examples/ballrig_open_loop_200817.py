#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

import logging
import PySpin

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


def main():
    # Set lightcrafter and GL environment settings
    os.system('/home/clandinin/miniconda3/bin/lcr_ctl --fps 120 --blue_current 2.1 --green_current 2.1')
    os.system('bash /home/clandinin/flystim/src/flystim/examples/closed_loop_GL_env_set.sh')

    #Camera boundaries
    CAM_WIDTH = 752
    CAM_HEIGHT = 616
    CAM_OFFSET_X = 328
    CAM_OFFSET_Y = 336

    try:
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        assert cam_list.GetSize() == 1
        cam = cam_list[0]
        cam.Init()
        nodemap = cam.GetNodeMap()
        node_width = PySpin.CIntegerPtr(nodemap.GetNode('Width'))
        if PySpin.IsAvailable(node_width) and PySpin.IsWritable(node_width):
            node_width.SetValue(CAM_WIDTH)
            print('Cam Width set to %i...' % node_width.GetValue())
        else:
            print('Cam Width not available...')
        node_height = PySpin.CIntegerPtr(nodemap.GetNode('Height'))
        if PySpin.IsAvailable(node_height) and PySpin.IsWritable(node_height):
            node_height.SetValue(CAM_HEIGHT)
            print('Cam Height set to %i...' % node_height.GetValue())
        else:
            print('Cam Height not available...')
        node_offset_x = PySpin.CIntegerPtr(nodemap.GetNode('OffsetX'))
        if PySpin.IsAvailable(node_offset_x) and PySpin.IsWritable(node_offset_x):
            node_offset_x.SetValue(CAM_OFFSET_X)
            print('Cam OffsetX set to %i...' % node_offset_x.GetValue())
        else:
            print('Cam OffsetX not available...')
        node_offset_y = PySpin.CIntegerPtr(nodemap.GetNode('OffsetY'))
        if PySpin.IsAvailable(node_offset_y) and PySpin.IsWritable(node_offset_y):
            node_offset_y.SetValue(CAM_OFFSET_Y)
            print('Cam OffsetY set to %i...' % node_offset_y.GetValue())
        else:
            print('Cam OffsetY not available...')
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)


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
        os.mkdir(save_path)

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


    background_color = 0.1
    bar_width = 15
    bar_height = 150
    bar_color = 1

    params = {'genotype':genotype, 'age':age, 'n_repeats':n_repeats, 'save_path':save_path, 'save_prefix': save_prefix, 'speed': speed, 'presample_duration': presample_duration, 'sample_duration': sample_duration, 'preocc_duration': preocc_duration, 'occlusion_duration': occlusion_duration, 'postocc_duration': postocc_duration, 'stim_duration': stim_duration, 'iti': iti, 'background_color': background_color, 'bar_width': bar_width, 'bar_height': bar_height, 'bar_color': bar_color}

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
    bar_traj = [(0,start_theta),(presample_duration,start_theta)]

    exp_sample_movement = speed*sample_duration
    exp_sample_end_theta = start_theta-exp_sample_movement
    exp_sample_traj = [(presample_duration+sample_duration, exp_sample_end_theta)]
    bar_traj.extend(exp_sample_traj)
    exp_postsample_movement = speed*(stim_duration-presample_duration-sample_duration)
    exp_end_theta = exp_sample_end_theta - exp_postsample_movement
    exp_postsample_traj = [(stim_duration, exp_end_theta)]
    bar_traj.extend(exp_postsample_traj)
    params['exp_traj'] = np.array2string(np.array(list(sum(bar_traj, ()))), precision=4, separator=',')

    # Create flystim trajectory objects
    bar = RectangleTrajectory(x=bar_traj, y=90, w=bar_width, h=bar_height, color=bar_color)

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

    t_iti_start = time()
    for t in range(n_trials):
        # begin trial
        manager.load_stim('MovingPatch', trajectory=bar.to_dict(), background=background_color, hold=True)

        print ("===== Trial " + str(t) + "; type " + str(trial_structure[t]) + " ======")
        t_start = time()
        manager.start_stim()
        sleep(stim_duration)
        manager.stop_stim()

        #sleep(2)
        t_iti_start = time()

    #plt.plot(ft_sync_means)
    #plt.show()

if __name__ == '__main__':
    main()
