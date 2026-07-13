"""
Baseline regression tests.

These lock in the numerical outputs from the original Emperical_Graph_Analysis.py
run against data/raw/img_nodes_2.xlsx, as reported in the paper preprint
(Sharma et al., 2026, Fig. 6).

Three metrics are checked exactly:
    - average shortest path
    - average edge length
    - total effective resistance

These are deterministic given the input graph — no randomness involved.

Percolation threshold is NOT checked here because it involves random edge
removal. It is verified separately in a stochastic test with a fixed seed.

If any of these values change, the refactor has introduced a regression.
Do not update the expected values without a written justification.
"""

import pytest

# Expected values from the paper preprint, verified against a docx run
# on the original codebase on 2026-07-04.
BASELINE = {
    "img1": {
        "avg_shortest_path": 676.304921882149,
        "avg_edge_length": 70.79855828904704,
        "total_effective_resistance": 189.01310211387613,
    },
    "img2": {
        "avg_shortest_path": 721.1112142231545,
        "avg_edge_length": 185.93778872738292,
        "total_effective_resistance": 4.554066166899909,
    },
    "img3": {
        "avg_shortest_path": 655.7907377956739,
        "avg_edge_length": 222.16096482477937,
        "total_effective_resistance": 1.7331557888643914,
    },
    "img4": {
        "avg_shortest_path": 628.8673476784811,
        "avg_edge_length": 121.3023926605208,
        "total_effective_resistance": 21.942143440295045,
    },
    "saksham_img1": {
        "avg_shortest_path": 277.3245844435843,
        "avg_edge_length": 176.22292534010515,
        "total_effective_resistance": 0.25511787529488167,
    },
    "saksham_img2": {
        "avg_shortest_path": 534.4428303482428,
        "avg_edge_length": 337.22112048921434,
        "total_effective_resistance": 0.21127080213552235,
    },
}

TOLERANCE = 1e-9  # absolute tolerance for float comparison


@pytest.fixture(scope="module")
def empirical_results():
    """
    Run the empirical pipeline once and cache the results for all tests.
    Skipped until the pipeline is implemented.
    """
    try:
        from proteinoid_complexity.io.excel import load_sheet_as_graph
        from proteinoid_complexity.metrics import compute_all_metrics
    except ImportError:
        pytest.skip("Pipeline modules not yet implemented.")

    from pathlib import Path
    xlsx_path = Path("data/raw/img_nodes_2.xlsx")
    if not xlsx_path.exists():
        pytest.skip(f"Baseline input not found at {xlsx_path}")

    results = {}
    for sheet in BASELINE.keys():
        graph = load_sheet_as_graph(xlsx_path, sheet)
        results[sheet] = compute_all_metrics(graph)
    return results


@pytest.mark.parametrize("sheet", list(BASELINE.keys()))
def test_avg_shortest_path(empirical_results, sheet):
    expected = BASELINE[sheet]["avg_shortest_path"]
    actual = empirical_results[sheet]["avg_shortest_path"]
    assert abs(actual - expected) < TOLERANCE, (
        f"{sheet}: expected {expected}, got {actual}, diff {abs(actual - expected)}"
    )


@pytest.mark.parametrize("sheet", list(BASELINE.keys()))
def test_avg_edge_length(empirical_results, sheet):
    expected = BASELINE[sheet]["avg_edge_length"]
    actual = empirical_results[sheet]["avg_edge_length"]
    assert abs(actual - expected) < TOLERANCE, (
        f"{sheet}: expected {expected}, got {actual}, diff {abs(actual - expected)}"
    )


@pytest.mark.parametrize("sheet", list(BASELINE.keys()))
def test_total_effective_resistance(empirical_results, sheet):
    expected = BASELINE[sheet]["total_effective_resistance"]
    actual = empirical_results[sheet]["total_effective_resistance"]
    assert abs(actual - expected) < TOLERANCE, (
        f"{sheet}: expected {expected}, got {actual}, diff {abs(actual - expected)}"
    )