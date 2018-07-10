#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

# Please be sure to launch the server first before starting this program.

from xmlrpc.client import ServerProxy
from time import sleep
from random import choice

def main(num_trials=15, stim_type='SineGrating', port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))

    signs = [-1, 1]
    rates = [10, 20, 40, 100, 200, 400, 1000]

    for _ in range(num_trials):
        sign = choice(signs)
        rate = sign*choice(rates)

        client.load_stim(stim_type, {'rate': rate, 'angle': 45})

        sleep(550e-3)
        client.start_stim()
        sleep(250e-3)
        client.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
