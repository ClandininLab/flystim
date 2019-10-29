from math import radians
from time import time
import numpy as np
from PIL import Image

from flystim import GenPerspective, GlCylinder, GlSphericalCirc, GlSphericalRect, CaveSystem, rel_path
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
    background_speed = 10
    patch_speed = 180
    az_start = -260
    display.render_actions.append(lambda: cave.render(GlCylinder(cylinder_radius=3, cylinder_height=6, texture=True).rotz(radians(background_speed*(time()-t0))).rotx(radians(0)), texture_img=img))
    display.render_actions.append(lambda: cave.render(GlSphericalCirc(color=1, sphere_radius=2).rotz(radians(az_start+patch_speed*(time()-t0)))))
    display.render_actions.append(lambda: cave.render(GlSphericalRect(width=10, height=30, color=0, sphere_radius=1).rotz(radians(az_start+50*(time()-t0)))))


if __name__ == '__main__':
    run_qt(lambda display: register_cave(display))
