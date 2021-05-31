import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
from collections import Iterable

COLOR_LIST = ['b', 'g', 'r', 'c', 'm', 'y']

def draw_screens(screens):
    if not isinstance(screens, Iterable):
        screens = [screens]

    fig = plt.figure()
    ax = Axes3D(fig)

    for screen in screens:
        for tri in screen.tri_list:
            # grab just the xyz coordinates of each point in the triangle
            pa = np.array(tri.pa.cart)
            pb = np.array(tri.pb.cart)
            pc = np.array(tri.pc.cart)

            # draw the triangle
            tri_draw(pa, pb, pc, ax=ax, color=COLOR_LIST[screen.id % len(COLOR_LIST)])

    # draw fly in the center
    ax.scatter(0, 0, 0, c='g')

    plt.show()

def tri_draw(p1, p2, p3, ax, color=None, alpha=0.8):
    coll = Poly3DCollection([[p1, p2, p3]])
    coll.set_alpha(alpha)

    if color is not None:
        coll.set_facecolor(color)

    ax.add_collection3d(coll)
