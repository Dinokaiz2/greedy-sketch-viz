import numpy as np

#get point closest to x on diagonal
def diagonal_point(x):
    return [(x[0]+x[1])/2, (x[0]+x[1])/2]

#compute l-infinity distance between 2 2-dpoints on persistence diagram
def l_inf(x1, x2):
    return max(abs(x1[1]-x2[1]), abs(x1[0]-x2[0]))

default_pd = np.array([[2, 4], [3, 6]])

#input is a persistence diagram, output is a greedy permutation of points. runs in O(n^2)
def naive_greedy_sketch(pd, n=-1, minimal=True):
    if n>len(pd):
        raise ValueError("Length of greedy permutation greater than number of points in persistence diagram")
    if n<0:
        n = len(pd)

    #To be returned at all times
    sketches = []                                         #greedy sketches to be returned
    transport_plans = []                                  #transportation plans of all sketches

    #Following to be returned iff minimal=False
    perm = np.empty((n,2))                                #stores points of pd ordered in a greedy permutation
    dist_seq = np.empty((n,1))                            #sequence of greedy distances which is also returned
    rnn = np.empty((len(pd), 2))                          #store reverse nearest neighbor of all points of pd
    dist = np.empty(len(pd))                              #store distances of every point in pd to its reverse nearest neighbor
    if not(minimal): voronoi = np.empty((n, len(pd), 2))  #discrete voronoi cells for each sketch
    
    max_dist = 0                                          #temporary variable to store maximum distance of the next greedy point within an iteration
    furthest = 0                                          #temporary variable to store furthest point index to compute the next greedy point
    
    #point [0,0] is the diagonal

    #initialize rnn data structure as reverse nearest neighbor of all points is the diagonal
    for i in range(len(pd)):
        rnn[i] = [0,0]
        dist[i] = l_inf(pd[i], diagonal_point(pd[i]))
        #print("Point = ("+str(pd[i][0])+", "+str(pd[i][1])+"), distance = "+str(dist[i]))
        if dist[i] > max_dist:
            max_dist = dist[i]
            furthest = i
    
    for i in range(n):
        #update reverse nearest neighbors of every point using newly added point
        perm[i] = pd[furthest].copy()
        dist_seq[i] = max_dist
        transport = dict()                               #temporary variable to store mass movement within successive sketches
        #print("Current round: "+str(i)+" furthest point: (" + str(round(pd[furthest][0],2))+", "+str(round(pd[furthest][1],2))+"), index: "+str(furthest))
        for j in range(len(pd)):
            if l_inf(pd[j], pd[furthest]) < dist[j]:
                #print("j: "+str(j)+ " point: (" + str(round(pd[j][0],2))+", "+str(round(pd[j][1],2))+") old rnn: ("+str(round(rnn[j][0],2))+", "+str(round(rnn[j][1],2))+"), old distance = "+str(round(dist[j],2))+" new rnn: ("+str(round(pd[furthest][0],2))+", "+str(round(pd[furthest][1],2))+"), new distance = "+str(round(l_inf(pd[j], pd[furthest]),2)))
                if tuple(rnn[j]) in transport:                  #one point lost by old rnn of j
                    transport[tuple(rnn[j])] -= 1                   
                else:
                    transport[tuple(rnn[j])] = -1
                rnn[j] = pd[furthest].copy()
                dist[j] = l_inf(pd[j], pd[furthest])
                if tuple(rnn[j]) in transport:                  #one point gained by new rnn of j
                    transport[tuple(rnn[j])] += 1
                else:
                    transport[tuple(rnn[j])] = 1

        #update max_dist and select next furthest point
        max_dist=0
        for j in range(len(pd)):
            if dist[j] > max_dist:
                max_dist = dist[j]
                furthest = j
        
        #store current voronoi diagram
        if not(minimal): voronoi[i] = rnn.copy()
        
        #append mass movement from previous sketch to the transportation plan
        transport_plans.append(transport)
                
    sketches = generate_sketches(perm, n=n)

    ret = {
        "sketches": sketches,
        "transport_plans": transport_plans
        }

    if not(minimal):
        ret["dist"]=dist_seq
        ret["voronoi"]=voronoi
        ret["perm"]=perm
    
    return ret

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