from collections import defaultdict

import numpy as np

X, Y = 0, 1
DIAGONAL = (0, 0)


def diagonal_point(x):
    """Get point closest to x on diagonal."""
    return (x[X] + x[Y]) / 2, (x[X] + x[Y]) / 2


def l_inf(x1, x2):
    """Compute l-infinity distance between two 2D-points on persistence diagram"""
    return max(abs(x1[Y] - x2[Y]), abs(x1[X] - x2[X]))


def naive_greedy_sketch(pd, n=-1, minimal=True):
    """
    Input is a persistence diagram. Output is a greedy permutation of points.
    Runs in O(n^2).
    """
    if n > len(pd):
        raise ValueError(
            "Length of greedy permutation greater than number of points in persistence diagram"
        )
    if n < 0:
        n = len(pd)

    # To be returned at all times
    # greedy sketches to be returned
    sketches = []
    # transportation plans of all sketches
    transport_plans = []

    # Following to be returned iff minimal=False
    # stores points of pd ordered in a greedy permutation
    perm = np.empty((n, 2))
    # sequence of greedy distances which is also returned
    dist_seq = np.empty((n, 1))
    # store reverse nearest neighbor of all points of pd
    rnn = np.empty((len(pd), 2))
    # store distances of every point in pd to its reverse nearest neighbor
    dist = np.empty(len(pd))
    if not minimal:
        # discrete voronoi cells for each sketch
        voronoi = np.empty((n, len(pd), 2))

    # temporary variable to store maximum distance of the next greedy point
    # within an iteration
    max_dist = 0
    # temporary variable to store furthest point index to compute the next
    # greedy point
    furthest = 0

    # point (0,0) is the diagonal

    # initialize rnn data structure as reverse nearest neighbor of all points
    # is the diagonal
    for i in range(len(pd)):
        rnn[i] = (0, 0)
        dist[i] = l_inf(pd[i], diagonal_point(pd[i]))
        # print(f"Point = {pd[i]}, distance = {dist[i]}")
        if dist[i] > max_dist:
            max_dist = dist[i]
            furthest = i

    for i in range(n):
        # print(f"Current round: {i} furthest point: {pd[furthest]}, index: {furthest}")

        # update reverse nearest neighbors of every point using newly added
        # point
        perm[i] = pd[furthest].copy()
        dist_seq[i] = max_dist

        # temporary variable to store mass movement within successive sketches
        transport = defaultdict(int)
        for j in range(len(pd)):
            if l_inf(pd[j], pd[furthest]) >= dist[j]:
                continue

            # print(
            #     f"j: {j}, point: {pd[j]}, old rnn: {rnn[j]}, old distance = {dist[j]:0.2f}, new rnn: {pd[furthest]}, new distance = {l_inf(pd[j], pd[furthest]):0.2f}"
            # )

            # one point lost by old rnn of j
            transport[tuple(rnn[j])] -= 1

            rnn[j] = pd[furthest].copy()
            dist[j] = l_inf(pd[j], pd[furthest])

            # one point gained by new rnn of j
            transport[tuple(rnn[j])] += 1

        # update max_dist and select next furthest point
        max_dist = 0
        for j in range(len(pd)):
            if dist[j] > max_dist:
                max_dist = dist[j]
                furthest = j

        # store current voronoi diagram
        if not minimal:
            voronoi[i] = rnn.copy()

        # append mass movement from previous sketch to the transportation plan
        transport_plans.append(transport)

    sketches = generate_sketches(perm, n=n)

    ret = {"sketches": sketches, "transport_plans": transport_plans}

    if not minimal:
        ret["dist"] = dist_seq
        ret["voronoi"] = voronoi
        ret["perm"] = perm
        ret["persistence_diagram"] = pd

    return ret


def generate_sketches(perm, n=-1):
    """
    Input is a greedy sequence of points of a pd. Output is a series of
    greedy sketches of that pd.
    """
    if n > len(perm):
        raise ValueError(
            "Number of sketches requested is greater than number of points in greedy permutation"
        )
    if n < 0:
        n = len(perm)
    sketches = []
    for i in range(1, n + 1):
        sketch = np.empty((i, 2))
        for j in range(i):
            sketch[j][X] = perm[j][X]
            sketch[j][Y] = perm[j][Y]
        sketches.append(sketch)
    return sketches