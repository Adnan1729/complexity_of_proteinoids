"""
Complexity and information-transmission metrics for proteinoid graphs.

The three metrics implemented here are all derived from the all-pairs shortest
paths matrix computed via Floyd-Warshall:
    - total effective resistance
    - average shortest path
    - average edge length

These reproduce the values reported in Sharma et al. (2026), Fig. 6.
"""

from __future__ import annotations

import networkx as nx

from .graph_builders import largest_connected_component_subgraph


def compute_all_metrics(G: nx.Graph) -> dict[str, float]:
    """
    Compute the three deterministic metrics on graph G.

    G is first reduced to its largest connected component if disconnected,
    because Floyd-Warshall requires a connected graph for finite path lengths.

    Parameters
    ----------
    G : networkx.Graph
        Weighted, undirected graph.

    Returns
    -------
    dict with keys:
        'total_effective_resistance'
        'avg_shortest_path'
        'avg_edge_length'
        'num_nodes'
        'num_edges'
    """
    G = largest_connected_component_subgraph(G)

    all_pairs_shortest_paths = nx.algorithms.shortest_paths.floyd_warshall_numpy(G)

    # Total effective resistance: sum of 1 / shortest_path_length over all node pairs (i < j).
    total_effective_resistance = 0.0
    nodes = list(G.nodes)
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i < j:
                shortest_path_length = all_pairs_shortest_paths[i][j]
                effective_resistance = 1 / shortest_path_length
                total_effective_resistance += effective_resistance

    # Average shortest path: sum of the entire matrix divided by n*(n-1).
    # Note: this includes both (i,j) and (j,i) since the matrix is symmetric,
    # and the diagonal is zero, so the normalisation n*(n-1) is consistent.
    total_shortest_paths = sum(sum(row) for row in all_pairs_shortest_paths)
    n = len(nodes)
    average_shortest_path = total_shortest_paths / (n * (n - 1))

    # Average edge length: mean of the edge weights.
    total_edge_lengths = sum(G.edges[edge]["weight"] for edge in G.edges)
    average_edge_length = total_edge_lengths / len(G.edges)

    return {
        "total_effective_resistance": float(total_effective_resistance),
        "avg_shortest_path": float(average_shortest_path),
        "avg_edge_length": float(average_edge_length),
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
    }