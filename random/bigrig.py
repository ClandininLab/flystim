from math import pi

from flystim.screen import Screen

def get_bigrig_screen(dir):
    w = 43 * 2.54e-2
    h = 24 * 2.54e-2

    if dir.lower() in ['w', 'west']:
        id = 1
        rotation = pi/2
        offset = (-w/2, 0, h/2)
    elif dir.lower() in ['n', 'north']:
        id = 2
        rotation = 0
        offset = (0, w/2, h/2)
    elif dir.lower() in ['s', 'south']:
        id = 3
        rotation = pi
        offset = (0, -w/2, h/2)
    elif dir.lower() in ['e', 'east']:
        id = 4
        rotation = -pi/2
        offset = (w/2, 0, h/2)
    else:
        raise ValueError('Invalid direction.')

    return Screen(id=id, rotation=rotation, width=w, height=h, offset=offset,
                  name='BigRig {} Screen'.format(dir.title()))