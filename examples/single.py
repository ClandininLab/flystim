#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep
from flystim.options import OptionParser

def main():
    parser = OptionParser('Show a specific stimulus type.')
    parser.add_argument('--stim_type', type=str, default='Checkerboard', help='Name of the stimulus type.')
    parser.add_argument('--freeze', action='store_true', help="Don't run the stimulus, just freeze at the first frame.")
    parser.add_argument('--duration', type=float, default=4.0, help='Length of each trial.')

    manager = parser.create_manager()

    print('Press Ctrl-C to quit the program...')
    while True:
        manager.load_stim(name=parser.args.stim_type)
        manager.start_stim()

        if parser.args.freeze:
            freeze()
        else:
            sleep(parser.args.duration)
            manager.stop_stim()

def freeze():
    while True:
        sleep(1)

if __name__ == '__main__':
    main()
