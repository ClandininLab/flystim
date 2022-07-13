#!/usr/bin/env python3

import sys, os
from cv2 import dft
import numpy as np
import matplotlib.pyplot as plt
import h5py
import logging
from time import sleep, time, strftime, localtime

from flyrpc import multicall

#from flystim1.draw import draw_screens
from flystim1.dlpc350 import make_dlpc350_objects
from flystim1.trajectory import RectangleAnyTrajectory, SinusoidalTrajectory
from flystim1.stim_server import launch_stim_server
from flystim1.bruker import get_bruker_screen
from ftutil.ft_managers import FtManager, FtSocketManager, FtClosedLoopManager

from ballrig_analysis.utils import fictrac_utils
from analyze_fix_stationary import analyze_fix_stationary

#LCR_CTL_PATH = '/home/clandininlab/.local/bin/lcr_ctl'

FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
FICTRAC_PORT = 33334         # The port used by the server
FICTRAC_BIN =    "/home/clandininlab/lib/fictrac211/bin/fictrac"
FICTRAC_CONFIG = "/home/clandininlab/lib/fictrac211/config_210617.txt"
FT_DATA_IDXES = {'ft_frame':0, 'ft_x':14, 'ft_y':15, 'ft_theta':16, 'ft_movement_speed':18, 'ft_fwd':19, 'ft_side':20, 'ft_timestamps':21}
# do not change ft_timestamps

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
    
    sleep_before_stim_min = input("Enter how long to sleep before stim in minutes (default: 0.1): ")#26
    if sleep_before_stim_min=="":
        sleep_before_stim_min = 0.1
    sleep_before_stim = float(sleep_before_stim_min) * 60 # seconds
    print(sleep_before_stim_min)
        
    n_trials = input("Enter number of trials (default 81): ")
    if n_trials=="":
        n_trials = 81
    n_trials = int(n_trials)
    print(n_trials)

    if save_history:
        genotype = input("Enter genotype (default: +; UAS-GC6f/UAS-myr-tdT; nsyb-Gal4/+): ")#"isoD1-F"
        if genotype=="":
            genotype = "+; UAS-GC6f/UAS-myr-tdT; nsyb-Gal4/+"
        print(genotype)
        age = input("Enter age in dpe (default: 5): ") #4
        if age=="":
            age = 5
        print(age)
        temperature = input("Enter temperature (default: 33.7): ") #36.0 #6.30=36.2  6.36=36  6.90=34 6.82=34.3  6.75=34.5(33.7) no hum   #7.10=34  7.00=34.2  6.97=34.5 @ 44%
        if temperature=="":
            temperature = 33.7
        print(temperature)
        humidity = input("Enter humidity (default: 28): ")#26
        if humidity=="":
            humidity = 28
        print(humidity)
        airflow = input("Enter airflow (default: 1.0): ")#26
        if airflow=="":
            airflow = 1.0
        print(airflow)
 
    _ = input("Press enter to continue.")#26

    parent_path = os.getcwd()
    save_prefix = strftime('%Y%m%d_%H%M%S', localtime())
    save_path = os.path.join(parent_path, save_prefix)
    if save_history:
        os.mkdir(save_path)

    rgb_power = [0, 0, 1.0]

    ft_frame_rate = 250 #Hz, higher
    fs_frame_rate = 120

    current_time = strftime('%Y%m%d_%H%M%S', localtime())

    #####################################################
    # part 3: stimulus definitions
    #####################################################

    # Stimulus parameters
    stim_name = "sine"

    background_color = 0

    bar_width = 15
    bar_height = 150
    bar_color = 1
    #bar_angle = 0

    fix_sine_amplitude = 0#15
    fix_sine_period = 2

    fix_start_thetas = [-50, -25, 0, 25, 50]
    fix_duration = 20
    iti = 2
    
    max_duration = (fix_duration + iti) * n_trials

    #######################
    # Stimulus construction

    # Bar start location
    start_theta = np.concatenate([np.random.choice(fix_start_thetas, len(fix_start_thetas), replace=False) for _ in range(int(np.ceil(n_trials/len(fix_start_thetas))))])[:n_trials]

    if save_history:
        params = {'closed_loop':closed_loop, 'genotype':genotype, 'age':age, \
            'save_path':save_path, 'save_prefix': save_prefix, \
            'ft_frame_rate': ft_frame_rate, 'fs_frame_rate':fs_frame_rate, \
            'rgb_power':rgb_power, 'current_time':current_time, \
            'temperature':temperature, 'humidity':humidity, 'airflow':airflow, \
            'stim_name':stim_name, 'background_color':background_color, \
            'bar_width':bar_width, 'bar_height':bar_height, 'bar_color':bar_color, \
            'start_theta':start_theta, 'n_trials':n_trials, \
            'fix_sine_amplitude':fix_sine_amplitude, \
            'fix_sine_period':fix_sine_period, \
            'fix_duration':fix_duration, 'iti':iti, 'fix_start_thetas':fix_start_thetas,
            }


        # Create h5f file
        h5f_path = os.path.join(save_path, save_prefix + '.h5')
        h5f = h5py.File(h5f_path, 'a')
        # params
        for (k,v) in params.items():
            h5f.attrs[k] = v
        # trials group
        trials = h5f.require_group('trials')

    #####################################################################

    # Set up logging
    if save_history:
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename="{}/{}.log".format(save_path, save_prefix),
            level=logging.DEBUG
        )

    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    dlpc350_objects[0].set_current(red=0, green = 0, blue = 1.2)    
    dlpc350_objects[1].set_current(red=0, green = 0, blue = 0.5)
    for dlpc350_object in dlpc350_objects:
         #dlpc350_object.set_current(red=0, green = 0, blue = 1.0)
         dlpc350_object.pattern_mode(fps=120, red=False, green=False, blue=True)
         dlpc350_object.pattern_mode(fps=120, red=False, green=False, blue=True)
    
    sleep(1) # to let lightcrafters think

    # Create screen object
    #bruker_left_screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=(0.11, 0.23), square_loc=(0.89, -1.00), name='Left')
    #bruker_right_screen = Screen(server_number=1, id=2,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=(0.14, 0.22), square_loc=(-0.85, -0.94), name='Right')
    bruker_left_screen = get_bruker_screen('Left', square_pattern='frame')
    bruker_right_screen = get_bruker_screen('Right', square_pattern='frame')
    #aux_screen = Screen(server_number=0, id=0, fullscreen=False, vsync=True, square_side=0, square_loc=(-1, -1), name='Aux')
    #print(screen)
    screens = [bruker_left_screen, bruker_right_screen]#, aux_screen]

    # Start stim server
    fs_manager = launch_stim_server(screens)
    fs_manager.black_corner_square()
    if save_history:
        fs_manager.set_save_history_params(save_history_flag=save_history, save_path=save_path, fs_frame_rate_estimate=fs_frame_rate, save_duration=max_duration)
    fs_manager.set_idle_background(background_color)

    #####################################################
    # part 3: start the loop
    #####################################################

    if closed_loop:
        ft_manager = FtClosedLoopManager(fs_manager=fs_manager, ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG, ft_host=FICTRAC_HOST, ft_port=FICTRAC_PORT, ft_theta_idx=FT_DATA_IDXES['ft_theta'], ft_frame_num_idx=FT_DATA_IDXES['ft_frame'], ft_timestamp_idx=FT_DATA_IDXES['ft_timestamps'])
    else:
        ft_manager = FtManager(ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG)
    ft_manager.sleep(sleep_before_stim) #allow fictrac to gather data

    start_times = []
    end_times = []

    # Pretend previous trial ended here before trial 0
    t_exp_start = time()
    trial_end_time_neg1 = t_exp_start #timestamp of ITI before first trial

    print("===== Start ITI =====")
    ft_manager.sleep(iti)
    print("===== End ITI =====")

    # Loop through trials
    for t in range(n_trials):

        # Fix bar trajectory
        sin_traj = SinusoidalTrajectory(v_0=int(start_theta[t]), amplitude=fix_sine_amplitude, period=fix_sine_period) # period of 1 second
        fixbar_traj = RectangleAnyTrajectory(x=sin_traj, y=90, w=bar_width, h=bar_height, color=bar_color)

        if save_history:
            fs_manager.start_saving_history()


        ft_manager.set_pos_0(theta_0=None, x_0=0, y_0=0)

        print(f"===== Trial {t}: start_theta={start_theta[t]} ======")

        fs_manager.load_stim('MovingPatchAnyTrajectory', trajectory=fixbar_traj.to_dict(), background=background_color)
        fs_manager.start_corner_square()
        fs_manager.start_stim()
        t_start_fix = time()

        while time()-t_start_fix < fix_duration:
            _ = ft_manager.update_pos()

        t_end_fix = time()

        fs_manager.stop_stim()
        fs_manager.black_corner_square()

        print("===== Start ITI =====")
        ft_manager.sleep(iti)
        print("===== End ITI =====")

        start_times.append(t_start_fix)
        end_times.append(t_end_fix)

        # Save things
        if save_history:
            fs_manager.stop_saving_history()
            fs_manager.set_save_prefix(save_prefix+"_t"+f'{t:03}')
            fs_manager.save_history()
            
            # Save start and end times for trial in HDF file
            trial = trials.require_group(f'{t:03}')
            trial.attrs['start_time'] = start_times[t]
            trial.attrs['end_time'] = end_times[t]
            trial.attrs['start_theta'] = start_theta[t]

    # close fictrac
    ft_manager.close()
    t_exp_end = time()

    print(f"===== Experiment duration: {(t_exp_end-t_exp_start)/60:.{5}} min =====")


    # Plot fictrac summary and save png
    fictrac_files = sorted([x for x in os.listdir(parent_path) if x[0:7]=='fictrac'])
    fictrac_data_fn = sorted([x for x in fictrac_files if x.endswith('.dat')])[-1]
    
    ft_summary_save_fn = os.path.join(parent_path, save_prefix+".png") if save_history else None
    fictrac_utils.plot_ft_session_summary(os.path.join(parent_path, fictrac_data_fn), label=save_prefix, show=(not save_history), save=ft_summary_save_fn, window_size=5)

    if save_history:
        # Write experiment duration to the HDF file
        h5f.attrs['experiment_duration'] = t_exp_end-t_exp_start

        # Move fictrac files
        print ("Moving/removing fictrac files.")
        for x in fictrac_files:
            os.rename(os.path.join(parent_path, x), os.path.join(save_path, x))

        # Move Fictrac summary
        os.rename(os.path.join(parent_path, save_prefix+".png"), os.path.join(save_path, save_prefix+".png"))

        # Open up fictrac file
        ft_data_handler = open(os.path.join(save_path, fictrac_data_fn), 'r')
        
        # Process through ft_data_handler until it gets to the frame iti before first trial
        start_time_next_trial = start_times[0]
        ft_data_next = dict.fromkeys(FT_DATA_IDXES.keys(), [])

        curr_time = 0
        while curr_time < trial_end_time_neg1:
            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_DATA_IDXES['ft_timestamps']])/1e3

        while curr_time < start_time_next_trial:
            ft_line = ft_data_handler.readline()
            ft_toks = ft_line.split(", ")
            curr_time = float(ft_toks[FT_DATA_IDXES['ft_timestamps']])/1e3
            for k in FT_DATA_IDXES.keys():
                ft_data_next[k].append(float(ft_toks[FT_DATA_IDXES[k]]))

        # Loop through trials and create trial groups and datasets
        ft_line = ft_data_handler.readline()
        for t in range(n_trials):
            save_dir_prefix = os.path.join(save_path, save_prefix+"_t"+f'{t:03}')

            fs_timestamps = np.loadtxt(save_dir_prefix+'_fs_timestamps.txt')

            ft_data = ft_data_next
            ft_data_next = dict.fromkeys(FT_DATA_IDXES.keys(), [])

            if t < n_trials-1:
                start_time_next_trial = start_times[t+1]
            else: #t == n_trials-1
                start_time_next_trial = np.infty

            while ft_line!="" and curr_time < start_time_next_trial:
                ft_toks = ft_line.split(", ")
                curr_time = float(ft_toks[FT_DATA_IDXES['ft_timestamps']])/1e3
                for k in FT_DATA_IDXES.keys():
                    ft_data[k].append(float(ft_toks[FT_DATA_IDXES[k]]))
                if curr_time >= end_times[t]:
                    for k in FT_DATA_IDXES.keys():
                        ft_data_next[k].append(float(ft_toks[FT_DATA_IDXES[k]]))
                ft_line = ft_data_handler.readline()

            # trial
            trial = trials.require_group(f'{t:03}')
            trial.create_dataset("fs_timestamps", data=fs_timestamps)
            for k in FT_DATA_IDXES.keys():
                if k == 'ft_timestamps':
                    trial.create_dataset(k, data=np.array(ft_data[k])/1e3)
                else:
                    trial.create_dataset(k, data=ft_data[k])

        ft_data_handler.close()
        h5f.close()

        # Delete flystim txt output files
        fs_txt_files = [x for x in os.listdir(save_path) if x.startswith(save_prefix) and x.endswith('.txt')]
        for txt_fn in fs_txt_files:
            os.remove(os.path.join(save_path, txt_fn))

        # Run quick analysis post experiment
        _=analyze_fix_stationary(h5f_path, front_region=[-15,15])

        # Move hdf5 file out to parent path
        os.rename(os.path.join(save_path, save_prefix + '.h5'), os.path.join(parent_path, save_prefix + '.h5'))

    else: #not saving history
        # Delete fictrac files
        print ("Deleting " + str(len(fictrac_files)) + " fictrac files.")
        for i in range(len(fictrac_files)):
            os.remove(os.path.join(parent_path, fictrac_files[i]))
        
        # Delete fictrac summary
        os.remove(os.path.join(parent_path, save_prefix+".png"))

if __name__ == '__main__':
    main()
