"""
Random-graph sweep pipeline entry point.

Generates random 2D point clouds, builds Delaunay triangulations over them,
sweeps over a range of edge-removal fractions p, and records how the graph
metrics vary with p across many iterations.

Outputs a CSV of the raw sweep data plus a 2x2 PNG of metric-vs-p regplots.

Usage:
    python scripts/run_random_sweep.py
    python scripts/run_random_sweep.py --config config/default.yaml
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteinoid_complexity.graph_builders import delaunay_triangulation  # noqa: E402
from proteinoid_complexity.metrics import compute_all_metrics  # noqa: E402
from proteinoid_complexity.depercolation import (  # noqa: E402
    largest_cc_fraction,
    remove_random_edges,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Random-graph sweep over edge-removal fraction.")
    parser.add_argument(
        "--config",
        default=str(ROOT / "config" / "default.yaml"),
        help="Path to the YAML config file.",
    )
    return parser.parse_args()


def load_config(path: str | Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def random_points(min_nodes: int, max_nodes: int, scale: float) -> np.ndarray:
    n = random.randint(min_nodes, max_nodes)
    return np.random.rand(n, 2) * scale


def run_one(p: float, min_nodes: int, max_nodes: int, scale: float) -> dict:
    points = random_points(min_nodes, max_nodes, scale)
    G, _ = delaunay_triangulation(points)
    G_removed = remove_random_edges(G, p=p)

    deperc_ratio = largest_cc_fraction(G_removed)
    metrics = compute_all_metrics(G_removed)

    return {
        "p": p,
        "total_eff_resistance": metrics["total_effective_resistance"],
        "avg_shortest_path": metrics["avg_shortest_path"],
        "avg_edge_length": metrics["avg_edge_length"],
        "deperc_ratio": deperc_ratio,
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    seed = config["reproducibility"]["seed"]
    random.seed(seed)
    np.random.seed(seed)

    sweep_cfg = config["random_sweep"]
    num_iterations = sweep_cfg["num_iterations"]
    p_values = np.linspace(
        sweep_cfg["p_values_start"],
        sweep_cfg["p_values_end"],
        sweep_cfg["p_values_count"],
    )
    min_nodes = sweep_cfg["min_nodes"]
    max_nodes = sweep_cfg["max_nodes"]
    scale = sweep_cfg["scale"]

    outputs_root = ROOT / config["paths"]["outputs_root"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = outputs_root / f"random_sweep_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Writing results to {run_dir}")
    print(f"Seed: {seed}, iterations: {num_iterations}, p range: [{p_values[0]:.2f}, {p_values[-1]:.2f}] ({len(p_values)} points)")
    print(f"Nodes per graph: [{min_nodes}, {max_nodes}], scale: {scale}")
    print()

    records = []
    for iteration in range(num_iterations):
        for p in p_values:
            result = run_one(p, min_nodes, max_nodes, scale)
            result["iteration"] = iteration
            records.append(result)
        print(f"  iteration {iteration + 1}/{num_iterations} done")

    df = pd.DataFrame.from_records(records)
    csv_path = run_dir / "sweep_data.csv"
    df.to_csv(csv_path, index=False)

    # Plot: 2x2 grid of metric-vs-p regplots, one line per iteration.
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    properties = [
        "total_eff_resistance",
        "avg_shortest_path",
        "avg_edge_length",
        "deperc_ratio",
    ]
    palette = sns.color_palette("husl", n_colors=num_iterations)

    for i, col in enumerate(properties):
        ax = axs[i // 2, i % 2]
        for j in range(num_iterations):
            sns.regplot(
                x="p",
                y=col,
                data=df[df["iteration"] == j],
                scatter_kws={"s": 10},
                lowess=True,
                ax=ax,
                color=palette[j],
            )
        ax.set_title(f"{col} vs p")

    plt.tight_layout()
    plot_path = run_dir / "sweep_plot.png"
    plt.savefig(plot_path, dpi=150)
    plt.close(fig)

    # Save config snapshot for reproducibility.
    (run_dir / "run_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    print()
    print(f"Wrote: {csv_path}")
    print(f"Wrote: {plot_path}")
    print(f"Wrote: {run_dir / 'run_config.yaml'}")


if __name__ == "__main__":
    main()