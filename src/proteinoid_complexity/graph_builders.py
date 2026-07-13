"""
Graph construction from raw inputs.

Two builders live here:
    - build_graph_from_edge_list: for empirical data (xlsx rows of x1,y1,x2,y2)
    - delaunay_triangulation:     for synthetic data (random point clouds)

Both return a networkx.Graph with edge weights set to Euclidean distance.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.spatial import Delaunay


def build_graph_from_edge_list(edge_rows) -> nx.Graph:
    """
    Build an undirected graph from an iterable of (x1, y1, x2, y2) rows.

    Each row defines a single edge between node (x1, y1) and node (x2, y2).
    Edge weight is set to the Euclidean distance between the two endpoints.
    Nodes are identified by their (x, y) coordinate tuple.

    Parameters
    ----------
    edge_rows : iterable of tuples (x1, y1, x2, y2)
        Typically comes from iterating rows of the input dataframe.

    Returns
    -------
    networkx.Graph
    """
    G = nx.Graph()

    # Two passes to exactly mirror the original script's structure:
    # first pass adds nodes, second pass adds edges.
    rows = list(edge_rows)

    for x1, y1, x2, y2 in rows:
        G.add_node((x1, y1))
        G.add_node((x2, y2))

    for x1, y1, x2, y2 in rows:
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        G.add_edge((x1, y1), (x2, y2), weight=distance)

    return G


def delaunay_triangulation(points) -> tuple[nx.Graph, np.ndarray]:
    """
    Build a Delaunay triangulation graph over a set of 2D points.

    Parameters
    ----------
    points : array-like of shape (n, 2)
        The 2D coordinates of the nodes.

    Returns
    -------
    G : networkx.Graph
        Nodes are integer indices 0..n-1, each with a 'pos' attribute
        holding the (x, y) coordinate. Edges are the triangulation edges,
        weighted by Euclidean distance.
    points : np.ndarray
        The input points, returned for downstream convenience.
    """
    points = np.asarray(points)
    tri = Delaunay(points)
    G = nx.Graph()

    for i, point in enumerate(points):
        G.add_node(i, pos=point)

    for simplex in tri.simplices:
        u, v, w = simplex
        u_coord, v_coord, w_coord = points[u], points[v], points[w]
        G.add_edge(u, v, weight=np.linalg.norm(np.subtract(u_coord, v_coord)))
        G.add_edge(v, w, weight=np.linalg.norm(np.subtract(v_coord, w_coord)))
        G.add_edge(w, u, weight=np.linalg.norm(np.subtract(w_coord, u_coord)))

    return G, points


def largest_connected_component_subgraph(G: nx.Graph) -> nx.Graph:
    """
    If G is disconnected, return the subgraph induced by its largest
    connected component. If already connected, return G unchanged.

    This is the standard pre-processing step before Floyd-Warshall, since
    shortest paths are undefined between disconnected components.
    """
    if nx.is_connected(G):
        return G
    components = sorted(nx.connected_components(G), key=len, reverse=True)
    return G.subgraph(components[0])