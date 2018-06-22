#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

# Please be sure to launch the server first before starting this program.

from xmlrpc.client import ServerProxy
from time import sleep
from random import choice

def main(port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))

    stims = ['SineGrating', 'RotatingBars', 'ExpandingEdges', 'SequentialBars', 'RandomBars',
             'RandomGrid', 'Checkerboard']

    sleep(1.0)

    for stim in stims:

        client.load_stim(stim, {})

        sleep(500e-3)
        client.start_stim()
        sleep(2.5)
        client.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
