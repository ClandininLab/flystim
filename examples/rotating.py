#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep
from random import choice

from flyrpc.launch import launch_server
import flystim.stim_server

def main():
    num_trials = 10
    stim_type = 'SineGrating'

    manager = launch_server(flystim.stim_server, setup_name='macbook')

    signs = [-1, 1]
    rates = [10, 20, 40, 100, 200, 400, 1000]

    for _ in range(num_trials):
        sign = choice(signs)
        rate = sign*choice(rates)

        manager.load_stim(name=stim_type, rate=rate)
        sleep(550e-3)

        manager.start_stim()
        sleep(250e-3)

        manager.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
