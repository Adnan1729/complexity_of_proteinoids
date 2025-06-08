# Morphological and Functional Complexity of Fluidic Proteinoid Microspheres

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://img.shields.io/badge/DOI-pending-orange.svg)]()

## Overview

This repository contains the computational framework for analyzing the morphological and functional complexity of proteinoid microsphere ensembles, as described in the paper:

**"Morphological and functional complexity of fluidic proteinoid microspheres"**  
*Saksham Sharma, Adnan Mahmud, Giuseppe Tarabella, Panagiotis Mougoyannis, Andrew Adamatzky*

Proteinoids are fluidic gels made from poly(amino acids) based polymers that exhibit oscillatory electrical activity and show potential for analog computing applications. This codebase provides tools to quantify complexity metrics that characterize the computational and design complexity of proteinoid networks as potential chemical hardware for analog computing.

## Key Features

- **Graph-based Analysis**: Convert proteinoid microsphere images to undirected graphs using Delaunay triangulation
- **Complexity Metrics**: Calculate 9 key complexity metrics including average degrees, resistance, percolation threshold
- **Protocol Comparison**: Compare two different preparation protocols for proteinoid synthesis
- **Percolation Analysis**: Simulate edge removal to study network robustness and connectivity
- **Automated Reporting**: Generate comprehensive Word documents with analysis results and visualizations

## Research Context

This work addresses the fundamental question of treating gels, microspheres, and fluidic systems as information-theoretic entities rather than purely continuum mechanical systems. The approach aligns with recent perspectives on fluid programmability and Turing-completeness, offering insights for:

- Analog computing hardware design
- Neuromorphic device development  
- Reservoir computing implementations
- Boolean circuit mining in biological systems

## Installation

### Prerequisites

```bash
python >= 3.8
```

### Required Dependencies

```bash
pip install pandas networkx numpy matplotlib scipy python-docx seaborn
```

### Complete Installation

```bash
git clone https://github.com/username/proteinoid-complexity-analysis.git
cd proteinoid-complexity-analysis
pip install -r requirements.txt
```

## Usage

### 1. Empirical Graph Analysis (From Excel Data)

Analyze proteinoid networks from experimental coordinate data:

```python
from proteinoid_analysis import empirical_analysis

# Process multiple sheets from Excel file
filename = 'path/to/img_nodes_data.xlsx'
sheet_names = ['img1', 'img2', 'img3', 'img4', 'saksham_img1', 'saksham_img2']

# Run complete analysis pipeline
empirical_analysis.process_sheets(filename, sheet_names)
```

### 2. Simulated Network Analysis

Generate and analyze synthetic proteinoid networks:

```python
from proteinoid_analysis import simulation

# Run Monte Carlo simulation with edge removal
num_iterations = 19
p_values = np.linspace(0.5, 0.9, 10)  # Edge removal probabilities

simulation.run_simulation(num_iterations, p_values)
```

### 3. Individual Graph Analysis

Process single proteinoid network:

```python
from proteinoid_analysis import graph_metrics

# Create graph from coordinates
points = random_points(90, 100, scale=1200)
G, pos = delaunay_triangulation(points)

# Calculate complexity metrics
metrics = graph_metrics.calculate_all_metrics(G, pos)
print(f"Average degree: {metrics['avg_degree']}")
print(f"Effective resistance: {metrics['total_resistance']}")
print(f"Percolation threshold: {metrics['perc_threshold']}")
```

## Complexity Metrics

The framework calculates nine key complexity metrics:

### Primary Metrics
- **Total edges (e)** and **Total nodes (v)**: Basic graph structure
- **Average degree (Deg_av)**: Connectivity measure
- **Maximum independent cycles (u)**: Topological complexity
- **Graph diameter (D_G)**: Network span in nodes

### Information Transmission Metrics  
- **Average connections per node (Conn_av)**: Information flow capacity
- **Average shortest path (p_short)**: Communication efficiency
- **Average edge length (l_edge)**: Physical connection distances

### Advanced Metrics
- **Effective resistance (res_eff)**: Network robustness
- **Percolation threshold (perc_t)**: Critical connectivity point

## File Structure

```
proteinoid-complexity-analysis/
├── src/
│   ├── proteinoid_analysis/
│   │   ├── __init__.py
│   │   ├── empirical_analysis.py      # Excel data processing
│   │   ├── simulation.py              # Monte Carlo simulations  
│   │   ├── graph_metrics.py           # Complexity calculations
│   │   ├── delaunay_utils.py          # Triangulation utilities
│   │   └── visualization.py           # Plotting functions
├── data/
│   ├── sample_data.xlsx               # Example experimental data
│   └── protocol_comparison/           # Protocol-specific datasets
├── results/
│   ├── graphs/                        # Generated network visualizations
│   ├── reports/                       # Auto-generated Word documents
│   └── analysis_plots/                # Complexity metric plots
├── tests/
│   └── test_metrics.py                # Unit tests
├── requirements.txt
├── setup.py
└── README.md
```

## Experimental Protocols

The codebase supports analysis of proteinoids prepared using two protocols:

### Protocol 1 (High-temperature synthesis)
- **Temperature**: 290°C heating
- **Amino acids**: Equimolar L-Glutamic acid, L-asparagine, L-phenylalanine  
- **Particle size**: ~100 nanometers
- **Characteristics**: Higher complexity, density, resistance

### Protocol 2 (Low-temperature synthesis)  
- **Temperature**: 70°C heating
- **Amino acids**: 1:1 aspartic acid and L-arginine
- **Particle size**: ~100 micrometers  
- **Characteristics**: Lower resistance, easier information flow

## Key Research Findings

- **Protocol 1** produces more complex, dense networks with higher information transmission resistance
- **Protocol 2** generates networks with easier information flow and lower power consumption
- Optimal analog computing hardware likely requires protocols between these extremes
- Percolation thresholds distinguish protocol effectiveness for parallel computing applications

## Citation

If you use this code in your research, please cite:

```bibtex
@article{sharma2025proteinoid,
  title={Morphological and functional complexity of fluidic proteinoid microspheres},
  author={Sharma, Saksham and Mahmud, Adnan and Tarabella, Giuseppe and Mougoyannis, Panagiotis and Adamatzky, Andrew},
  journal={[Computers & Fluids]},
  year={2025},
  note={Submitted}
}
```

## Contributing

We welcome contributions to improve the analysis framework:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new complexity metric'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Saksham Sharma** - Cambridge Centre for Physical Biology, Unconventional Computing Laboratory UWE Bristol
- **Adnan Mahmud** - Department of Chemical Engineering, Cambridge University  
- **Giuseppe Tarabella** - Institute of Materials for Electronic and Magnetism, National Research Council (IMEM-CNR)
- **Panagiotis Mougoyannis** - Unconventional Computing Laboratory, UWE Bristol
- **Andrew Adamatzky** - Unconventional Computing Laboratory, UWE Bristol

## Acknowledgments

- Cambridge Centre for Physical Biology
- Unconventional Computing Laboratory, UWE Bristol
- National Research Council (IMEM-CNR), Italy
- NetworkX and SciPy communities for computational tools

## Contact

For questions about the code or methodology:
- Adnan Mahmud: mam255@cantab.ac.uk

---

*This work contributes to the emerging field of analog computing with biological materials and information-theoretic approaches to fluid dynamics.*
