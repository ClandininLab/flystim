from math import pi, sqrt

from flystim1.screen import Screen

def get_bruker_screen(dir):
    # display geometry
    z_bottom = -12.13e-2 #m
    z_top = 0
    x_left = -7.99e-2
    x_right = +7.99e-2
    x_center = 0
    y_forward = +7.17e-2
    y_back = -0.8e-2

    if dir.lower() in ['l', 'left']:
        id=1
        pts = [
            ((+0.7100, -1), (x_left,   y_back,    z_bottom)),
            ((-0.6000, -1), (x_center, y_forward, z_bottom)),
            ((-0.6000, +1), (x_center, y_forward, z_top)),
            ((+0.7100, +1), (x_left,   y_back,    z_top))
        ]
        square_side=(0.11, 0.23)
        square_loc = (0.89, -1.00)
    elif dir.lower() in ['r', 'right']:
        id=2
        pts = [
            ((+0.7500, -1), (x_center, y_forward, z_bottom)),
            ((-0.5800, -1), (x_right,  y_back,    z_bottom)),
            ((-0.5800, +1), (x_right,  y_back,    z_top)),
            ((+0.7500, +1), (x_center, y_forward, z_top))
        ]
        square_side=(0.14, 0.22)
        square_loc = (-0.85, -0.94)
    else:
        raise ValueError('Invalid direction.')

    return Screen(id=id, tri_list=Screen.quad_to_tri_list(*pts), square_loc=square_loc,
           fullscreen=True, square_side=square_side, name='Bruker {} Screen'.format(dir.title()))
