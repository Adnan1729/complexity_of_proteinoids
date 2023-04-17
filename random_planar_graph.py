import numpy as np
import networkx as nx
import random
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

def random_points(min_nodes, max_nodes):
    n = random.randint(min_nodes, max_nodes)
    points = np.random.rand(n, 2)
    return points

def delaunay_triangulation(points):
    tri = Delaunay(points)
    G = nx.Graph()
    
    for simplex in tri.simplices:
        G.add_edges_from([(simplex[0], simplex[1]), (simplex[1], simplex[2]), (simplex[2], simplex[0])])
    
    return G, points

if __name__ == "__main__":
    points = random_points(100, 100)
    G, pos = delaunay_triangulation(points)
    nx.draw(G, pos, with_labels=True)
    plt.show()
