"""
Empirical pipeline entry point.

Reads the raw xlsx, computes complexity metrics for each sheet, computes
depercolation ratios (both variants if configured), draws each graph,
and writes a CSV + HTML report to a timestamped output folder.

Usage:
    python scripts/run_empirical.py
    python scripts/run_empirical.py --config config/default.yaml
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

# Make the src package importable when running as a script.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteinoid_complexity.graph_builders import delaunay_triangulation  # noqa: E402
from proteinoid_complexity.io.excel import load_sheet_as_graph  # noqa: E402
from proteinoid_complexity.io.report import write_csv, write_html  # noqa: E402
from proteinoid_complexity.metrics import compute_all_metrics  # noqa: E402
from proteinoid_complexity.depercolation import (  # noqa: E402
    depercolation_ratio,
    remove_random_edges,
)
from proteinoid_complexity.visualization import draw_graph_to_png  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the empirical proteinoid pipeline.")
    parser.add_argument(
        "--config",
        default=str(ROOT / "config" / "default.yaml"),
        help="Path to the YAML config file.",
    )
    return parser.parse_args()


def load_config(path: str | Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    seed = config["reproducibility"]["seed"]
    random.seed(seed)
    np.random.seed(seed)

    xlsx_path = ROOT / config["paths"]["raw_data"]
    outputs_root = ROOT / config["paths"]["outputs_root"]
    sheet_names = config["empirical"]["sheet_names"]
    p_removal = config["depercolation"]["edge_removal_fraction"]
    deperc_mode = config["depercolation"]["mode"]  # "empirical", "fresh_delaunay", or "both"

    do_deperc_empirical = deperc_mode in ("empirical", "both")
    do_deperc_fresh = deperc_mode in ("fresh_delaunay", "both")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = outputs_root / f"empirical_{timestamp}"
    figures_dir = run_dir / "figures"
    run_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading {xlsx_path}")
    print(f"Writing results to {run_dir}")
    print(f"Seed: {seed}, edge removal fraction: {p_removal}, mode: {deperc_mode}")
    print()

    rows: list[dict] = []
    figure_paths: dict[str, Path] = {}

    for sheet in sheet_names:
        print(f"Processing sheet: {sheet}")
        G = load_sheet_as_graph(xlsx_path, sheet)

        metrics = compute_all_metrics(G)

        # Depercolation on the empirical graph itself.
        deperc_empirical = None
        if do_deperc_empirical:
            G_removed = remove_random_edges(G, p=p_removal)
            deperc_empirical = depercolation_ratio(G, G_removed)

        # Depercolation on a fresh Delaunay triangulation of the empirical node
        # set. This preserves the paper's original computation.
        deperc_fresh = None
        if do_deperc_fresh:
            points = [(x, y) for x, y in G.nodes()]
            G_delaunay, _ = delaunay_triangulation(points)
            G_delaunay_removed = remove_random_edges(G_delaunay, p=p_removal)
            deperc_fresh = depercolation_ratio(G_delaunay, G_delaunay_removed)

        # Draw the empirical graph.
        fig_path = draw_graph_to_png(G, figures_dir / f"graph_{sheet}.png")
        figure_paths[sheet] = fig_path

        row = {
            "sheet": sheet,
            **metrics,
            "deperc_empirical": deperc_empirical,
            "deperc_fresh_delaunay": deperc_fresh,
        }
        rows.append(row)

        print(f"  nodes={metrics['num_nodes']}, edges={metrics['num_edges']}")
        print(f"  avg_shortest_path={metrics['avg_shortest_path']:.4f}")
        print(f"  avg_edge_length={metrics['avg_edge_length']:.4f}")
        print(f"  total_effective_resistance={metrics['total_effective_resistance']:.4f}")
        if deperc_empirical is not None:
            print(f"  deperc_empirical={deperc_empirical:.4f}")
        if deperc_fresh is not None:
            print(f"  deperc_fresh_delaunay={deperc_fresh:.4f}")
        print()

    # Write outputs.
    csv_path = write_csv(rows, run_dir / "metrics.csv")
    html_path = write_html(
        rows=rows,
        figure_paths=figure_paths,
        output_path=run_dir / "report.html",
        title="Proteinoid empirical pipeline results",
        timestamp=timestamp,
        config_summary=f"seed={seed}, p_removal={p_removal}, mode={deperc_mode}",
        show_deperc_empirical=do_deperc_empirical,
        show_deperc_fresh=do_deperc_fresh,
    )

    # Save a snapshot of the config used, for reproducibility.
    (run_dir / "run_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {html_path}")
    print(f"Wrote: {run_dir / 'run_config.yaml'}")


if __name__ == "__main__":
    main()