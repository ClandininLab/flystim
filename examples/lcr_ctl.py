#!/usr/bin/env python3

from argparse import ArgumentParser
from flystim.dlpc350 import make_dlpc350_objects

def main():
    parser = ArgumentParser()

    # FPS argument
    parser.add_argument('--fps', type=float, default=115.06)

    # RGB currents
    parser.add_argument('--red_current', type=float, default=0)
    parser.add_argument('--green_current', type=float, default=0)
    parser.add_argument('--blue_current', type=float, default=2.1529)

    args = parser.parse_args()

    print('Using FPS: ' + str(args.fps))
    print('Red current: ' + str(args.red_current))
    print('Green current: ' + str(args.green_current))
    print('Blue current: ' + str(args.blue_current))

    dlpc350_objects = make_dlpc350_objects()

    print('Found {} lightcrafters.'.format(len(dlpc350_objects)))

    for dlpc350_object in dlpc350_objects:
        dlpc350_object.set_current(red=args.red_current, green=args.green_current, blue=args.blue_current)
        dlpc350_object.pattern_mode(fps=args.fps)

if __name__ == "__main__":
    main()
