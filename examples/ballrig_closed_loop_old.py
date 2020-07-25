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

import matplotlib.pyplot as plt

def dir_to_tri_list(dir):

    north_w = 3.0e-2
    side_w = 2.96e-2

    # set coordinates as a function of direction
    if dir == 'w':
       # set screen width and height
       h = 2.94e-2
       pts = [
            ((+0.4602, -0.3159), (-north_w/2, -side_w/2, -h/2)),
            ((+0.4502, -0.6347), (-north_w/2, +side_w/2, -h/2)),
            ((+0.2527, -0.6234), (-north_w/2, +side_w/2, +h/2)),
            ((+0.2527, -0.3034), (-north_w/2, -side_w/2, +h/2))
        ]
    elif dir == 'n':
       # set screen width and height
       h = 3.29e-2
       pts = [
            ((+0.1295, +0.6278), (-north_w/2, +side_w/2, -h/2)),
            ((+0.1297, +0.3233), (+north_w/2, +side_w/2, -h/2)),
            ((-0.0675, +0.3213), (+north_w/2, +side_w/2, +h/2)),
            ((-0.0675, +0.6175), (-north_w/2, +side_w/2, +h/2))
        ]

    elif dir == 'e':
        # set screen width and height
        h = 3.18e-2
        pts = [
            ((-0.1973, -0.2634), (+north_w/2, +side_w/2, -h/2)),
            ((-0.1873, -0.5509), (+north_w/2, -side_w/2, -h/2)),
            ((-0.3986, -0.5734), (+north_w/2, -side_w/2, +h/2)),
            ((-0.4023, -0.2791), (+north_w/2, +side_w/2, +h/2))
        ]
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(*pts)

def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def fictrac_get_data(sock):
    data = sock.recv(1024)

    #if not data:
    #    break

    # Decode received data
    line = data.decode('UTF-8')
    endline = line.find("\n")
    line = line[:endline]
    toks = line.split(", ")

    logging.debug("Received from fictrac socket: %s", line)

    # Fixme: sometimes we read more than one line at a time,
    # should handle that rather than just dropping extra data...
    if ((len(toks) < 7) | (toks[0] != "FT")):
        logging.warning("Bad read, too few tokens: %s", line)
        return fictrac_get_data(sock)
        #continue

    if len(toks) > 7:
        logging.warning("Bad read, too many tokens: %s", line)

    #dr_lab = [float(toks[6]), float(toks[7]), float(toks[8])]

    #posx = float(toks[15])
    #posy = float(toks[16])
    #heading = float(toks[17])
    #timestamp = float(toks[22])
    #sync_illum = int(toks[24])
    #sync_mean = float(toks[25])

    posx = float(toks[1])
    posy = float(toks[2])
    heading = float(toks[3])
    timestamp = float(toks[4])
    sync_mean = float(toks[5])

    #print(time()*1000 - float(toks[6]))

    return (posx, posy, heading, timestamp, sync_mean)


def main():
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), \
                    square_side=0.08, square_loc='ur', save_square_history=True)
    # square_toggle_prob=0.1,
    print(screen)

    FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
    FICTRAC_PORT = 33334         # The port used by the server
    RADIUS = 0.0045 # in meters; i.e. 4.5mm

    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: display a stimulus
    #####################################################

    n_trials=4
#    save_path = "/home/clandinin/minseung_cl_data"
#    save_prefix = "preallocate_vsync_on"
    save_path = "/home/clandinin/andrew/latency_measurements"
    save_prefix = "200711_trial_01"

    logging.basicConfig(
        format='%(asctime)s %(message)s',
        filename="{}/{}".format(save_path, save_prefix),
        level=logging.DEBUG
    )

    manager = launch_stim_server(screen)
    manager.set_save_history_flag(True)

    ft_frame_rate = 250 #Hz, higher

    stim_length = 10 #sec
    speed = 0 #degrees per sec
    still_duration = 1 #seconds
    sample_period = 6 #seconds
    occlusion_period = 2 #seconds
    iti = 2 #seconds
    trajectory = RectangleTrajectory(x=[(0,90),(still_duration,90),(stim_length, 90-speed*(stim_length-still_duration))], y=90, w=2, h=60)
    occluder = RectangleTrajectory(x=[(0,90-speed*(still_duration+sample_period)),(stim_length,90-speed*(still_duration+sample_period))], y=90, w=occlusion_period*speed, h=70)

    #p = subprocess.Popen(["/home/clandinin/fictrac_test/bin/fictrac","/home/clandinin/fictrac_test/config1.txt"], start_new_session=True)
    p = subprocess.Popen(["/home/clandinin/fictrac_test/bin/fictrac","/home/clandinin/fictrac_test/config_smaller_window.txt","-v","ERR"], start_new_session=True)
    sleep(2)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as fictrac_sock:
        fictrac_sock.connect((FICTRAC_HOST, FICTRAC_PORT))

        for t in range(n_trials):
            # begin trial
            ft_sync_means = np.zeros(ft_frame_rate * (stim_length+5))
            ft_timestamps = np.zeros(ft_frame_rate * (stim_length+5))
            ft_posx = np.zeros(ft_frame_rate * (stim_length+5))
            ft_posy = np.zeros(ft_frame_rate * (stim_length+5))
            ft_theta = np.zeros(ft_frame_rate * (stim_length+5))
            #manager.load_stim(name='MovingPatch', trajectory=occluder.to_dict())
            #manager.load_stim(name='MovingPatch', trajectory=trajectory.to_dict(), vary='alpha', hold=True)
            #_=fictrac_sock.recv(8192) #clear trash
            _ = fictrac_get_data(fictrac_sock)
            #_=fictrac_sock.recv(2048) #clear trash
            #sleep(5)
            #for i in range(4):
            #    _ = fictrac_get_data(fictrac_sock)
            manager.load_stim('MovingPatch', trajectory=trajectory.to_dict(), background=None)
            #manager.load_stim('MovingPatch', trajectory=occluder.to_dict(), background=None, hold=True)

            print ("===== Trial " + str(t) + " ======")
            t_start = time()
            manager.start_stim()
            posx_0, posy_0, theta_0, _, _ = fictrac_get_data(fictrac_sock)

            cnt = 0
            while (time() -  t_start) < stim_length:

                #posx, posy, theta_rad, timestamp, sync_illum, sync_mean = fictrac_get_data(fictrac_sock)
                posx, posy, theta_rad, timestamp, sync_mean = fictrac_get_data(fictrac_sock)
                posx = posx - posx_0
                posy = posy - posy_0
                theta_rad = theta_rad - theta_0

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
            manager.set_save_path(save_path)
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
            while (time() - t_iti_start) < iti:
                _ = fictrac_get_data(fictrac_sock)

    p.terminate()
    p.kill()


    #sync_means = np.array(ft_sync_means)
    plt.plot(ft_sync_means)
    plt.show()

if __name__ == '__main__':
    main()
