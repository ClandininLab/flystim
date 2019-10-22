from math import radians
from time import time
from PIL import Image
import numpy as np

from flystim import GenPerspective, GlSphericalCirc, CaveSystem, rel_path
from common import run_qt, run_headless, get_img_err

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
    center = (-200, 0)
    display.render_actions.append(lambda: cave.render(GlSphericalCirc(color=0.5 + 0.5*np.sin(2*np.pi*omega*(time()-t0))).rotz(radians(center[0])).roty(radians(center[1]))))

def test_spherical_circ(max_err=100):
    # render image
    obs = run_headless(register_cave)

    # load image for comparison
    ref = Image.open(rel_path('tests', 'data', 'color_cube.png'))

    # compute error
    error = get_img_err(obs, ref)
    print(error)

    # check that error is OK
    assert error <= max_err, f'Error {error} exceeds limit of {max_err}.'

if __name__ == '__main__':
    run_qt(lambda display: register_cave(display, omega=1))
    #test_spherical_circ()
