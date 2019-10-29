from math import radians
from time import time

from flystim import GenPerspective, GlSphericalRect, CaveSystem
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

    # add rect rendering to the render action list
    display.render_objs.append(cave)
    t0 = time()
    elevation = 20
    az_start = -260
    display.render_actions.append(lambda: cave.render(GlSphericalRect(width=10, height=30).rotx(radians(90)).rotz(radians(az_start+omega*(time()-t0))).roty(radians(elevation))))

if __name__ == '__main__':
    run_qt(lambda display: register_cave(display, omega=20))
