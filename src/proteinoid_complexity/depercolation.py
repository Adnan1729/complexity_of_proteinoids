"""
Depercolation computations.

The term *depercolation* denotes the process of removing edges from a formed
graph and measuring the resulting fragmentation. This is distinct from
*percolation* in the classical sense, which refers to the emergence of a
giant connected component under progressive edge addition to an initially
disconnected graph. The two thresholds coincide only for random-bond
formation processes; in non-ergodic formation processes such as the
proteinoid synthesis studied here, they can differ substantially.

Following the reviewer's observation, we adopt the term "depercolation"
throughout this module. See Sharma et al. (2026), revised methods section,
for the full discussion.

Two variants are implemented:

1. depercolation_ratio:
   The definition used in the paper. Remove a fraction p of edges at random,
   then divide the size of the largest connected component after removal by
   the size before removal. Value in [0, 1]: 1 means the graph stayed fully
   connected, 0 means it fragmented into singletons.

2. largest_cc_fraction:
   A related but distinct measure used by the random-sweep pipeline. Returns
   the fraction of nodes contained in the largest connected component of the
   (already edge-removed) graph, relative to the total node count. Not itself
   a depercolation quantity, but a useful summary of the LCC after removal.
"""

from __future__ import annotations

import random

import networkx as nx


def remove_random_edges(G: nx.Graph, p: float, rng: random.Random | None = None) -> nx.Graph:
    """
    Return a copy of G with a fraction p of its edges removed at random.

    Parameters
    ----------
    G : networkx.Graph
        Input graph. Not modified.
    p : float
        Fraction of edges to remove, in [0, 1].
    rng : random.Random, optional
        Random number generator for reproducibility. If None, uses the
        module-level random state.

    Returns
    -------
    networkx.Graph
        A new graph with the same nodes as G and (1 - p) fraction of its edges.
    """
    G_copy = G.copy()
    num_edges = len(G_copy.edges())
    num_to_remove = int(num_edges * p)

    edges = list(G_copy.edges())
    if rng is None:
        random.shuffle(edges)
    else:
        rng.shuffle(edges)

    for edge in edges[:num_to_remove]:
        G_copy.remove_edge(*edge)

    return G_copy


def depercolation_ratio(G_before: nx.Graph, G_after: nx.Graph) -> float:
    """
    Ratio of largest-connected-component sizes after vs before edge removal.

    Implements Eq. (X) of the revised paper:

        D(G, p) = C(G \\ E_p) / C(G)

    where C(H) is the size of the largest connected component of H and
    E_p is the set of removed edges.

    Returns 1.0 if the graph stayed fully intact under removal;
    approaches 0 as the graph fragments.
    """
    largest_before = len(max(nx.connected_components(G_before), key=len))
    largest_after = len(max(nx.connected_components(G_after), key=len))
    return largest_after / largest_before


def largest_cc_fraction(G: nx.Graph) -> float:
    """
    Fraction of nodes in the largest connected component of G.

    Distinct from depercolation_ratio: this is a property of a single graph,
    not a before/after comparison. Used by the random-sweep pipeline as a
    scalar summary of graph fragmentation.
    """
    if G.number_of_nodes() == 0:
        return 0.0
    if nx.is_connected(G):
        return 1.0
    largest = max(nx.connected_components(G), key=len)
    return len(largest) / G.number_of_nodes()