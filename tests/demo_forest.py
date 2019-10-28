from math import radians
from time import time
import numpy as np

from flystim import GenPerspective, GlCylinder, CaveSystem
from common import run_qt

def get_perspective(theta, phi):
    # nominal position
    perspective = GenPerspective(pa=(+1, -1, -1), pb=(+1, +1, -1), pc=(+1, -1, 1), pe=(+2, 0, 0))

    # rotate screen and eye position
    return perspective.roty(-radians(phi)).rotz(radians(theta))

def register_cave(display, omega=0):
    # create the CAVE system with various perspectives
    cave = CaveSystem()
    cave.add_subscreen((0, 0, 512, 512), get_perspective(theta=0, phi=0))

    # add rect rendering to the render action list
    display.render_objs.append(cave)

    n_trees = 40
    height = 1
    radius = 0.25

    xx = np.random.uniform(-2, 0, size=n_trees)
    yy = np.random.uniform(-3, 3, size=n_trees)

    for t in range(n_trees):
        new_obj = GlCylinder(cylinder_height=height, cylinder_radius=radius, cylinder_location=(xx[t], yy[t],+height/2))
        display.render_actions.append(lambda: cave.render(new_obj))

if __name__ == '__main__':
    run_qt(lambda display: register_cave(display, omega=20))
