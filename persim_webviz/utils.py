import numpy as np

# Generates a dictionary that maps points in the given greedy permutation to colors
def generate_greedy_sketch_coloring(greedy_permutation):
    from greedy_sketch import DIAGONAL
    # Cool paper about these colors: https://eleanormaclure.files.wordpress.com/2011/03/colour-coding.pdf
    # White, black, and grey removed
    KELLY_COLORS = [
        '#F3C300', '#875692', '#F38400', '#A1CAF1', '#BE0032',
        '#C2B280', '#008856', '#E68FAC', '#0067A5', '#F99379',
        '#604E97', '#F6A600', '#B3446C', '#DCD300', '#882D17',
        '#8DB600', '#654522', '#E25822', '#2B3D26'
    ]
    sorted_points = sorted(greedy_permutation, key=lambda p1: np.linalg.norm(p1))
    mapping = {tuple(pt): KELLY_COLORS[i % len(KELLY_COLORS)] for i, pt in enumerate(sorted_points)}
    mapping[DIAGONAL] = '#848482' # Reserve grey for the diagonal
    return mapping