import numpy as np

#get point closest to x on diagonal
def diagonal_point(x):
    return [(x[0]+x[1])/2, (x[0]+x[1])/2]

#compute l-infinity distance between 2 2-dpoints on persistence diagram
def l_inf(x1, x2):
    return max(abs(x1[1]-x2[1]), abs(x1[0]-x2[0]))

default_pd = np.array([[2, 4], [3, 6]])

#input is a persistence diagram, output is a greedy permutation of points. runs in O(n^2)
def naive_greedy_perm(pd=default_pd, n=-1):
    if n>len(pd):
        raise ValueError("Length of greedy permutation greater than number of points in persistence diagram")
    if n<0:
        n = len(pd)
    perm = np.empty(n, dtype=np.int64)                    #stores indices of points of pd according to greedy permutation
    perm_points = np.empty((n,2))                         #to be returned: points according to greedy permutation
    dist_seq = np.empty((n,1))                            #sequence of greedy distances which is also returned

    rnn = np.empty((len(pd), 2))                          #store reverse nearest neighbor of all points of pd
    dist = np.empty(len(pd))                              #store distances of every point in pd to its reverse nearest neighbor
    
    max_dist = 0                                          #temporary variable to store maximum distance of the next greedy point within an iteration
    furthest = 0                                          #temporary variable to store 
    
    #point [0,0] is the diagonal

    #initialize rnn data structure to sketch 0 as reverse nearest neighbor of all points is the diagonal
    for i in range(len(pd)):
        rnn[i] = [0,0]
        dist[i] = l_inf(pd[i], diagonal_point(pd[i]))
        #print("Point = ("+str(pd[i][0])+", "+str(pd[i][1])+"), distance = "+str(dist[i]))
        if dist[i] > max_dist:
            max_dist = dist[i]
            furthest = i
    
    for i in range(n):
        #update reverse nearest neighbors of every point using newly added point
        perm[i] = furthest
        dist_seq[i] = max_dist
        #print("Current round: "+str(i)+" furthest point: (" + str(round(pd[furthest][0],2))+", "+str(round(pd[furthest][1],2))+"), index: "+str(furthest))
        for j in range(len(pd)):
            if l_inf(pd[j], pd[furthest]) < dist[j]:
                #print("j: "+str(j)+ " point: (" + str(round(pd[j][0],2))+", "+str(round(pd[j][1],2))+") old rnn: ("+str(round(rnn[j][0],2))+", "+str(round(rnn[j][1],2))+"), old distance = "+str(round(dist[j],2))+" new rnn: ("+str(round(pd[furthest][0],2))+", "+str(round(pd[furthest][1],2))+"), new distance = "+str(round(l_inf(pd[j], pd[furthest]),2)))
                rnn[j] = pd[furthest].copy()
                dist[j] = l_inf(pd[j], pd[furthest])
        #update max_dist and select next furthest point
        max_dist=0
        for j in range(len(pd)):
            if dist[j] > max_dist:
                max_dist = dist[j]
                furthest = j
    
    for i in range(n):
        perm_points[i] = pd[perm[i]].copy()
    return perm_points, dist_seq

#input is a greedy sequence of points of a pd. output is a series of greedy sketches of that pd.
def generate_sketches(perm, n=-1):
    if n>len(perm):
        raise ValueError("Number of sketches requested is greater than number of points in greedy permutation")
    if n<0:
        n = len(perm)
    sketches = []
    for i in range(1, n+1):
        sketch = np.empty((i,2))
        for j in range(i):
            sketch[j][0] = perm[j][0]
            sketch[j][1] = perm[j][1]
        sketches.append(sketch)
    return sketches