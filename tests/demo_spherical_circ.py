from math import radians
from time import time
import numpy as np

from flystim import GenPerspective, GlSphericalCirc, CaveSystem
from common import run_qt

def get_perspective(theta, phi):
    # nominal position
    perspective = GenPerspective(pa=(+1, -1, -1), pb=(+1, +1, -1), pc=(+1, -1, 1), pe=(0, 0, 0))

    # rotate screen and eye position
    return perspective.roty(-radians(phi)).rotz(radians(theta))

def register_cave(display, omega=0):
    # create the CAVE system with various perspectives
    cave = CaveSystem()
    cave.add_subscreen((0, 0, 512, 512), get_perspective(theta=0, phi=0))

    # add circ rendering to the render action list
    display.render_objs.append(cave)
    t0 = time()
    center_1 = (-200, 0)
    display.render_actions.append(lambda: cave.render(GlSphericalCirc(color=0.5 + 0.5*np.sin(2*np.pi*(2*omega)*(time()-t0))).rotz(radians(center_1[0])).roty(radians(center_1[1]))))

    center_2 = (-160, 0)
    display.render_actions.append(lambda: cave.render(GlSphericalCirc(color=0.5 + 0.5*np.sin(2*np.pi*(omega/2)*(time()-t0))).rotz(radians(center_2[0])).roty(radians(center_2[1]))))

if __name__ == '__main__':
    run_qt(lambda display: register_cave(display, omega=1))
