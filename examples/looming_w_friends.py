#!/usr/bin/env python3

#!/usr/bin/env python3

# Example client program that walks through all available stimuli.
from math import pi, sqrt
from time import sleep, time
from datetime import datetime

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleAnyTrajectory, Trajectory
import itertools

import numpy as np

from multi_sensory_traj import loomingList, loomingEdge #Note: loomingList is for randomizing the stimulus projection, loomingEdge is for designing looming patch with parameters

def pol2cart(amp, angle):
    theta = amp * np.cos(angle)
    phi = amp * np.sin(angle)
    return(list(zip(theta.tolist(), phi.tolist())))


def main():
    bg =1.0  # background brightness
    lm=0 # brightness of the looming patch

    n_trials = 1
    iti_uniform_lo = 3
    ini_uniform_hi = 6
    loom_duration = 2
    loomtraj = loomingEdge(cx=0, cy=90, wStart=10, hStart=10, wEnd=100, hEnd=100, T=loom_duration, c=lm)
    # cx, cy: center of looming patch; wStart, hStart: width and height of the looming patch when starting
    # wEnd, hEnd: width and height of the looming patch at the end
    # T: length of looming presentation, in seconds
    # c: brightness of the patch


    n_friends_per_zone = 10
    friends_speed_mean = 8
    friends_speed_std = 3
    friends_rad_mean = 1
    friends_rad_std = 0

    # Define where flies will spawn
    #friends_spawn_theta_zones = [(45, 135), (-135, -45)]
    #friends_spawn_phi_zone = (45, 135)
    friends_spawn_theta_zones = [(10, 45), (-45, -10)]
    friends_spawn_phi_zone = (75, 105)
    n_spawn_zones = len(friends_spawn_theta_zones)

    n_friends = n_friends_per_zone * n_spawn_zones

    # 1. Randomly choose spawn locations
    spawn_thetas = list(itertools.chain(*[np.random.uniform(*zone, n_friends_per_zone) for zone in friends_spawn_theta_zones]))
    spawn_phis = np.random.uniform(*friends_spawn_phi_zone, n_friends)

    # 2. Randomly choose sizes
    radii = np.random.normal(friends_rad_mean, friends_rad_std, n_friends)

    # 3. Randomly choose velocity
    speeds = np.random.normal(friends_speed_mean, friends_speed_std, n_friends)
    angle = np.random.uniform(0,2*pi, n_friends)
    velocities = pol2cart(speeds, angle) #in radians


    ##### TODO:
    # 0. Function for generating flystim trajectories from (time, x, y, heading) trajectories, perhaps from bigrig
    # 1. For now, generate some fake (time, x, y, heading) trajectories of random walk
    # 2. Get big rig trajectories from Avery
    # 3. Figure out how to show friends AND loom concurrently


    #targets =

    #print(spawn_thetas)
    #print(spawn_phis)

    # 4. Create trajectories
    friends_traj = []
    for f in range(n_friends):
        theta_traj = Trajectory([(0, spawn_thetas[f]), (2, spawn_thetas[f]+velocities[f][0]*2)])
        phi_traj = Trajectory([(0, spawn_phis[f]), (2, spawn_phis[f]+velocities[f][1]*2)])
        friend_traj = RectangleAnyTrajectory(x=theta_traj, y=phi_traj, w=radii[f]+1, h=radii[f], angle=np.rad2deg(angle[f]), color=lm)
        friends_traj.append(friend_traj)



    screen = Screen(server_number=1, id=1,fullscreen=True)

    manager = launch_stim_server(screen)
    manager.set_idle_background(bg)
    sleep(3)

    for f in range(n_friends):
        bg_color = bg if f==0 else None
        manager.load_stim('MovingEllipseAnyTrajectory', trajectory=friends_traj[f].to_dict(), background=bg_color, hold=True)

    manager.start_stim()
    sleep(3)
    #manager.stop_stim()
    #sleep(5 * 1)

    for t in range(n_trials):
        print('looping')

        manager.load_stim('MovingPatch', trajectory=loomtraj, background = None, hold=True)

        #manager.start_stim()
        sleep(loom_duration)

        #manager.stop_stim()
        iti = np.random.uniform(iti_uniform_lo, ini_uniform_hi)
        sleep(iti)
    

if __name__ == '__main__':
    main()
