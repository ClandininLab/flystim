#!/usr/bin/env python3

# Example client program that walks through all available stimuli
# Please be sure to launch the server first before starting this program.

from xmlrpc.client import ServerProxy, MultiCall
from time import sleep
from random import choice

def main(port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))

    stims = ['SineGrating', 'RotatingBars', 'ExpandingEdges', 'SequentialBars', 'RandomBars',
             'RandomGrid', 'Checkerboard', 'MovingPatch']

    sleep(1.0)

    for stim in stims:

        multi = MultiCall(client)
        multi.load_stim(stim, {})
        multi.start_stim()
        multi.start_corner_square()
        multi()

        sleep(2.5)

        multi = MultiCall(client)
        multi.stop_stim()
        multi.black_corner_square()
        multi()

        sleep(1)

if __name__ == '__main__':
    main()
