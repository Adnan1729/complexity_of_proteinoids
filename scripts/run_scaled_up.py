"""
Scaled-up random-graph pipeline entry point.

Iterates over N random Delaunay graphs (no edge removal), computes metrics
for each, and writes a CSV plus an HTML report with per-graph PNGs.

Replaces the old scaled_up.py.

Usage:
    python scripts/run_scaled_up.py
    python scripts/run_scaled_up.py --config config/default.yaml
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteinoid_complexity.graph_builders import delaunay_triangulation  # noqa: E402
from proteinoid_complexity.io.report import write_csv, write_html  # noqa: E402
from proteinoid_complexity.metrics import compute_all_metrics  # noqa: E402
from proteinoid_complexity.visualization import draw_graph_to_png  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the scaled-up random-graph pipeline.")
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


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    seed = config["reproducibility"]["seed"]
    random.seed(seed)
    np.random.seed(seed)

    cfg = config["scaled_up"]
    num_iterations = cfg["num_iterations"]
    min_nodes = cfg["min_nodes"]
    max_nodes = cfg["max_nodes"]
    scale = cfg["scale"]

    outputs_root = ROOT / config["paths"]["outputs_root"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = outputs_root / f"scaled_up_{timestamp}"
    figures_dir = run_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    print(f"Writing results to {run_dir}")
    print(f"Seed: {seed}, iterations: {num_iterations}")
    print(f"Nodes per graph: [{min_nodes}, {max_nodes}], scale: {scale}")
    print()

    rows: list[dict] = []
    figure_paths: dict[str, Path] = {}

    for i in range(num_iterations):
        label = f"graph_{i:03d}"
        print(f"Processing {label}")

        points = random_points(min_nodes, max_nodes, scale)
        G, _ = delaunay_triangulation(points)
        metrics = compute_all_metrics(G)

        fig_path = draw_graph_to_png(G, figures_dir / f"{label}.png")
        figure_paths[label] = fig_path

        row = {
            "sheet": label,
            **metrics,
            "deperc_empirical": None,
            "deperc_fresh_delaunay": None,
        }
        rows.append(row)

        print(f"  nodes={metrics['num_nodes']}, edges={metrics['num_edges']}")
        print(f"  avg_shortest_path={metrics['avg_shortest_path']:.4f}")
        print(f"  avg_edge_length={metrics['avg_edge_length']:.4f}")
        print(f"  total_effective_resistance={metrics['total_effective_resistance']:.4f}")
        print()

    csv_path = write_csv(rows, run_dir / "metrics.csv")
    html_path = write_html(
        rows=rows,
        figure_paths=figure_paths,
        output_path=run_dir / "report.html",
        title="Scaled-up random-graph pipeline results",
        timestamp=timestamp,
        config_summary=f"seed={seed}, iterations={num_iterations}, nodes=[{min_nodes},{max_nodes}], scale={scale}",
        show_deperc_empirical=False,
        show_deperc_fresh=False,
    )
    (run_dir / "run_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {html_path}")
    print(f"Wrote: {run_dir / 'run_config.yaml'}")


if __name__ == "__main__":
    main()