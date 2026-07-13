"""
Graph plotting helpers.

Kept intentionally minimal — matplotlib + networkx defaults, no styling.
The point is to produce the same graph_<name>.png files the original
scripts produced, so figures in the report look familiar.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

# Use a non-interactive backend so this works in headless / script contexts
# without opening plot windows.
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402


def draw_graph_to_png(G: nx.Graph, output_path: str | Path, node_size: int = 15) -> Path:
    """
    Draw G with a spring layout and save to output_path.

    Parameters
    ----------
    G : networkx.Graph
    output_path : str or Path
        Where to save the PNG. Parent directories are created if missing.
    node_size : int
        Passed through to networkx.draw_networkx_nodes.

    Returns
    -------
    Path
        The path the figure was written to.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure()
    try:
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=node_size)
        nx.draw_networkx_edges(G, pos)
        plt.savefig(output_path)
    finally:
        plt.close(fig)

    return output_path