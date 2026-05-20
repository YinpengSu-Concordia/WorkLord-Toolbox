# WorkLord Toolbox

**Portfolio version by Yinpeng Su**  
Research software prototype for workload modeling, capacity-zone simulation, and visualization.

## Overview

WorkLord Toolbox is a Python-based simulation and visualization toolkit for exploring the relationship among workload, perceived stress, mental capacity, effort, and work efficiency.

The project implements a parameter-controllable workflow that can generate workload-efficiency curves, beta-variation comparisons, and time-series simulations. It is intended as a research software portfolio project in human factors engineering, cognitive workload modeling, and human-autonomy teaming.

## What I built

This repository focuses on the software implementation and research-tooling layer:

- structured Python modules for formulas, analysis utilities, simulation orchestration, visualization, and user interaction;
- configurable simulation parameters;
- automatic figure generation;
- reproducible scripts for model replication and extension;
- documentation and presentation materials summarizing the replication workflow.

## Attribution

The original theoretical model and paper are attributed to:

> Mengting Zhao, Dongyu Qiu, and Yong Zeng, “How much workload is a ‘good’ workload for human beings to meet the deadline: human capacity zone and workload equilibrium,” *Journal of Engineering Design*.

This repository does **not** claim authorship of the original theory. My contribution is the Python implementation, engineering structure, replication workflow, visualization pipeline, and portfolio documentation.

## Project Structure

```text
WorkLord-Toolbox/
├── config/                 # Default simulation parameters
├── docs/                   # Project documentation and portfolio materials
├── environment/            # Detailed environment notes
├── reproduce_code/         # Figure-level replication scripts
├── results/figures/        # Example generated figures
├── scripts/                # Main entry point
├── workload_code/          # Core implementation modules
├── requirements.txt        # Python dependencies
├── CITATION.cff            # Citation metadata
├── LICENSE                 # Portfolio-use license notice
└── README.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YinpengSu-Concordia/WorkLord-Toolbox.git
cd WorkLord-Toolbox
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the toolbox

```bash
python scripts/main.py
```

The console will ask whether to use default parameters or custom parameters.

Generated figures will be saved under:

```text
results/figures/
```

## Main Features

- Workload-efficiency curve generation
- Capacity Zone / Fatigue Zone visualization
- Beta-variation comparison under different mental capacity assumptions
- Time-series simulation of efficiency and stress
- Modular code structure for further extension
- Lightweight dependency stack suitable for ordinary laptops

## Technical Stack

- Python 3.9–3.12
- NumPy
- Matplotlib
- Typing Extensions
- pathlib-based cross-platform file handling

## Portfolio Positioning

This project demonstrates my ability to:

- translate a mathematical research model into runnable software;
- organize research code into a maintainable Python package structure;
- create reproducible visual outputs;
- document assumptions, parameters, and model limitations;
- connect human factors theory with computational simulation.

## Suggested Future Extensions

- Add unit tests for formula-level validation;
- Add a command-line interface with named parameters;
- Add Jupyter notebooks for research demonstrations;
- Add empirical data calibration once workload or psychophysiological data become available;
- Extend the model toward adaptive workload allocation in human-autonomy teaming.
