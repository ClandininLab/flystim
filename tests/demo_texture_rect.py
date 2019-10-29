from math import radians
from time import time
import numpy as np
from PIL import Image

from flystim import GenPerspective, GlQuad, CaveSystem, rel_path
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

    # load the texture image
    img = np.array(Image.open(rel_path('tests', 'data', 'preview_sample_0101_tonemapped.jpg'))).astype(np.uint8)

    t0 = time()

    h = 1
    w = 1
    v1, v2, v3, v4 = ((-1, -w/2, -h/2), (-1, +w/2, -h/2), (-1, +w/2, +h/2), (-1, -w/2, +h/2))
    color = (1, 1, 1, 1)
    tc1, tc2, tc3, tc4 = ((0, 0), (1, 0), (1, 1), (0, 1))
    display.render_actions.append(lambda: cave.render(GlQuad(v1, v2, v3, v4, color, tc1, tc2, tc3, tc4, texture_shift=(0, 0)), texture_img=img))

if __name__ == '__main__':
    run_qt(lambda display: register_cave(display))
