#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep
from random import choice
from flystim.options import OptionParser

def main():
    parser = OptionParser('Random choose different rotation directions and speeds.')
    parser.add_argument('--num_trials', type=int, default=10, help='Total number of trials in the experiment.')
    parser.add_argument('--stim_type', type=str, default='SineGrating', help='Name of the grating type.')

    manager = parser.create_manager()

    signs = [-1, 1]
    rates = [10, 20, 40, 100, 200, 400, 1000]

    for _ in range(parser.args.num_trials):
        sign = choice(signs)
        rate = sign*choice(rates)

        manager.load_stim(name=parser.args.stim_type, rate=rate)
        sleep(550e-3)

        manager.start_stim()
        sleep(250e-3)

        manager.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
