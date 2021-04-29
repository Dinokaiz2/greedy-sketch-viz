from collections import defaultdict

import numpy as np
import persim
import sketch as gs

import pytest

default_pd = [[2,4],[3,6],[4,8],[5,10], [6,24], [7,35], [10,50], [12,60]]
single_pd = [[2,4]]
double_pd = [[2,4], [3,6]]

class TestSketch:
    def test_diagonal_point(self):
        '''Case: Correct point mapped to diagonal returned'''
        x = gs.diagonal_point([2,4])
        assert x == (3,3)
    
    def test_l_inf(self):
        '''Case: Correct l_inf distance calculated'''
        d = gs.l_inf([2,4], [3,6])
        assert d == 2
    
    def test_greedy_single_perm(self):
        '''Case: Correct greedy permutation computed for a single point pd'''
        single_pd_sketch = gs.naive_greedy_sketch(single_pd)
        assert (single_pd_sketch['perm'] == [[2,4]]).all()

    def test_greedy_single_transport(self):
        '''Case: Correct transportation plan computed for a single point pd'''
        single_pd_sketch = gs.naive_greedy_sketch(single_pd)
        plans = [{(0,0): 1},
            {(0,0): -1, (2,4):1}]
        assert single_pd_sketch['transport_plans'] == plans

    def test_greedy_double_perm(self):
        '''Case: Correct greedy permutation computed for a double point pd'''
        double_pd_sketch = gs.naive_greedy_sketch(double_pd)
        assert (double_pd_sketch['perm'] == [[3,6], [2,4]]).all()
    
    def test_greedy_double_transport(self):
        '''Case: Correct transportation plan computed for a double point pd'''
        double_pd_sketch = gs.naive_greedy_sketch(double_pd)
        plans = [{(0,0): 2},
            {(0,0): -1, (3,6):1},
            {(0,0): -1, (2,4):1}]
        assert double_pd_sketch['transport_plans'] == plans
    
    def test_greedy_perm(self):
        '''Case: Correct greedy permutation computed for an 8 point pd'''
        pd_sketch = gs.naive_greedy_sketch(default_pd)
        assert (pd_sketch['perm'] ==  [[12,60], [7,35], [10, 50], [6, 24], [5, 10], [4, 8], [3, 6], [2, 4]]).all()

    def test_greedy_transport(self):
        '''Case: Correct transportation plan computed for an 8 point pd'''
        pd_sketch = gs.naive_greedy_sketch(default_pd)

        plans = [{(0, 0): 8}, 
            {(0, 0): -2, (12, 60): 2}, 
            {(0, 0): -1, (7, 35): 1}, 
            {(12, 60): -1, (10, 50): 1}, 
            {(0, 0): -1, (6, 24): 1}, 
            {(0, 0): -1, (5, 10): 1}, 
            {(0, 0): -1, (4, 8): 1}, 
            {(0, 0): -1, (3, 6): 1}, 
            {(0, 0): -1, (2, 4): 1}]
        assert pd_sketch['transport_plans']==plans

    def test_greedy_voronoi(self):
        '''Case: Correct voronoi cells computed for a pd'''
        voronoi0 = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        voronoi1 = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[12,60],[12,60]]
        voronoi8 = [[2,4],[3,6],[4,8],[5,10], [6,24], [7,35], [10,50], [12,60]]
        pd_sketch = gs.naive_greedy_sketch(default_pd, minimal=False)
        assert (voronoi0==pd_sketch['voronoi'][0]).all()
        assert (voronoi1==pd_sketch['voronoi'][1]).all()
        assert (voronoi8==pd_sketch['voronoi'][8]).all()
    
    def test_greedy_dist(self):
        '''Case: Correct greedy distances computed for an 8 point pd'''
        dist_seq = [[24],[14],[10],[9],[2.5],[2],[1.5],[1]]
        pd_sketch = gs.naive_greedy_sketch(default_pd, minimal=False)
        assert (dist_seq==pd_sketch['dist']).all()

    def test_mult(self):
        '''Case: compute_mult computes multiplicities correctly'''
        pd_sketch = gs.naive_greedy_sketch(default_pd, minimal=False)
        transport_plans = pd_sketch['transport_plans']
        mult0 = {(0,0): 8}
        mult1 = {(0,0): 6, (12,60): 2}
        mult8 = {(0,0): 0, (2,4): 1, (3,6): 1, (4,8): 1, (5,10): 1, (6,24): 1, (7,35): 1, (10,50): 1, (12,60): 1}
        mult = gs.compute_mult(transport_plans[:1])
        assert(mult == mult0)
        mult = gs.compute_mult(transport_plans[:2])
        assert(mult == mult1)
        mult = gs.compute_mult(transport_plans[:9])
        assert(mult == mult8)

    def test_intersketch_bd_same(self):
        '''Case: Correct bottleneck distance computed for 2 non successive sketches of the same pd'''
        pd_sketch = gs.naive_greedy_sketch(default_pd, minimal=False)
        perm = pd_sketch['perm']
        transport_plans = pd_sketch['transport_plans']
        assert(gs.intersketch_bd(perm[:1], transport_plans[:2], perm[:8], transport_plans[:9]) == 14)

    def test_intersketch_bd_diff(self):
        '''Case: Correct bottleneck distance computed for 2 non successive sketches of different pds'''
        pd_sketch = gs.naive_greedy_sketch(default_pd)
        perm = pd_sketch['perm']
        transport_plans = pd_sketch['transport_plans']
        
        double_pd_sketch = gs.naive_greedy_sketch(double_pd)
        double_perm = double_pd_sketch['perm']
        double_transport_plans = double_pd_sketch['transport_plans']

        assert(gs.intersketch_bd(perm[:1], transport_plans[:2], double_perm[:1], double_transport_plans[:2]) == 24)       
