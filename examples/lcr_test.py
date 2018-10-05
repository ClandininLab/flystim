#!/usr/bin/env python3

import sys

from time import sleep
from flystim.dlpc350 import make_dlpc350_objects

def main():
    try:
        fps = float(sys.argv[1])
    except:
        fps = 115.06

    print('Using fps=' + str(fps))

    dlpc350_objects = make_dlpc350_objects()

    print('Found {} lightcrafters.'.format(len(dlpc350_objects)))

    for dlpc350_object in dlpc350_objects:
        dlpc350_object.pattern_mode(fps=fps)

if __name__ == "__main__":
    main()
