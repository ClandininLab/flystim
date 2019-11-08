#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen

from time import sleep


def main():
    manager = launch_stim_server(Screen(fullscreen=False, server_number=1, id=0, vsync=True))

    manager.load_stim(name='CylindricalGrating', period=10, mean=0.5, contrast=1.0, offset=0.0, profile='square',
                  color=[1, 1, 1, 1], cylinder_radius=1, cylinder_height=10, theta=0, phi=0, angle=0)
    sleep(0.5)

    manager.start_stim()
    sleep(8)

    manager.stop_stim(print_profile=False)
    sleep(0.5)

if __name__ == '__main__':
    main()
