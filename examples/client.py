#!/usr/bin/env python3

# Example client program that randomly cycles through different RotatingBars stimuli.
# Please launch the server first before starting this program.

from xmlrpc.client import ServerProxy
from time import sleep

from random import choice

def main(port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))

    dirs = [-1, 1]
    rates = [10, 20, 40, 100, 200, 400, 1000]

    while True:
        dir = choice(dirs)
        rate = dir*choice(rates)

        client.load_stim('RotatingBars', {'rate': rate})

        sleep(550e-3)
        client.start_stim()
        sleep(250e-3)
        client.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()