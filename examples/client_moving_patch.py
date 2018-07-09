#!/usr/bin/env python3

# Example client program that displays a patch that is sent on a square trajectory

# Please be sure to launch the server first before starting this program.

from xmlrpc.client import ServerProxy
from time import sleep

def main(num_trials=15, port=62632):
    client = ServerProxy('http://127.0.0.1:{}'.format(port))

    trajectory = [(0, 90, 90), (1, 92, 90), (2, 92, 92), (3, 90, 92), (4, 90, 90), (5, 90, 90)]

    for _ in range(num_trials):
        client.load_stim('MovingPatch', {'trajectory': trajectory})

        sleep(550e-3)
        client.start_stim()
        sleep(6)
        client.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()
