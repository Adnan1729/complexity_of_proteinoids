"""
Minimal Delaunay demo — draws a triangulation of 10 random points.

Kept as a smoke test for the graph_builders module. Saves a single PNG.

Usage:
    python scripts/demo_delaunay.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteinoid_complexity.graph_builders import delaunay_triangulation  # noqa: E402


def main() -> None:
    np.random.seed(42)
    points = np.random.rand(10, 2)
    G, pts = delaunay_triangulation(points)

    pos = {i: pts[i] for i in G.nodes}
    fig = plt.figure()
    nx.draw(G, pos, with_labels=True, node_color="#c0c0c0", node_size=300)

    output_path = ROOT / "data" / "outputs" / "demo_delaunay.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close(fig)

    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()