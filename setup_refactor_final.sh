#!/bin/bash
# setup_refactor_final.sh
set -e

echo "Sweeping stray files at root..."
mkdir -p arkive
shopt -s nullglob
for f in *.png *.docx; do
    mv "$f" arkive/
    echo "  moved $f"
done

echo ""
echo "Tidying data/ folder..."
# Archive the old baseline docx so data/outputs starts empty
if [ -e "data/output/graph_analysis_results.docx" ]; then
    mv data/output/graph_analysis_results.docx arkive/baseline_graph_analysis_results.docx
    echo "  archived old docx as arkive/baseline_graph_analysis_results.docx"
fi

# Rename output -> outputs (plural)
if [ -d "data/output" ] && [ ! -d "data/outputs" ]; then
    mv data/output data/outputs
    echo "  renamed data/output -> data/outputs"
fi

echo ""
echo "Creating new project structure..."

touch pyproject.toml
[ ! -e README.md ] && touch README.md
[ ! -e .gitignore ] && touch .gitignore

mkdir -p config
touch config/default.yaml

mkdir -p src/proteinoid_complexity/io
touch src/proteinoid_complexity/__init__.py
touch src/proteinoid_complexity/graph_builders.py
touch src/proteinoid_complexity/metrics.py
touch src/proteinoid_complexity/percolation.py
touch src/proteinoid_complexity/visualization.py
touch src/proteinoid_complexity/io/__init__.py
touch src/proteinoid_complexity/io/excel.py
touch src/proteinoid_complexity/io/report.py

mkdir -p scripts
touch scripts/run_empirical.py
touch scripts/run_random_sweep.py
touch scripts/run_scaled_up.py
touch scripts/demo_delaunay.py

mkdir -p tests
touch tests/__init__.py
touch tests/test_baseline.py

echo ""
echo "Done. Structure:"
echo ""
find . -maxdepth 3 -not -path './arkive*' -not -path './.git*' -not -path './venv*' -not -path './.venv*' | sort