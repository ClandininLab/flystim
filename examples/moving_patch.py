#!/usr/bin/env python3

# Example client program that displays a patch that is sent on a square trajectory

from time import sleep

from flystim.launch import StimManager
from flystim.screen import Screen

def main(num_trials=15):
    screens = [Screen()]
    manager = StimManager(screens)

    for _ in range(num_trials):
        manager.load_stim('MovingPatch')
        sleep(550e-3)

        manager.start_stim()
        sleep(6)

        manager.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
