import itertools

import matplotlib.pyplot as plt
import numpy as np
import persim
import ripser
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

X, Y = 0, 1


def make_greedy_sketch_animation(
    greedy_sketch,
    colors=DEFAULT_COLORS,
    diagonal_color=DEFAULT_DIAGONAL_COLOR,
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
    point_colors = {
        tuple(point): next(colors)
        for point in sorted(perm, key=lambda p: np.linalg.norm(p))
    }
    point_colors[DIAGONAL] = diagonal_color

    ax.set_title("Incremental Greedy Sketches")
    graph = ax.scatter(
        [point[0] for point in orig_pts], [point[1] for point in orig_pts], s=5
    )
    [bneck_main_line] = ax.plot(-1, -1, color="black")
    # Densly dotted linestyle from
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
    [bneck_sub_line] = ax.plot(-1, -1, color="black", linestyle=(0, (1, 1)))

    # Draw the diagonal, scale axes to a little past the final death
    final_death = max(death for birth, death in orig_pts)
    persim.plot_diagrams(
        np.zeros((1, 2)),
        xy_range=[0, final_death * 1.1, 0, final_death * 1.1],
        show=False,
        legend=False,
        ax=ax,
    )

    def init_animation():
        # This prevents the final frame from being displayed as if it were a
        # still figure
        plt.close(fig)

    def animate(frame):
        # Add the sketch point
        pts = np.concatenate((orig_pts, sketches[frame]), axis=0)

        # Draw points
        graph.set_offsets(pts)
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
        # We get the first point where the match occurs. This returns two
        # identical indexes because bottleneck is 2D I believe.
        bneck_idx = np.where(orig_pts == bneck)[0][0]
        bneck_nn = voronoi[frame, bneck_idx]
        if tuple(bneck_nn) == DIAGONAL:
            bneck_nn = diagonal_point(bneck)

        # We draw these such that the main line always comes from the
        # bottleneck point.
        # The way to read this is if we want to draw a line from (x1,y1) to
        # (x2,y2) we do line.set_data([x1, x2], [y1, y2])
        if abs(bneck[0] - bneck_nn[0]) > abs(bneck[Y] - bneck_nn[Y]):
            # The horizontal line (x) is the main line
            bneck_main_line.set_data([bneck[X], bneck_nn[X]], [bneck[Y], bneck[Y]])
            bneck_sub_line.set_data([bneck_nn[X], bneck_nn[X]], [bneck[Y], bneck_nn[Y]])
        else:
            # The vertical line (y) is the main line
            bneck_main_line.set_data([bneck[X], bneck[X]], [bneck[Y], bneck_nn[Y]])
            bneck_sub_line.set_data([bneck[X], bneck_nn[X]], [bneck_nn[Y], bneck_nn[Y]])

    return animation.FuncAnimation(
        fig,
        animate,
        init_func=init_animation,
        # We don't show the last frame, so we can always show the bottleneck
        # distance
        frames=len(sketches) - 1,
        interval=500,
    )


LIVE_POINT_COLOR = "#FF4500FF"
DEAD_POINT_COLOR = "#FF450066"


def make_persistent_homology_animation(points, data_ax=None, pd_ax=None):
    """Create visualization of building persistence diagram from set of 2d points.

    Input is an n x 2 `numpy.ndarray`. Output is a `matplotlib.animation.FuncAnimation`
    that lasts ~5 seconds with two animated subplots: the original points with animated
    inflating balls around them, and the persistence diagram being built.
    """
    # Create two square subplots with square aspect ratios
    if data_ax is None and pd_ax is None:
        fig, (data_ax, pd_ax) = plt.subplots(1, 2)
        fig.set_figwidth(10)
        data_ax.set_title("Data Set")
        data_ax.set_aspect("equal", adjustable="datalim")
        pd_ax.set_title("Persistence Diagram")
        pd_ax.set_aspect("equal")
    if (data_ax is None and pd_ax is not None) or (
        data_ax is not None and pd_ax is None
    ):
        raise ValueError("data_ax and pd_ax must be given together")
    if data_ax.figure is not pd_ax.figure:
        raise ValueError("data_ax and pd_ax must be from same figure")
    fig = data_ax.figure

    # Build persistence diagram and calculate how we need to scale the axes for
    # it
    pd = ripser.ripser(points)["dgms"][1]
    final_death = max(death for birth, death in pd)
    pd_ax_lim = final_death * 1.1
    radius_arrow_offset = pd_ax_lim / 50

    # Build initial state of the plots
    balls = [
        data_ax.add_patch(plt.Circle(point, 10, color="lightblue")) for point in points
    ]
    data_ax.plot(*points.T, "o")
    [radius_arrow] = pd_ax.plot(
        [radius_arrow_offset], [-radius_arrow_offset], marker=(3, 0, 45), markersize=10
    )
    pd_graph = pd_ax.scatter([], [])
    persim.plot_diagrams(
        np.zeros((1, 2)), ax=pd_ax, xy_range=[0, pd_ax_lim, 0, pd_ax_lim], legend=False
    )

    def init_animation():
        # This prevents the final frame from being displayed as if it were a
        # still figure
        plt.close(fig)

    def animate(frame):
        # Inflate balls
        for ball in balls:
            ball.set_radius(frame * 0.5 * (final_death / 100))
        dist = frame * (final_death / 100)
        # Plot points for living and dead loops according to ball radius. For
        # loops that are still alive, plot them as if they're about to die, a
        # bit transparent
        pd_pts = [(birth, min(death, dist)) for birth, death in pd if birth < dist]
        pd_graph.set_offsets(pd_pts)
        pd_graph.set_facecolors(
            [
                LIVE_POINT_COLOR if death < dist else DEAD_POINT_COLOR
                for birth, death in pd_pts
            ]
        )
        radius_arrow.set_data(
            [dist + radius_arrow_offset], [dist - radius_arrow_offset]
        )

    return animation.FuncAnimation(
        fig,
        animate,
        init_func=init_animation,
        frames=110,
        interval=50,
    )
