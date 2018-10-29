from math import pi, sqrt

from flystim.screen import Screen

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