import numpy as np


n_points = 100
y_locations = np.random.uniform(0, 8, n_points)
x_locations = np.random.uniform(-2, 2, n_points)
z_locations = np.random.uniform(-2, 2, n_points)

point_locations = [y_locations, x_locations, z_locations]
len(point_locations)

vertices = np.vstack(point_locations)
vertices.shape
