from math import pi
from math import sqrt

from flystim.draw import draw_screens
from flystim.screen import Screen

def get_test_screen():
    #w = 2
    #h = 1

    #if dir.lower() in ['w', 'west']:
    #    id = 0
    #    rotation = pi/2
    ##    offset = (-w/2, 0, h/2)
    #elif dir.lower() in ['n', 'north']:
    #    id = 1
    #    rotation = 0
    #    offset = (0, w/2, h/2)
    #elif dir.lower() in ['s', 'south']:
    #    id = 2
    #    rotation = pi
    #    offset = (0, -w/2, h/2)
    #elif dir.lower() in ['e', 'east']:
    #    id = 3
    #    rotation = -pi/2
    #    offset = (w/2, 0, h/2)
    #else:
    #    raise ValueError('Invalid direction.')

    #w = 14.2e-2
    #h = 9e-2
    #d = (w/2) * sqrt(2)
    #s = (w/2) / sqrt(2)
    #eye_correction = -10e-3

    #right_screen = Screen(width=w, height=h, rotation=+pi/4, offset=(+s+eye_correction, -d + s, -h / 2), id=1, fullscreen=True, vsync=None, square_side=4e-2, square_loc='lr')
    #left_screen = Screen(width=w, height=h, rotation=-pi/4, offset=(-s-eye_correction, -d + s, -h / 2), id=2, fullscreen=True, vsync=None, square_side=4e-2, square_loc='ll')
    #Screen(id=id, rotation=rotation, width=w, height=h, offset=offset, name=f'Screen {dir.title()}')
    
    #RIGHT_SCREEN
    right_pts = [
            ((0.34, 0.94), (58.9e-3, 3e-3, -6.7e-3)),            
            ((-0.53, 0.94), (0, 71.6e-3, -6.7e-3)),
            ((-0.53, -0.96), (0, 71.6e-3, -131.7e-3)),
            ((0.34, -0.96), (58.9e-3, 3e-3, -131.7e-3))
        ]
    tri_list = Screen.quad_to_tri_list(*right_pts)
    right_screen = Screen(tri_list=tri_list, id=1, fullscreen=True, vsync=None)

    #LEFT_SCREEN
    left_pts = [
            ((0.57, 0.93), (-58.9e-3, 3e-3, -6.7e-3)),            
            ((-0.31, 0.93), (0, 71.6e-3, -6.7e-3)),
            ((-0.31, -0.99), (0, 71.6e-3, -131.7e-3)),
            ((0.57, -0.99), (-58.9e-3, 3e-3, -131.7e-3))
        ]
    tri_list = Screen.quad_to_tri_list(*left_pts)
    left_screen = Screen(tri_list=tri_list, id=2, fullscreen=True, vsync=None)

    screens = [right_screen, left_screen]

    return screens

def main():
    #screens = [get_test_screen(dir) for dir in ['w', 'n', 's', 'e']]
    screens = get_test_screen()

    draw_screens(screens)

if __name__=='__main__':
    main()
