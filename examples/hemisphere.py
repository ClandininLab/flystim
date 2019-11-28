#!/usr/bin/env python3

# Example showing rendering onto a hemisphere

from math import radians, sin, cos

from flystim.draw import draw_screens
from flystim.trajectory import Trajectory
from flystim.screen import Screen
from flystim.stim_server import launch_stim_server

from time import sleep

SPHERE_RADIUS = 1   # in meters
PROJECTOR_DIST = 1  # distance from the projector to the surface of the sphere in meters
THROW_RATIO = 1.75  # projector throw ratio (D/W)
ASPECT_RATIO = 16/9 # projector aspect ratio (W/H)

def to_screen_pt(lon, lat):
    # compute cartesian coordinates of this point
    r_xy = SPHERE_RADIUS*sin(radians(lat))
    x = r_xy*cos(radians(lon))
    y = r_xy*sin(radians(lon))
    z = SPHERE_RADIUS*cos(radians(lat))

    # compute NDC coordinates of this point
    ndc_x = 2*THROW_RATIO*x/(SPHERE_RADIUS+PROJECTOR_DIST-z)
    ndc_y = 2*THROW_RATIO*ASPECT_RATIO*y/(SPHERE_RADIUS+PROJECTOR_DIST-z)

    return ((ndc_x, ndc_y), (x, y, z))

def make_patch(lon, lat, d_lon, d_lat):
    # compute corners of the patch
    pts = [
        (lon, lat),
        (lon, lat + d_lat),
        (lon + d_lon, lat + d_lat),
        (lon + d_lon, lat)
    ]

    # convert points to ScreenPoints
    pts = [to_screen_pt(*pt) for pt in pts]

    # convert ScreenPoints to triangle list
    return Screen.quad_to_tri_list(*pts)

def make_tri_list(n_lon=10, n_lat=10):
    # input validation
    assert 360 % n_lon == 0, f'n_lon={n_lon} does not divide 360'
    assert  90 % n_lat == 0, f'n_lat={n_lat} does not divide 90'

    # determine angular step
    d_lon = 360//n_lon
    d_lat =  90//n_lat

    # build up a list of triangles
    tri_list = []

    for lon in range(0, 360, d_lon):
        for lat in range(0, 90, d_lat):
            tri_list += make_patch(lon=lon, lat=lat, d_lon=d_lon, d_lat=d_lat)

    # return result
    return tri_list

def main():
    screen = Screen(fullscreen=False, tri_list=make_tri_list())

    #####################################################
    # part 1: draw the screen configuration
    #####################################################

    draw_screens(screen)

    #####################################################
    # part 2: display a stimulus
    #####################################################

    manager = launch_stim_server(screen)

    tv_pairs = [(0,0),(10,360)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    manager.load_stim(name='MovingPatch',width=30, height=180, phi=0, color=1, theta=theta_traj, hold=True, angle=45)

    sleep(1)

    manager.start_stim()
    sleep(5)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()
