import itertools

import matplotlib.pyplot as plt
import numpy as np
import persim
from matplotlib import animation

from greedy_sketch.sketch import DIAGONAL, diagonal_point

# Cool paper about these colors: https://eleanormaclure.files.wordpress.com/2011/03/colour-coding.pdf
# White, black, and grey removed
DEFAULT_COLORS = [
    "#F3C300",
    "#875692",
    "#F38400",
    "#A1CAF1",
    "#BE0032",
    "#C2B280",
    "#008856",
    "#E68FAC",
    "#0067A5",
    "#F99379",
    "#604E97",
    "#F6A600",
    "#B3446C",
    "#DCD300",
    "#882D17",
    "#8DB600",
    "#654522",
    "#E25822",
    "#2B3D26",
]
# Reserve grey for the diagonal
DEFAULT_DIAGONAL_COLOR = "lightgrey"

DEFAULT_SIZE_X = 300
DEFAULT_SIZE_Y = 300


def make_animation(
    greedy_sketch,
    colors=DEFAULT_COLORS,
    diagonal_color=DEFAULT_DIAGONAL_COLOR,
    size_x=DEFAULT_SIZE_X,
    size_y=DEFAULT_SIZE_Y,
    ax=None,
):
    ax = ax or plt.gca()
    fig = ax.figure

    # Unpack greedy_sketch
    sketches = greedy_sketch["sketches"]
    perm = greedy_sketch["perm"]
    voronoi = greedy_sketch["voronoi"]
    orig_pts = greedy_sketch["persistence_diagram"]

    colors = itertools.cycle(colors)
    point_colors = {tuple(point): next(colors) for point in perm}
    point_colors[DIAGONAL] = diagonal_color

    graph = ax.scatter(
        [point[0] for point in orig_pts], [point[1] for point in orig_pts], s=5
    )
    [bottleneck_main_line] = ax.plot(-1, -1, color="black")
    [bottleneck_dash_line] = ax.plot(-1, -1, color="black", linestyle="dotted")

    def init_animation():
        # Draw diagonal
        persim.plot_diagrams(
            np.zeros((1, 2)),
            xy_range=[0, size_x, 0, size_y],
            show=False,
            legend=False,
            ax=ax,
        )
        plt.close(fig)

    pts = orig_pts.tolist()

    def animate(frame):
        # Add the sketch point
        pts = np.concatenate((orig_pts, sketches[frame]), axis=0)

        # Draw points
        xs = [x for x, y in pts]
        ys = [y for x, y in pts]
        graph.set_offsets(np.vstack((xs, ys)).T)
        graph.set_facecolors(
            # Color other points based on their nearest neighbor
            [point_colors[tuple(voronoi[frame, i])] for i, _pt in enumerate(orig_pts)]
            # Color all old sketch points
            + ["black"] * (frame - 1)
            # Color new sketch point
            + ["red"]
        )
        graph.set_sizes(
            # Make other points small
            [5] * len(orig_pts)
            # Make sketch points large
            + [20] * (frame)
        )

        # Show bottleneck distance
        bneck = perm[frame]
        # We get the first point where the match occurs. This returns two identical
        # indexes because bottleneck is 2D I believe.
        bneck_idx = np.where(orig_pts == bneck)[0][0]
        bneck_nn = voronoi[frame, bneck_idx]
        if tuple(bneck_nn) == DIAGONAL:
            bneck_nn = diagonal_point(bneck)

        vline = [bneck_nn[0], bneck_nn[0]], [bneck[1], bneck_nn[1]]
        hline = [bneck[0], bneck_nn[0]], [bneck[1], bneck[1]]
        if abs(bneck[0] - bneck_nn[0]) >= abs(bneck[1] - bneck_nn[1]):
            # The horizontal line (x) is the main line
            bottleneck_main_line.set_data(*hline)
            bottleneck_dash_line.set_data(*vline)
        else:
            # The vertical line (y) is the main line
            bottleneck_main_line.set_data(*vline)
            bottleneck_dash_line.set_data(*hline)

    return animation.FuncAnimation(
        fig,
        animate,
        init_func=init_animation,
        # We don't show the last frame, so we can always show the bottleneck
        # distance
        frames=len(sketches) - 1,
        interval=500,
    )
