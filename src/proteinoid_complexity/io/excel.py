"""
Excel I/O for the empirical pipeline.

The raw data is an xlsx file with one sheet per proteinoid image. Each sheet
has columns x1, y1, x2, y2 defining the edges of the graph extracted from
the corresponding SEM or optical micrograph.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd

from ..graph_builders import build_graph_from_edge_list


REQUIRED_COLUMNS = ("x1", "y1", "x2", "y2")


def load_sheet_as_graph(xlsx_path: str | Path, sheet_name: str) -> nx.Graph:
    """
    Load a single sheet from the input xlsx and return it as a graph.

    Parameters
    ----------
    xlsx_path : str or Path
        Path to the input xlsx file.
    sheet_name : str
        Name of the sheet to load.

    Returns
    -------
    networkx.Graph
    """
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
    _validate_columns(df, sheet_name)

    edge_rows = (
        (row["x1"], row["y1"], row["x2"], row["y2"])
        for _, row in df.iterrows()
    )
    return build_graph_from_edge_list(edge_rows)


def _validate_columns(df: pd.DataFrame, sheet_name: str) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Sheet '{sheet_name}' is missing required columns: {missing}. "
            f"Found: {list(df.columns)}"
        )