from math import pi, sqrt
from flystim.screen import Screen

def get_macbook_screen():
    return Screen(id=0, rotation=0, width=0.332, height=0.207, offset=(0, 0.3, 0), square_loc='ll',
           fullscreen=False, square_side=2e-2, name='MacBook Screen')

def get_bruker_screen(dir):
    # display geometry
    w = 14.2e-2
    h = 9e-2
    d = (w/2) * sqrt(2)

    # derived parameters
    s = (w/2) / sqrt(2)

    if dir.lower() in ['l', 'left']:
        id=2
        rotation = -pi/4
        offset = (-s, -d + s, -h / 2)
        square_loc = 'll'
    elif dir.lower() in ['r', 'right']:
        id=1
        rotation = +pi/4
        offset = (+s, -d + s, -h / 2)
        square_loc = 'lr'
    else:
        raise ValueError('Invalid direction.')

    return Screen(id=id, rotation=rotation, width=w, height=h, offset=offset, square_loc=square_loc,
           fullscreen=True, square_side=5e-2, name='Bruker {} Screen'.format(dir.title()))

def get_bigrig_screen(dir):
    w = 43 * 2.54e-2
    h = 24 * 2.54e-2

    if dir.lower() in ['w', 'west']:
        id = 1
        rotation = pi/2
        offset = (-w/2, 0, h/2)
    elif dir.lower() in ['n', 'north']:
        id = 3
        rotation = 0
        offset = (0, w/2, h/2)
    elif dir.lower() in ['s', 'south']:
        id = 2
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

def get_screens(setup_name):
    if setup_name.lower() == 'macbook':
        return [get_macbook_screen()]
    elif setup_name.lower() in ['bruker_right']:
        return [get_bruker_screen('right')]
    elif setup_name.lower() in ['bruker_left']:
        return [get_bruker_screen('left')]
    elif setup_name.lower() in ['bruker']:
        return [get_bruker_screen(dir) for dir in ['left', 'right']]
    elif setup_name.lower() in ['bigrig']:
        return [get_bigrig_screen(dir) for dir in ['west', 'north', 'south', 'east']]
    else:
        raise ValueError('Invalid setup name.')
