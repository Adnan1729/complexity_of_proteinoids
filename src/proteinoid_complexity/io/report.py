"""
Report writers.

Two output formats are produced per run:
    - metrics.csv: one row per sheet, all metrics as columns.
      This is the machine-readable output for downstream analysis.
    - report.html: a self-contained HTML file with embedded PNG figures.
      This is the human-readable output for sharing and eyeballing.

The old .docx output has been dropped. If needed later, add a docx writer here.
"""

from __future__ import annotations

import base64
import csv
from pathlib import Path

from jinja2 import Template


HTML_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{{ title }}</title>
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           max-width: 900px; margin: 2em auto; padding: 0 1em; color: #222; }
    h1 { border-bottom: 2px solid #333; padding-bottom: 0.3em; }
    h2 { margin-top: 2em; color: #444; }
    table { border-collapse: collapse; margin: 1em 0; }
    th, td { padding: 0.4em 0.8em; border: 1px solid #ccc; text-align: right; }
    th { background: #f0f0f0; text-align: left; }
    td:first-child { text-align: left; font-weight: 600; }
    img { max-width: 100%; height: auto; border: 1px solid #ddd; margin: 0.5em 0; }
    .meta { color: #666; font-size: 0.9em; }
</style>
</head>
<body>
<h1>{{ title }}</h1>
<p class="meta">Generated: {{ timestamp }}<br>
Config: {{ config_summary }}</p>

<h2>Summary</h2>
<table>
<tr>
    <th>Sheet</th>
    <th>Nodes</th>
    <th>Edges</th>
    <th>Avg shortest path</th>
    <th>Avg edge length</th>
    <th>Total eff. resistance</th>
    {% if show_deperc_empirical %}<th>Deperc. (empirical)</th>{% endif %}
    {% if show_deperc_fresh %}<th>Deperc. (fresh Delaunay)</th>{% endif %}
</tr>
{% for row in rows %}
<tr>
    <td>{{ row.sheet }}</td>
    <td>{{ row.num_nodes }}</td>
    <td>{{ row.num_edges }}</td>
    <td>{{ "%.4f"|format(row.avg_shortest_path) }}</td>
    <td>{{ "%.4f"|format(row.avg_edge_length) }}</td>
    <td>{{ "%.4f"|format(row.total_effective_resistance) }}</td>
    {% if show_deperc_empirical %}<td>{{ "%.4f"|format(row.deperc_empirical) if row.deperc_empirical is not none else "-" }}</td>{% endif %}
    {% if show_deperc_fresh %}<td>{{ "%.4f"|format(row.deperc_fresh_delaunay) if row.deperc_fresh_delaunay is not none else "-" }}</td>{% endif %}
</tr>
{% endfor %}
</table>

{% for row in rows %}
<h2>{{ row.sheet }}</h2>
<img src="data:image/png;base64,{{ row.image_b64 }}" alt="Graph of {{ row.sheet }}">
{% endfor %}

</body>
</html>
""")


CSV_COLUMNS = [
    "sheet",
    "num_nodes",
    "num_edges",
    "avg_shortest_path",
    "avg_edge_length",
    "total_effective_resistance",
    "deperc_empirical",
    "deperc_fresh_delaunay",
]


def write_csv(rows: list[dict], output_path: str | Path) -> Path:
    """
    Write one row per sheet to a CSV file.

    Missing keys are written as empty strings.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CSV_COLUMNS})

    return output_path


def write_html(
    rows: list[dict],
    figure_paths: dict[str, Path],
    output_path: str | Path,
    title: str,
    timestamp: str,
    config_summary: str,
    show_deperc_empirical: bool,
    show_deperc_fresh: bool,
) -> Path:
    """
    Write a self-contained HTML report with PNGs embedded as base64.

    Parameters
    ----------
    rows : list of dicts
        One dict per sheet, containing all the metric fields.
    figure_paths : dict
        Maps sheet name to the PNG path for that sheet's graph.
    output_path : str or Path
        Where to write the HTML.
    title, timestamp, config_summary : str
        Metadata rendered in the report header.
    show_deperc_empirical, show_deperc_fresh : bool
        Whether to include the corresponding depercolation columns in the table.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    enriched_rows = []
    for row in rows:
        image_path = figure_paths.get(row["sheet"])
        if image_path and Path(image_path).exists():
            image_b64 = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        else:
            image_b64 = ""
        enriched_rows.append({**row, "image_b64": image_b64})

    html = HTML_TEMPLATE.render(
        title=title,
        timestamp=timestamp,
        config_summary=config_summary,
        rows=enriched_rows,
        show_deperc_empirical=show_deperc_empirical,
        show_deperc_fresh=show_deperc_fresh,
    )
    output_path.write_text(html, encoding="utf-8")
    return output_path