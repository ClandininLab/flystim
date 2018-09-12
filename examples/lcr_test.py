#!/usr/bin/env python3

from flystim.dlpc350 import make_dlpc350_objects

def main():

    dlpc350_objects = make_dlpc350_objects()

    for dlpc350_object in dlpc350_objects:
        dlpc350_object.pattern_mode(fps=90)

if __name__ == "__main__":
    main()
