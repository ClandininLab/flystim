#!/usr/bin/env python3

import numpy as np
from time import sleep

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory


def main():
    #####################################################
    # part 1: User defined parameters
    #####################################################

    n_repeats = input("Enter number of repeats (default 30): ")#26
    if n_repeats=="":
        n_repeats = 30
    print(n_repeats)

    _ = input("Press enter to continue.")#26

    #####################################################
    # part 2: stimulus definitions
    #####################################################

    # Trial structure
    trial_labels = np.array(["inc_r_inv","inc_l_inv","con_r_inv","con_l_inv",
                             "inc_r_vis","inc_l_vis","con_r_vis","con_l_vis"]) # visible, consistent. 00, 01, 10, 11
    trial_structure = np.random.permutation(np.repeat(trial_labels, n_repeats))
    n_trials = len(trial_structure)

    # Stimulus parameters
    stim_name = "pause"
    prime_speed = 10 #degrees per sec
    probe_speed = 10 #degrees per sec
    preprime_duration = 2 #seconds
    prime_duration = 2 #seconds
    occlusion_duration = 0.5 #seconds
    pause_duration = 1 #seconds
    probe_duration = 1 #seconds
    iti = 3 #seconds

    # Bar start location
    start_theta = -10

    con_stim_duration = preprime_duration + prime_duration + occlusion_duration + probe_duration
    inc_stim_duration = con_stim_duration + pause_duration

    background_color = 0

    bar_width = 15
    bar_height = 150
    bar_color = 1
    #bar_angle = 0

    occluder_height = 170
    occluder_color = 0.5

    #######################
    # Stimulus construction

    center = 0

    # consistent bar trajectory
    con_time = [0, preprime_duration]
    con_x = [start_theta, start_theta]
    inc_time = [0, preprime_duration]
    inc_x = [start_theta, start_theta]

    prime_movement = prime_speed * (prime_duration + occlusion_duration)
    prime_end_theta = start_theta + prime_movement
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
    occlusion_start_theta = start_theta + prime_speed * prime_duration
    occluder_width = prime_speed * occlusion_duration + bar_width # the last term ensures that the bar is completely hidden during the occlusion period
    occluder_loc = occlusion_start_theta + occluder_width/2 - bar_width/2 # the last two terms account for widths of the bar and the occluder, such that the bar is completely hidden during occlusion period
    occluder_time = [0, con_stim_duration]
    occluder_x = [occluder_loc, occluder_loc]

    con_bar_traj_r = list(zip(con_time, (center - np.array(con_x)).tolist()))
    con_bar_traj_l = list(zip(con_time, (center + np.array(con_x)).tolist()))
    inc_bar_traj_r = list(zip(inc_time, (center - np.array(inc_x)).tolist()))
    inc_bar_traj_l = list(zip(inc_time, (center + np.array(inc_x)).tolist()))
    occluder_traj_r = list(zip(occluder_time, (center - np.array(occluder_x)).tolist()))
    occluder_traj_l = list(zip(occluder_time, (center + np.array(occluder_x)).tolist()))

    # Create flystim trajectory objects
    con_bar_r = {'name': 'tv_pairs', 'tv_pairs': con_bar_traj_r, 'kind': 'linear'}
    con_bar_l = {'name': 'tv_pairs', 'tv_pairs': con_bar_traj_l, 'kind': 'linear'}
    inc_bar_r = {'name': 'tv_pairs', 'tv_pairs': inc_bar_traj_r, 'kind': 'linear'}
    inc_bar_l = {'name': 'tv_pairs', 'tv_pairs': inc_bar_traj_l, 'kind': 'linear'}
    occluder_r = {'name': 'tv_pairs', 'tv_pairs': occluder_traj_r, 'kind': 'linear'}
    occluder_l = {'name': 'tv_pairs', 'tv_pairs': occluder_traj_l, 'kind': 'linear'}



    #####################################################
    # part 3: Start experiment
    #####################################################
    
    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))
    manager.set_idle_background(background_color)

    # Loop through trials
    for t in range(n_trials):
        # begin trial

        if trial_structure[t] == "inc_r_inv": # invisible, inconsistent_r. 00, 01, 10, 11
            bar_traj = inc_bar_r
            occ_traj = occluder_r
            occ_color = background_color
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_r_inv": # invisible, consistent_r. 00, 01, 10, 11
            bar_traj = con_bar_r
            occ_traj = occluder_r
            occ_color = background_color
            stim_duration = con_stim_duration
        elif trial_structure[t] == "inc_l_inv": # invisible, inconsistent_l. 00, 01, 10, 11
            bar_traj = inc_bar_l
            occ_traj = occluder_l
            occ_color = background_color
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_l_inv": # invisible, consistent_l. 00, 01, 10, 11
            bar_traj = con_bar_l
            occ_traj = occluder_l
            occ_color = background_color
            stim_duration = con_stim_duration
        elif trial_structure[t] == "inc_r_vis": # invisible, inconsistent_r. 00, 01, 10, 11
            bar_traj = inc_bar_r
            occ_traj = occluder_r
            occ_color = occluder_color
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_r_vis": # invisible, consistent_r. 00, 01, 10, 11
            bar_traj = con_bar_r
            occ_traj = occluder_r
            occ_color = occluder_color
            stim_duration = con_stim_duration
        elif trial_structure[t] == "inc_l_vis": # invisible, inconsistent_l. 00, 01, 10, 11
            bar_traj = inc_bar_l
            occ_traj = occluder_l
            occ_color = occluder_color
            stim_duration = inc_stim_duration
        elif trial_structure[t] == "con_l_vis": # invisible, consistent_l. 00, 01, 10, 11
            bar_traj = con_bar_l
            occ_traj = occluder_l
            occ_color = occluder_color
            stim_duration = con_stim_duration

        print(f"===== Trial {t}; type {trial_structure[t]} ======")

        manager.load_stim(name='ConstantBackground', color=[background_color,background_color,background_color,1], side_length=200)

        # manager.load_stim(name='MovingPatch', width=bar_width, height=bar_height, sphere_radius=2, color=bar_color, theta=bar_traj, phi=0, hold=True)
        # manager.load_stim(name='MovingPatch', width=occluder_width, height=occluder_height, sphere_radius=1, color=occ_color, theta=occ_traj, phi=0, hold=True)
        manager.load_stim(name='MovingPatchOnCylinder', width=bar_width, height=bar_height, cylinder_radius=2, color=bar_color, theta=bar_traj, phi=0, hold=True)
        manager.load_stim(name='MovingPatchOnCylinder', width=occluder_width, height=occluder_height, cylinder_radius=1, color=occ_color, theta=occ_traj, phi=0, hold=True)

        manager.start_stim()
        sleep(stim_duration)

        manager.stop_stim(print_profile=False)

        print("===== Start ITI =====")
        sleep(iti)
        print("===== End ITI =====")

if __name__ == '__main__':
    main()
