#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

# Please be sure to launch the server first before starting this program.

from xmlrpc.client import ServerProxy
from time import sleep
from random import choice

def main(num_trials=15, port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))

    all_stims = ['SineGrating', 'RotatingBars', 'ExpandingEdges', 'SequentialBars', 'RandomBars', 'RandomGrid',
                 'Checkerboard']

    for _ in range(num_trials):

        client.load_stim(choice(all_stims), {})

        sleep(500e-3)
        client.start_stim()
        sleep(2.5)
        client.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
