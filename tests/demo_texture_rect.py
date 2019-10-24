from math import radians
from time import time
import numpy as np
from PIL import Image

from flystim import GenPerspective, GlQuad, CaveSystem, rel_path
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

    display.render_objs.append(cave)

    # load the texture image
    img = np.flipud(np.array(Image.open(rel_path('tests', 'data', 'preview_sample_0101_tonemapped.jpg'))))
    img = img[:196, :196].astype(np.uint8)

    t0 = time()

    s = 1 # side length
    v1, v2, v3, v4 = ((-1, -s, -s), (-1, +s, -s), (-1, +s, +s), (-1, -s, +s))
    color = (1, 1, 1, 1)
    tc1, tc2, tc3, tc4 = ((0, 0), (1, 0), (1, 1), (0, 1))
    display.render_actions.append(lambda: cave.render(GlQuad(v1, v2, v3, v4, color, tc1, tc2, tc3, tc4).translate((0,np.cos(2*np.pi*(time()-t0)/4),np.sin(2*np.pi*(time()-t0)/2))), texture_img=img))

if __name__ == '__main__':
    run_qt(lambda display: register_cave(display, omega=1))
