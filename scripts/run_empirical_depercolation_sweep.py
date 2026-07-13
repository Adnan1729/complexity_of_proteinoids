"""
Empirical depercolation sweep pipeline entry point.

For each sheet in the raw xlsx, this script:
    1. Builds the empirical graph.
    2. Sweeps the edge-removal fraction p over a user-specified range.
    3. At each p, runs N random realizations of edge removal.
    4. Records the depercolation ratio D(G, p) for each realization.
    5. Aggregates mean and standard deviation per (sheet, p).

Outputs (in data/outputs/empirical_deperc_sweep_<timestamp>/):
    - sweep_data.csv       — raw per-realization records
    - sweep_summary.csv    — mean and std per (sheet, p)
    - figures/curve_<sheet>.png  — one curve per sheet with error band
    - figures/overlay.png  — all sheets on one axis for comparison
    - run_config.yaml      — reproducibility snapshot

This is the empirical analogue of run_random_sweep.py, but operating on the
six real proteinoid graphs from the paper rather than random Delaunay graphs.
Produces the supplementary figure that answers reviewer comment 4.

Usage:
    python scripts/run_empirical_depercolation_sweep.py
    python scripts/run_empirical_depercolation_sweep.py --config config/default.yaml
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
import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteinoid_complexity.depercolation import (  # noqa: E402
    depercolation_ratio,
    remove_random_edges,
)
from proteinoid_complexity.io.excel import load_sheet_as_graph  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Depercolation sweep over the empirical proteinoid graphs."
    )
    parser.add_argument(
        "--config",
        default=str(ROOT / "config" / "default.yaml"),
        help="Path to the YAML config file.",
    )
    return parser.parse_args()


def load_config(path: str | Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def sweep_single_graph(
    G, p_values: np.ndarray, n_realizations: int, rng: random.Random
) -> list[dict]:
    """
    Implements Algorithm 3 (DepercolationSweep) for one graph.

    Returns one record per (p, realization) pair.
    """
    records = []
    for p in p_values:
        for n in range(n_realizations):
            G_removed = remove_random_edges(G, p=float(p), rng=rng)
            D = depercolation_ratio(G, G_removed)
            records.append({"p": float(p), "realization": n, "deperc_ratio": D})
    return records


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mean and standard deviation of deperc_ratio per (sheet, p).
    """
    summary = (
        df.groupby(["sheet", "p"])["deperc_ratio"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={"mean": "deperc_mean", "std": "deperc_std", "count": "n"})
    )
    return summary


def plot_per_sheet_curve(
    summary: pd.DataFrame, sheet: str, output_path: Path
) -> None:
    sub = summary[summary["sheet"] == sheet].sort_values("p")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(sub["p"], sub["deperc_mean"], color="#1f77b4", linewidth=2, label="mean")
    ax.fill_between(
        sub["p"],
        sub["deperc_mean"] - sub["deperc_std"],
        sub["deperc_mean"] + sub["deperc_std"],
        color="#1f77b4",
        alpha=0.25,
        label="±1 std",
    )
    ax.set_xlabel("edge removal fraction $p$")
    ax.set_ylabel("depercolation ratio $D(G, p)$")
    ax.set_title(f"Depercolation curve — {sheet}")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_overlay(summary: pd.DataFrame, output_path: Path) -> None:
    sheets = sorted(summary["sheet"].unique())
    colors = plt.cm.tab10(np.linspace(0, 1, len(sheets)))

    fig, ax = plt.subplots(figsize=(8, 5))
    for sheet, color in zip(sheets, colors):
        sub = summary[summary["sheet"] == sheet].sort_values("p")
        ax.plot(sub["p"], sub["deperc_mean"], color=color, linewidth=2, label=sheet)
        ax.fill_between(
            sub["p"],
            sub["deperc_mean"] - sub["deperc_std"],
            sub["deperc_mean"] + sub["deperc_std"],
            color=color,
            alpha=0.15,
        )
    ax.set_xlabel("edge removal fraction $p$")
    ax.set_ylabel("depercolation ratio $D(G, p)$")
    ax.set_title("Depercolation curves — all empirical graphs")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

def plot_overlay_by_node_count(
    summary: pd.DataFrame, node_counts: dict[str, int], output_path: Path
) -> None:
    """
    Same data as plot_overlay, but colors curves by node count instead of by
    sheet identity, and orders the legend by node count. Helps distinguish
    finite-size effects from protocol-level differences.
    """
    sheets_by_size = sorted(node_counts.keys(), key=lambda s: node_counts[s])
    cmap = plt.cm.viridis
    norm = plt.Normalize(vmin=min(node_counts.values()), vmax=max(node_counts.values()))

    fig, ax = plt.subplots(figsize=(8, 5))
    for sheet in sheets_by_size:
        sub = summary[summary["sheet"] == sheet].sort_values("p")
        color = cmap(norm(node_counts[sheet]))
        label = f"{sheet} (n={node_counts[sheet]})"
        ax.plot(sub["p"], sub["deperc_mean"], color=color, linewidth=2, label=label)
        ax.fill_between(
            sub["p"],
            sub["deperc_mean"] - sub["deperc_std"],
            sub["deperc_mean"] + sub["deperc_std"],
            color=color,
            alpha=0.15,
        )
    ax.set_xlabel("edge removal fraction $p$")
    ax.set_ylabel("depercolation ratio $D(G, p)$")
    ax.set_title("Depercolation curves — colored by node count")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    seed = config["reproducibility"]["seed"]
    # Use a dedicated RNG so this script's randomness is independent of other
    # scripts that may share the module-level random state.
    rng = random.Random(seed)
    np.random.seed(seed)

    xlsx_path = ROOT / config["paths"]["raw_data"]
    outputs_root = ROOT / config["paths"]["outputs_root"]
    sheet_names = config["empirical"]["sheet_names"]

    sweep_cfg = config["empirical_deperc_sweep"]
    p_min = sweep_cfg["p_min"]
    p_max = sweep_cfg["p_max"]
    n_steps = sweep_cfg["n_steps"]
    n_realizations = sweep_cfg["n_realizations"]

    p_values = np.linspace(p_min, p_max, n_steps)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = outputs_root / f"empirical_deperc_sweep_{timestamp}"
    figures_dir = run_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading {xlsx_path}")
    print(f"Writing results to {run_dir}")
    print(
        f"Seed: {seed}, p range: [{p_min}, {p_max}] "
        f"({n_steps} steps), realizations per p: {n_realizations}"
    )
    print()

    all_records = []
    node_counts: dict[str, int] = {}
    for sheet in sheet_names:
        print(f"Processing sheet: {sheet}")
        G = load_sheet_as_graph(xlsx_path, sheet)
        node_counts[sheet] = G.number_of_nodes()
        print(f"  nodes={G.number_of_nodes()}, edges={G.number_of_edges()}")

        records = sweep_single_graph(G, p_values, n_realizations, rng)
        for r in records:
            r["sheet"] = sheet
        all_records.extend(records)
        print(f"  {len(records)} realizations recorded")

    df = pd.DataFrame.from_records(all_records)
    # Reorder columns for readability.
    df = df[["sheet", "p", "realization", "deperc_ratio"]]

    raw_csv = run_dir / "sweep_data.csv"
    df.to_csv(raw_csv, index=False)

    summary = summarize(df)
    summary_csv = run_dir / "sweep_summary.csv"
    summary.to_csv(summary_csv, index=False)

    print()
    print("Rendering per-sheet curves...")
    for sheet in sheet_names:
        plot_per_sheet_curve(summary, sheet, figures_dir / f"curve_{sheet}.png")
    print("Rendering overlay...")
    plot_overlay(summary, figures_dir / "overlay.png")
    print("Rendering overlay by node count...")
    plot_overlay_by_node_count(summary, node_counts, figures_dir / "overlay_by_node_count.png")

    (run_dir / "run_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    print()
    print(f"Wrote: {raw_csv}")
    print(f"Wrote: {summary_csv}")
    print(f"Wrote: {figures_dir}")


if __name__ == "__main__":
    main()