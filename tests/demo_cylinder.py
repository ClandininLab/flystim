from math import radians
from time import time
import numpy as np

from flystim import GenPerspective, GlCylinder, CaveSystem
from common import run_qt


def get_perspective(theta, phi):
    # nominal position
    perspective = GenPerspective(pa=(+1, -1, -1), pb=(+1, +1, -1), pc=(+1, -1, 1), pe=(0, 0, 0))

    # rotate screen and eye position
    return perspective.roty(-radians(phi)).rotz(radians(theta))


def register_cave(display):
    # create the CAVE system with various perspectives
    cave = CaveSystem()
    cave.add_subscreen((0, 0, 512, 512), get_perspective(theta=0, phi=0))

    display.render_objs.append(cave)

    # make the texture image
    dim = 512
    sf = 20/(2*np.pi)  # cycles per radian
    xx = np.linspace(0, 2*np.pi, dim)
    yy = 255*((0.5 + 0.5*(np.sin(sf*2*np.pi*xx))) > 0.5)
    img = np.tile(yy, (dim, 1)).astype(np.uint8)

    t0 = time()
    omega = 20
    display.render_actions.append(lambda: cave.render(GlCylinder(texture=True).rotz(radians(omega*(time()-t0))).rotx(radians(0)), texture_img=img))


if __name__ == '__main__':
    run_qt(lambda display: register_cave(display))
