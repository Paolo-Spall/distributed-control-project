from numpy import arange
import numpy as np
from matplotlib.path import Path
import scipy as sp
from math import exp

def in_box(towers, bounding_box):
    return np.logical_and(np.logical_and(bounding_box[0] <= towers[:, 0],
                                         towers[:, 0] <= bounding_box[1]),
                          np.logical_and(bounding_box[2] <= towers[:, 1],
                                         towers[:, 1] <= bounding_box[3]))


def gauss_pdf(x, y, sigma, mean):
    xt = mean[0]
    yt = mean[1]
    temp = ((x - xt) ** 2 + (y - yt) ** 2) / (2 * sigma ** 2)
    val = exp(-temp)
    return val


def compute_centroid(vertices, sigma=0.2, mean=[0.8, 0.8], discretz_int=20):
    x_inf = np.min(vertices[:, 0])
    x_sup = np.max(vertices[:, 0])
    y_inf = np.min(vertices[:, 1])
    y_sup = np.max(vertices[:, 1])

    t_discretize = 1.0 / discretz_int

    dx = (x_sup - x_inf) / 2.0 * t_discretize
    dy = (y_sup - y_inf) / 2.0 * t_discretize
    dA = dx * dy
    A = 0
    Cx = 0
    Cy = 0

    bool_val = 0

    for i in arange(x_inf, x_sup, dx):
        for j in arange(y_inf, y_sup, dy):
            p = Path(vertices)
            bool_val = p.contains_points([(i + dx, j + dy)])[0]
            if bool_val:
                A = A + dA * gauss_pdf(i, j, sigma, mean)
                Cx = Cx + i * dA * gauss_pdf(i, j, sigma, mean)
                Cy = Cy + j * dA * gauss_pdf(i, j, sigma, mean)

    Cx = Cx / A
    Cy = Cy / A

    return np.array([[Cx, Cy]])


# Generates a bounded Voronoi diagram with finite regions
def bounded_voronoi(towers, bounding_box):
    # Select towers inside the bounding box
    i = in_box(towers, bounding_box)
    # Mirror points left, right, above, and below to provide finite regions for the edge regions
    points_center = towers[i, :]

    points_left = np.copy(points_center)
    points_left[:, 0] = bounding_box[0] - (points_left[:, 0] - bounding_box[0])

    points_right = np.copy(points_center)
    points_right[:, 0] = bounding_box[1] + (bounding_box[1] - points_right[:, 0])

    points_down = np.copy(points_center)
    points_down[:, 1] = bounding_box[2] - (points_down[:, 1] - bounding_box[2])

    points_up = np.copy(points_center)
    points_up[:, 1] = bounding_box[3] + (bounding_box[3] - points_up[:, 1])

    points = np.concatenate((points_center, points_left, points_right, points_down, points_up), axis=0)

    # Compute Voronoi
    vor = sp.spatial.Voronoi(points)

    # Store the original regions corresponding to `points_center`
    original_region_indices = vor.point_region[:len(points_center)]
    filtered_regions = [vor.regions[idx] for idx in original_region_indices if -1 not in vor.regions[idx]]

    # Assign filtered regions and points to the vor object
    vor.filtered_points = points_center
    vor.filtered_regions = filtered_regions  # This is now a list of lists

    return vor


def centroid_region(vertices):
    # Polygon's signed area
    A = 0
    # Centroid's x
    C_x = 0
    # Centroid's y
    C_y = 0
    for i in range(0, len(vertices) - 1):
        s = (vertices[i, 0] * vertices[i + 1, 1] - vertices[i + 1, 0] * vertices[i, 1])
        A = A + s
        C_x = C_x + (vertices[i, 0] + vertices[i + 1, 0]) * s
        C_y = C_y + (vertices[i, 1] + vertices[i + 1, 1]) * s
    A = 0.5 * A
    C_x = (1.0 / (6.0 * A)) * C_x
    C_y = (1.0 / (6.0 * A)) * C_y

    return np.array([[C_x, C_y]])