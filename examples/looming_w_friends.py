#!/usr/bin/env python3

#!/usr/bin/env python3

# Example client program that walks through all available stimuli.
import os
from math import pi, sqrt
from time import sleep
import random

from flystim1.stim_server import launch_stim_server
from flystim1.screen import Screen
from flystim1.trajectory import RectangleAnyTrajectory

import numpy as np

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

    ##### User defined inputs:
    dist_window = 0.2 # meters # do 0.02 on the rig

    c_bg =1.0  # background brightness
    c_lm=0 # brightness of the looming patch

    n_trials = 20
    iti_uniform_lo = 13
    ini_uniform_hi = 16
    loom_duration = 0.5
    loom_diam_start = 10
    loom_diam_end = 100
    loom_dt = 0.00001

    friends_duration = 5   #duration in which only friends are shown

    c_friends = 0.3  #brightness of friends
    n_friends_per_zone = 10
    friends_rad_mean = 0.002
    friends_rad_std = 0

    friends_theta_zones = [(-20, 20)] #[(10, 45), (-45, -10)]
    friends_phi_zone = (75, 105)
    n_zones = len(friends_theta_zones)
    n_friends = n_friends_per_zone * n_zones

    friend_traj_dir = '/Users/Ilana/repos/stim_scripts/trajectories/chosen'

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
    diam_traj = [(0,0), (friends_duration,0)]
    last_t = friends_duration
    for t in range(n_trials):
        diam_traj.extend([(last_t-loom_dt, 0), (last_t, loom_diam_start)])
        last_t += loom_duration
        diam_traj.extend([(last_t, loom_diam_end), (last_t+loom_dt, 0)])
        last_t += itis[t]
    diam_traj.append((last_t, 0))
    loomtraj = RectangleAnyTrajectory(x=0, y=90, angle=0, color=c_lm, w=diam_traj)

    ##### Launch flystim server and load stimuli
    screen = Screen(server_number=1, id=1,fullscreen=True)
    manager = launch_stim_server(screen)
    manager.set_idle_background(c_bg)
    sleep(1)

    for f in range(n_friends):
        bg_color = c_bg if f==0 else None
        manager.load_stim('MovingEllipseAnyTrajectory', trajectory=friends[f].flystim_traj.to_dict(), background=bg_color, hold=True)

    manager.load_stim('MovingEllipseAnyTrajectory', trajectory=loomtraj.to_dict(), background=None, hold=True)

    # 7. Start experiment
    manager.start_stim()
    sleep(exp_duration)
    manager.stop_stim()
    

if __name__ == '__main__':
    main()
