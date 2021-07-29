#!/usr/bin/env python3

#from flystim1.draw import draw_screens
from flystim1.dlpc350 import make_dlpc350_objects
from flystim1.screen import Screen
from flystim1.stim_server import launch_stim_server
from flystim1.bruker import get_bruker_screen


def main():

    background_color = input("Enter background color (default: 1): ")#26
    if background_color=="":
        background_color = 1
    background_color = float(background_color)
    print(background_color)


    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    dlpc350_objects[0].set_current(red=0, green = 0, blue = 1.2)    
    dlpc350_objects[1].set_current(red=0, green = 0, blue = 0.5)
    for dlpc350_object in dlpc350_objects:
         #dlpc350_object.set_current(red=0, green = 0, blue = 1.0)
         dlpc350_object.pattern_mode(fps=120, red=False, green=False, blue=True)
         dlpc350_object.pattern_mode(fps=120, red=False, green=False, blue=True)
         
    # Create screen object
    bruker_left_screen = get_bruker_screen('Left', square_pattern='frame')
    bruker_right_screen = get_bruker_screen('Right', square_pattern='frame')

    screens = [bruker_left_screen, bruker_right_screen]

    # Start stim server
    fs_manager = launch_stim_server(screens)
    fs_manager.set_idle_background(background_color)

    input("Press enter to quit.")
    
if __name__ == '__main__':
    main()
