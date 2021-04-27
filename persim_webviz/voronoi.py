
# For indexing into points
X, Y = 0, 1

class Voronoi:
    def __init__(self):
        self.points = []

    def add_point(self, point):
        self.points.append(point)

    # Returns the point in `points` that's closest to the query based on the L-infinity metric
    def nn_max_norm(self, query):
        nn = ((), float("inf")) # point, distance
        for point in self.points:
            if (dist := dist_max_norm(point, query)) < nn[1]:
                nn = (point, dist)
        return nn


def dist_max_norm(point1, point2):
    return max(abs(point1[X] - point2[X]), abs(point1[Y] - point2[Y]))