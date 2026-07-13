"""
Fit a sigmoid to each empirical depercolation curve and analyze how the
transition midpoint depends on node count.

Uses the sweep_summary.csv produced by run_empirical_depercolation_sweep.py.
By default picks the most recent empirical_deperc_sweep_* directory under
data/outputs/, but a specific run directory can be passed via --run-dir.

Sigmoid model:

    D(p) = 1 / (1 + exp(k * (p - p_c)))

where p_c is the transition midpoint (where D = 0.5) and k > 0 controls
steepness. As p -> 0 the model tends to 1; as p -> 1 it tends to 0. This
matches the observed shape of the depercolation curves.

Outputs (in the same run directory):
    - midpoints.csv                — one row per sheet with p_c, k, and stderr
    - figures/sigmoid_fits.png     — per-sheet fit overlay on data
    - figures/midpoint_vs_nodes.png — p_c vs node count (the money figure)

Usage:
    python scripts/analyze_deperc_midpoints.py
    python scripts/analyze_deperc_midpoints.py --run-dir data/outputs/empirical_deperc_sweep_20260713_080300
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.optimize import curve_fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def sigmoid(p: np.ndarray, p_c: float, k: float) -> np.ndarray:
    """
    Descending sigmoid: 1 at p=0, 0 at p=1, midpoint at p_c, steepness k.
    """
    return 1.0 / (1.0 + np.exp(k * (p - p_c)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fit sigmoids to empirical depercolation curves.")
    parser.add_argument(
        "--run-dir",
        default=None,
        help=(
            "Path to a specific empirical_deperc_sweep_<timestamp> directory. "
            "If omitted, uses the most recent one."
        ),
    )
    return parser.parse_args()


def find_latest_sweep_dir() -> Path:
    outputs = ROOT / "data" / "outputs"
    candidates = sorted(outputs.glob("empirical_deperc_sweep_*"))
    if not candidates:
        raise FileNotFoundError(
            "No empirical_deperc_sweep_* directories found under data/outputs/. "
            "Run scripts/run_empirical_depercolation_sweep.py first."
        )
    return candidates[-1]


def fit_one_sheet(sub: pd.DataFrame) -> dict:
    """
    Fit the descending sigmoid to one sheet's mean depercolation curve.
    Returns dict with p_c, k, and their standard errors.
    """
    p = sub["p"].to_numpy()
    d = sub["deperc_mean"].to_numpy()
    # Guard against zero std causing weight issues; substitute a small floor.
    sigma = sub["deperc_std"].to_numpy()
    sigma = np.where(sigma < 1e-6, 1e-6, sigma)

    # Initial guesses: p_c at the p where mean is closest to 0.5, k around 10.
    p_c_init = float(p[np.argmin(np.abs(d - 0.5))])
    k_init = 10.0

    try:
        popt, pcov = curve_fit(
            sigmoid,
            p,
            d,
            p0=[p_c_init, k_init],
            sigma=sigma,
            absolute_sigma=True,
            bounds=([0.0, 0.0], [1.0, 200.0]),
        )
        perr = np.sqrt(np.diag(pcov))
        return {
            "p_c": float(popt[0]),
            "k": float(popt[1]),
            "p_c_stderr": float(perr[0]),
            "k_stderr": float(perr[1]),
            "fit_ok": True,
        }
    except (RuntimeError, ValueError) as e:
        return {
            "p_c": np.nan,
            "k": np.nan,
            "p_c_stderr": np.nan,
            "k_stderr": np.nan,
            "fit_ok": False,
            "error": str(e),
        }


def plot_sigmoid_fits(
    summary: pd.DataFrame,
    fits: pd.DataFrame,
    output_path: Path,
) -> None:
    sheets = sorted(summary["sheet"].unique())
    n_cols = 3
    n_rows = (len(sheets) + n_cols - 1) // n_cols
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3.5 * n_rows), squeeze=False)

    p_smooth = np.linspace(0.0, 1.0, 200)
    for i, sheet in enumerate(sheets):
        ax = axs[i // n_cols][i % n_cols]
        sub = summary[summary["sheet"] == sheet].sort_values("p")
        ax.errorbar(
            sub["p"], sub["deperc_mean"], yerr=sub["deperc_std"],
            fmt="o", color="#1f77b4", markersize=4, capsize=2, label="data",
        )
        fit_row = fits[fits["sheet"] == sheet].iloc[0]
        if fit_row["fit_ok"]:
            d_fit = sigmoid(p_smooth, fit_row["p_c"], fit_row["k"])
            ax.plot(p_smooth, d_fit, color="#d62728", linewidth=2,
                    label=f"fit: $p_c$={fit_row['p_c']:.3f}, $k$={fit_row['k']:.2f}")
        ax.set_title(f"{sheet} (n={int(fit_row['num_nodes'])})")
        ax.set_xlabel("$p$")
        ax.set_ylabel("$D(G, p)$")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="lower left")

    # Blank any unused axes.
    for j in range(len(sheets), n_rows * n_cols):
        axs[j // n_cols][j % n_cols].axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_midpoint_vs_nodes(fits: pd.DataFrame, output_path: Path) -> None:
    """
    The money figure: scatter of p_c vs node count, with error bars, one point
    per sheet, plus a log-linear trend line fit across all fitted sheets.
    """
    protocol_1 = {"img1", "img2", "img3", "img4"}
    protocol_2 = {"saksham_img1", "saksham_img2"}

    ok = fits[fits["fit_ok"]].copy()
    log_n = np.log10(ok["num_nodes"].to_numpy())
    p_c = ok["p_c"].to_numpy()
    p_c_err = ok["p_c_stderr"].to_numpy()

    # Weighted linear regression of p_c vs log10(n) using p_c_stderr as weights.
    # Model: p_c = a * log10(n) + b
    w = 1.0 / np.maximum(p_c_err ** 2, 1e-12)
    coeffs, cov = np.polyfit(log_n, p_c, deg=1, w=w, cov=True)
    slope, intercept = coeffs[0], coeffs[1]
    slope_err = float(np.sqrt(cov[0, 0]))
    intercept_err = float(np.sqrt(cov[1, 1]))

    # Prediction interval on a dense grid for the shaded band.
    n_grid = np.logspace(np.log10(ok["num_nodes"].min() * 0.7),
                         np.log10(ok["num_nodes"].max() * 1.5), 200)
    log_n_grid = np.log10(n_grid)
    p_c_pred = slope * log_n_grid + intercept
    # Propagate uncertainty of the two coefficients (ignoring covariance for a
    # simple 1-sigma band — good enough for a paper figure).
    p_c_band = np.sqrt((log_n_grid * slope_err) ** 2 + intercept_err ** 2)

    fig, ax = plt.subplots(figsize=(7, 5))

    # Trend line and band first, so points sit on top.
    ax.fill_between(n_grid, p_c_pred - p_c_band, p_c_pred + p_c_band,
                    color="#7f7f7f", alpha=0.2, label="±1σ trend band")
    ax.plot(n_grid, p_c_pred, color="#7f7f7f", linewidth=1.5, linestyle="--",
            label=f"fit: $p_c = {slope:.3f} \\log_{{10}} n + {intercept:.3f}$")

    for _, row in fits.iterrows():
        if not row["fit_ok"]:
            continue
        color = "#1f77b4" if row["sheet"] in protocol_1 else "#d62728"
        marker = "o" if row["sheet"] in protocol_1 else "s"
        ax.errorbar(
            row["num_nodes"], row["p_c"], yerr=row["p_c_stderr"],
            fmt=marker, color=color, markersize=9, capsize=3, zorder=5,
        )
        ax.annotate(
            row["sheet"], (row["num_nodes"], row["p_c"]),
            textcoords="offset points", xytext=(7, 4), fontsize=9,
        )

    ax.scatter([], [], color="#1f77b4", marker="o", s=80, label="Protocol 1")
    ax.scatter([], [], color="#d62728", marker="s", s=80, label="Protocol 2")

    ax.set_xscale("log")
    ax.set_xlabel("Number of nodes (log scale)")
    ax.set_ylabel("Depercolation midpoint $p_c$")
    ax.set_title("Transition midpoint vs graph size")
    ax.grid(alpha=0.3, which="both")
    ax.legend(loc="best", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    # Print the fit result so it shows in the console.
    print(f"  Trend fit: p_c = {slope:.4f} (±{slope_err:.4f}) log10(n) + {intercept:.4f} (±{intercept_err:.4f})")

def main() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from proteinoid_complexity.io.excel import load_sheet_as_graph  # noqa: E402
    import yaml
    
    args = parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else find_latest_sweep_dir()
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir

    summary_csv = run_dir / "sweep_summary.csv"
    raw_csv = run_dir / "sweep_data.csv"
    if not summary_csv.exists():
        print(f"ERROR: {summary_csv} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {summary_csv}")
    summary = pd.read_csv(summary_csv)

    # Recover node counts from the raw sweep data. Each sheet's node count is
    # not stored in the summary directly, so we take it from the run_config or,
    # equivalently, re-derive by counting unique node coords from the raw xlsx.
    # Simpler: read from the raw CSV metadata if available; else fall back to
    # a hardcoded lookup based on what the pipeline reported. For robustness we
    # recompute from the xlsx here.

    config_path = run_dir / "run_config.yaml"
    with open(config_path) as f:
        run_config = yaml.safe_load(f)
    xlsx_path = ROOT / run_config["paths"]["raw_data"]

    print(f"Recovering node counts from {xlsx_path}")
    node_counts: dict[str, int] = {}
    for sheet in summary["sheet"].unique():
        G = load_sheet_as_graph(xlsx_path, sheet)
        node_counts[sheet] = G.number_of_nodes()

    print()
    print("Fitting sigmoids...")
    fit_records = []
    for sheet in sorted(summary["sheet"].unique()):
        sub = summary[summary["sheet"] == sheet].sort_values("p")
        fit = fit_one_sheet(sub)
        fit["sheet"] = sheet
        fit["num_nodes"] = node_counts[sheet]
        fit_records.append(fit)
        if fit["fit_ok"]:
            print(
                f"  {sheet:15s} n={node_counts[sheet]:5d}  "
                f"p_c={fit['p_c']:.4f} ± {fit['p_c_stderr']:.4f}   "
                f"k={fit['k']:.2f} ± {fit['k_stderr']:.2f}"
            )
        else:
            print(f"  {sheet:15s} FIT FAILED: {fit.get('error', 'unknown')}")

    fits = pd.DataFrame.from_records(fit_records)
    fits_csv = run_dir / "midpoints.csv"
    fits.to_csv(fits_csv, index=False)

    figures_dir = run_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    print()
    print("Rendering sigmoid fits...")
    plot_sigmoid_fits(summary, fits, figures_dir / "sigmoid_fits.png")

    print("Rendering midpoint vs node count...")
    plot_midpoint_vs_nodes(fits, figures_dir / "midpoint_vs_nodes.png")

    print()
    print(f"Wrote: {fits_csv}")
    print(f"Wrote: {figures_dir / 'sigmoid_fits.png'}")
    print(f"Wrote: {figures_dir / 'midpoint_vs_nodes.png'}")


if __name__ == "__main__":
    main()