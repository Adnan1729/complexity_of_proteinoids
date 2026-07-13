# Proteinoid Complexity Analysis

Image-to-graph pipeline and complexity-metric analysis for proteinoid microsphere
ensembles. This is the code accompanying the paper:

> Sharma, S., Mahmud, A., Adamatzky, A., Mougkogiannis, P., Tarabella, G.
> *Morphological and functional complexity of fluidic proteinoid microspheres.*
> (Under revision, 2026.)

Given SEM or optical micrographs of proteinoid samples that have been transcribed
into edge-list form (via Fiji's Delaunay-Voronoi plugin), this codebase computes
nine graph-theoretic complexity and information-transmission metrics, plus a
full depercolation sweep with finite-size scaling analysis.

## Quick start

```bash
# Clone and enter the repo
git clone https://github.com/Adnan1729/complexity_analysis.git
cd complexity_analysis

# Create a venv and install
python -m venv venv
source venv/bin/activate           # on Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Verify by running the regression tests
pytest -v

# Reproduce the paper's empirical results
python scripts/run_empirical.py

# Reproduce the finite-size scaling analysis (Appendix A of the paper)
python scripts/run_empirical_depercolation_sweep.py
python scripts/analyze_deperc_midpoints.py
```

Outputs land in `data/outputs/<pipeline>_<timestamp>/`, one folder per run, each
containing a CSV of metrics, an HTML report with embedded figures, a snapshot of
the config used, and a `figures/` subfolder with the individual plots.

## Repository structure

```
complexity_of_proteinoids/
├── config/
│   └── default.yaml          # all pipeline parameters
├── data/
│   ├── raw/
│   │   └── img_nodes_2.xlsx  # source data: one sheet per image
│   └── outputs/              # generated per-run output folders (gitignored)
├── src/
│   └── proteinoid_complexity/
│       ├── graph_builders.py # Delaunay triangulation, edge-list ingestion
│       ├── metrics.py        # res_eff, p_short, l_edge (Algorithm 1)
│       ├── depercolation.py  # D(G, p) and edge-removal (Algorithm 2)
│       ├── visualization.py  # PNG rendering of graphs
│       └── io/
│           ├── excel.py      # xlsx sheet loading
│           └── report.py     # CSV + HTML writers
├── scripts/
│   ├── run_empirical.py                       # main empirical pipeline
│   ├── run_empirical_depercolation_sweep.py   # Algorithm 3 on empirical graphs
│   ├── analyze_deperc_midpoints.py            # sigmoid fits + midpoint scaling
│   ├── run_scaled_up.py                       # random Delaunay graphs, N trials
│   ├── run_random_sweep.py                    # p-sweep on random graphs
│   └── demo_delaunay.py                       # minimal Delaunay demo
├── tests/
│   └── test_baseline.py      # regression tests locking paper values to 1e-9
├── pyproject.toml
└── README.md
```

The `src/` package contains the reusable computational core. The `scripts/`
folder contains thin entry points that each script imports from `src/` — no
metric logic lives in `scripts/`. If you want to compute metrics on your own
data, import from `proteinoid_complexity` directly rather than editing scripts.

## What each script produces

| Script | Output |
|---|---|
| `run_empirical.py` | Per-sheet metrics CSV, HTML report with embedded graphs, PNGs |
| `run_empirical_depercolation_sweep.py` | Raw sweep CSV, per-(sheet, p) summary CSV, per-sheet curves, all-sheet overlay, node-count-coloured overlay |
| `analyze_deperc_midpoints.py` | Sigmoid fits per sheet, midpoint-vs-nodes plot with log-linear trend |
| `run_scaled_up.py` | Random-graph pipeline: metrics CSV, HTML report, PNGs |
| `run_random_sweep.py` | p-sweep on random Delaunay graphs: CSV + 2×2 regplot grid |
| `demo_delaunay.py` | Minimal 10-point Delaunay demo (smoke test) |

## Reproducibility

All stochastic operations (edge removal, random point generation) are seeded via
`config/default.yaml`. The default seed is 42. To reproduce a specific published
result exactly, use the `run_config.yaml` snapshot saved inside that result's
output folder — it captures every parameter used for that run.

The three deterministic metrics reported in the paper's Fig. 6 (average shortest
path, average edge length, total effective resistance) are locked into
`tests/test_baseline.py` at 1e-9 tolerance. Any refactor that changes those
values will fail `pytest`.

## Configuration

Edit `config/default.yaml` to change:

- Which xlsx file to read and which sheets to analyse
- Depercolation edge-removal fraction and mode (empirical graph, fresh Delaunay
  of the same nodes, or both)
- Sweep parameters: p range, step count, realisations per step
- Random-graph parameters: node count range, scale
- Random seed

Pass a different config file with `--config path/to/other.yaml` on any script.

## Requirements

Python 3.11 or later. Dependencies are declared in `pyproject.toml` and pulled in
by `pip install -e .`. Development extras (pytest) are pulled in by
`pip install -e ".[dev]"`.

Tested on Python 3.14.2 (Windows), but any 3.11+ should work.

## Citing this work

If you use this code, please cite the paper:

```
@article{sharma2026proteinoid,
  title={Morphological and functional complexity of fluidic proteinoid microspheres},
  author={Sharma, Saksham and Mahmud, Adnan and Adamatzky, Andrew and
          Mougkogiannis, Panagiotis and Tarabella, Giuseppe},
  year={2026},
  note={Under revision at Cognitive Computation}
}
```

## Contact

Corresponding author: Saksham Sharma (ss2531@cam.ac.uk).
Code maintainer: Adnan Mahmud.
Issues and pull requests welcome via GitHub.

## License

MIT. See `LICENSE` file.
