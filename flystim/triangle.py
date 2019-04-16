import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

def tri_normal(p1, p2, p3):
    # convert to numpy arrays for convenience
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    p3 = np.array(p3, dtype=float)

    # find direction of surface normal
    # ref: https://www.khronos.org/opengl/wiki/Calculating_a_Surface_Normal
    cross = np.cross(p2 - p1, p3 - p1)

    # normalize
    unit_v = cross / np.linalg.norm(cross)

    # return result
    return unit_v

def tri_centroid(p1, p2, p3):
    # convert to numpy arrays for convenience
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    p3 = np.array(p3, dtype=float)

    return (p1 + p2 + p3) / 3.0

def tri_perim(p1, p2, p3):
    # convert to numpy arrays for convenience
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    p3 = np.array(p3, dtype=float)

    # compute side lengths
    sa = np.linalg.norm(p2-p1)
    sb = np.linalg.norm(p3-p2)
    sc = np.linalg.norm(p1-p3)

    # return perimeter
    return sa + sb + sc

def tri_draw(p1, p2, p3, ax, color=None, alpha=0.8):
    # draw the patch
    coll = Poly3DCollection([[p1, p2, p3]])
    coll.set_alpha(alpha)
    if color is not None:
        coll.set_facecolor(color)
    ax.add_collection3d(coll)

    # draw arrow in direction of patch normal
    centroid = tri_centroid(p1, p2, p3)
    normal = tri_normal(p1, p2, p3) * (tri_perim(p1, p2, p3)/10.0)
    ax.quiver(centroid[0], centroid[1], centroid[2], normal[0], normal[1], normal[2], colors=[(0,0,0,1)])

def main():
    fig = plt.figure()
    ax = Axes3D(fig)
    tri_draw((0,0,0), (1,0,0), (0,0,1), ax=ax)
    plt.show()

if __name__ == '__main__':
    main()