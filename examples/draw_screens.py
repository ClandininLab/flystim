from math import pi
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from flystim.screen import Screen

def get_test_screen(dir):
    w = 2
    h = 1

    if dir.lower() in ['w', 'west']:
        id = 0
        rotation = pi/2
        offset = (-w/2, 0, h/2)
    elif dir.lower() in ['n', 'north']:
        id = 1
        rotation = 0
        offset = (0, w/2, h/2)
    elif dir.lower() in ['s', 'south']:
        id = 2
        rotation = pi
        offset = (0, -w/2, h/2)
    elif dir.lower() in ['e', 'east']:
        id = 3
        rotation = -pi/2
        offset = (w/2, 0, h/2)
    else:
        raise ValueError('Invalid direction.')

    return Screen(id=id, rotation=rotation, width=w, height=h, offset=offset, name=f'Screen {dir.title()}')

def main():
    screens = [get_test_screen(dir) for dir in ['w', 'n', 's', 'e']]

    fig = plt.figure()
    ax = Axes3D(fig)

    for screen in screens:
        screen.draw(ax=ax)

    # draw fly in the center
    ax.scatter(0, 0, 0, c='g')

    plt.show()

if __name__=='__main__':
    main()