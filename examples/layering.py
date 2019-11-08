#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=1, id=0, vsync=False))

    # manager.load_stim(name='ConstantBackground', color = [0.5, 0.5, 0.5, 1.0], side_length=100)

    distribution_data = {'name': 'Gaussian',
                         'args': [],
                         'kwargs': {'rand_mean': 0.5,
                                    'rand_stdev': 0.3}}

    manager.load_stim(name='RandomGrid', patch_width=5, patch_height=5, start_seed=0, update_rate=5.0,
                      distribution_data=distribution_data, color=[1, 1, 1, 1], angle=0,
                      cylinder_radius=2, cylinder_vertical_extent=80, cylinder_angular_extent=60, theta=0, phi=0, hold=True)

    tv_pairs = [(0,-45), (4, 45)]
    theta_traj = Trajectory(tv_pairs, kind='linear').to_dict()
    manager.load_stim(name='MovingPatch',width=10, height=30, phi=0, color=1, theta=theta_traj, hold=True, angle=45)
    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=True)
    sleep(0.5)

if __name__ == '__main__':
    main()
