from collections import defaultdict

import numpy as np
import persim

X, Y = 0, 1

# point (0,0) is the diagonal
DIAGONAL = (0, 0)


def diagonal_point(x):
    """Get point closest to x on diagonal."""
    return (x[X] + x[Y]) / 2, (x[X] + x[Y]) / 2


def l_inf(x1, x2):
    """Compute l-infinity distance between two 2D-points on persistence diagram"""
    return max(abs(x1[Y] - x2[Y]), abs(x1[X] - x2[X]))


def naive_greedy_sketch(pd, n=-1, minimal=True):
    """Generate greedy permutation and sketches of points in persistence diagram.

    Runs in O(n^2).

    Parameters
    ----------
    pd : numpy.ndarray
        A n by 2 array of points in the persistence diagram.
    n : int, optional
        The size of the largest greedy sketch to produce. By default this is
        all points of the persistence diagrams.
    minimal : bool, default=False
        Whether to include extra information, detailed in the "Returns".

    Returns
    -------
    dict
        "perm": The points ordered in the order of the greedy permutation.

        "transport_plans": The changes of the mass of points over successive
        sketches. Taking the sum up to some sketch will give you the
        multiplicity of each point.

        "dist" (when `minimal=False`): A list of distances between each point
        in the original persistence diagram and the greedy sketch. The first
        index `i` is the `i`th greedy sketch to look at and the second index
        `j` is the smallest distance between the `j`th point in the original
        persistence diagram (`pd`) and the greedy sketch. Distance is
        determined by the `l_inf` metric.

        "voronoi" (when `minimal=False`): A list of the discrete Voronoi cells
        for each sketch. The first index `i` is the `i`th greedy sketch to look
        at and the second index `j` is the point in the greedy sketch which the
        `j`th point in the original persistence diagram maps to.

        "sketches" (when `minimal=False`): A list of full descriptions of each
        greedy sketch.
    """

    if n > len(pd):
        raise ValueError(
            "Length of greedy permutation greater than number of points in persistence diagram"
        )
    if n < 0:
        n = len(pd)

    # To be returned at all times
    # stores points of pd ordered in a greedy permutation
    perm = np.empty((n, 2))
    # transportation plans of all sketches
    transport_plans = []

    # Following to be returned if minimal=False
    # sequence of greedy distances
    dist_seq = np.empty((n, 1))
    if not minimal:
        # discrete voronoi cells for each sketch
        voronoi = np.empty((n + 1, len(pd), 2))

    # store reverse nearest neighbor of all points of pd
    rnn = np.empty((len(pd), 2))
    # store distances of every point in pd to its reverse nearest neighbor
    dist = np.empty(len(pd))
    # temporary variable to store maximum distance of the next greedy point
    # within an iteration
    max_dist = 0
    # temporary variable to store furthest point index to compute the next
    # greedy point
    furthest = 0

    # initialize RNN of all points as the diagonal
    for i in range(len(pd)):
        rnn[i] = DIAGONAL
        dist[i] = l_inf(pd[i], diagonal_point(pd[i]))
        # print(f"Point = {pd[i]}, distance = {dist[i]}")
        if dist[i] > max_dist:
            max_dist = dist[i]
            furthest = i
    # initialize first transportation plan and first voronoi diagram
    transport = defaultdict(int)
    transport[DIAGONAL] = len(pd)
    transport_plans.append(transport)
    if not minimal:
        voronoi[0] = rnn.copy()

    for i in range(n):
        # print(f"Current round: {i} furthest point: {pd[furthest]}, index: {furthest}")

        # update RNN of every point using newly added point
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

            # one point lost by old RNN of j
            transport[tuple(rnn[j])] -= 1

            rnn[j] = pd[furthest].copy()
            dist[j] = l_inf(pd[j], pd[furthest])

            # one point gained by new RNN of j
            transport[tuple(rnn[j])] += 1

        # update max_dist and select next furthest point
        max_dist = 0
        for j in range(len(pd)):
            if dist[j] > max_dist:
                max_dist = dist[j]
                furthest = j

        # store current voronoi diagram
        if not minimal:
            voronoi[i + 1] = rnn.copy()

        # append mass movement from previous sketch to the transportation plan
        transport_plans.append(transport)

    ret = {"perm": perm, "transport_plans": transport_plans}

    if not minimal:
        ret["dist"] = dist_seq
        ret["voronoi"] = voronoi
        ret["sketches"] = generate_sketches(perm, transport_plans, n)
        ret["persistence_diagram"] = pd

    return ret


def generate_sketches(perm, transport_plans, n=-1):
    """Generate a series of `n+1` greedy sketches of the given persistence diagram.

    Parameters
    ----------
    perm : numpy.ndarray
        The points ordered in the order of the greedy permutation for the
        persistence diagram.

    Returns
    ------
        A series of `n+1` greedy sketches of the given persistence diagram.
    """
    if n > len(perm):
        raise ValueError(
            "Number of sketches requested is greater than number of points in greedy permutation"
        )
    if n < 0:
        n = len(perm)
    if len(transport_plans) != n+1:
        raise ValueError(
            "Mismatch between transportation plan length and greedy permutation"
        )
    sketches = []
    mult_dict = defaultdict(int)
    
    for i in range(n + 1):
        points = np.empty((i+1, 2))
        mult = np.empty(i+1)
        for p in transport_plans[i]:
            mult_dict[p] += transport_plans[i][p]
        for j in range(i):
            points[j][X] = perm[j][X]
            points[j][Y] = perm[j][Y]
            mult[j] = mult_dict[tuple(perm[j])]
        points[i] = [0,0]
        mult[i] = mult_dict[(0,0)]
        sketches.append((points, mult))
    return sketches


def compute_mult(transport_plans):
    """
    Input is a series of transportation plans for n sketches ordered in greedy permutation
    Output is pointwise multiplicity of nth sketch
    """
    # test if ordering of sketches is greedy

    multiplicity = defaultdict(int)
    for i in range(len(transport_plans)):
        for point in transport_plans[i]:
            multiplicity[point] += transport_plans[i][point]
    return multiplicity


def intersketch_bd(transport_plans_a, transport_plans_b):
    """Find the bottleneck distance between two greedy sketches.

    Parameters
    ----------
    transport_plans_a, transport_plans_b
        Transportation plans of arbitrary persistence diagrams. Each plan
        corresponds to one persistence diagram.

    Returns
    -------
    float
        Bottleneck distance between the two sketches.
    """

    # if len(perm_a)+1 != len(transport_plans_a):
    #     raise ValueError(
    #         "Mismatch between transportation plans and permutation for sketch a"
    #     )
    # if len(perm_b)+1 != len(transport_plans_b):
    #     raise ValueError(
    #         "Mismatch between transportation plans and permutation for sketch b"
    #     )

    mult_a = compute_mult(transport_plans_a)
    mult_b = compute_mult(transport_plans_b)
    sketch_a = np.empty((transport_plans_a[0][DIAGONAL], 2))
    sketch_b = np.empty((transport_plans_b[0][DIAGONAL], 2))
    points_a = mult_a.keys()
    points_b = mult_b.keys()
    i = 0
    for point in points_a:
        for count in range(mult_a[tuple(point)]):
            sketch_a[i] = point
            i += 1
    i = 0
    for point in points_b:
        for count in range(mult_b[tuple(point)]):
            sketch_b[i] = point
            i += 1
    return persim.bottleneck(sketch_a, sketch_b, matching=False)
