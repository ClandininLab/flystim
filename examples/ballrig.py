#!/usr/bin/env python3

# Example program showing rendering onto three subscreens

from flystim.draw import draw_screens
from flystim.trajectory import Trajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server

from time import sleep

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

def main():
    #screen = Screen(server_number=1, id=0, fullscreen=False, tri_list=make_tri_list())
    screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=0.08, square_loc='ur')

    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    #draw_screens(screen)

    #####################################################
    # part 2: define a stimulus
    #####################################################

    stim_length = 10 #sec
    speed = 2 #degrees per sec
    still_duration = 2 #seconds
    sample_period = 4 #seconds
    occlusion_period = 2 #seconds
    iti = 2 #seconds

    bar_theta_traj = Trajectory([(0,90),(still_duration,90),(stim_length, 90-speed*(stim_length-still_duration))], kind='linear').to_dict()
    bar_width = 2
    bar_height = 10
    bar_color = 1
    bar_sphere_radius = 1.1
    bar_angle = 0

    occluder_theta_traj = Trajectory([(0,90-speed*(still_duration+sample_period)),(stim_length,90-speed*(still_duration+sample_period))], kind='linear').to_dict()
    occluder_width = 2
    occluder_height = 10
    occluder_color = 0.8
    occluder_sphere_radius = 1
    occluder_angle = 0


    #####################################################
    # part 3: display a stimulus
    #####################################################

    manager = launch_stim_server(screen)
    manager.load_stim(name='MovingPatch',width=bar_width, height=bar_height, phi=0, color=bar_color, sphere_radius=bar_sphere_radius, theta=bar_theta_traj, angle=bar_angle, hold=True)
    manager.load_stim(name='MovingPatch',width=occluder_width, height=occluder_height, phi=0, color=occluder_color, sphere_radius=occluder_sphere_radius, theta=occluder_theta_traj, angle=occluder_angle, hold=True)


    #tv_pairs = [(0,-90), (5,270)]
    #theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    #manager.load_stim(name='MovingPatch',width=10, height=50, phi=0, color=1, theta=theta_traj, angle=0, hold=True)

    sleep(1)

    manager.start_stim()
    sleep(stim_length)

    manager.stop_stim()
    #manager.set_screen_color()
    #manager.black_corner_square()
    sleep(1)

if __name__ == '__main__':
    main()
