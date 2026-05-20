# workload_code/simulation_engine.py

from __future__ import annotations  # Allow forward references in type hints (common in Py3.7+)
from typing import Any, Dict        # For type annotations of function parameters/dictionaries
from pathlib import Path            # Cross-platform path handling (avoid hard-coded strings)
import logging                      # Logging (integrated with entry script, stored in results/logs/)

# Import three types of visualization functions (this module only orchestrates, no computation)
from .visualization import (
    plot_efficiency_vs_workload,          # Generate Figure 3: Efficiency–Workload curve with zones
    plot_beta_variation_comparison,       # Generate Figure 10: β ± Δβ comparison curves
    generate_beta_variation_time_series,  # Generate two time-series plots: Efficiency/Stress vs Time (β ± Δβ)
)

# Module-level logger (named workload_code.simulation_engine)
logger = logging.getLogger(__name__)


def _get_output_dir() -> Path:
    """
    Unified entry for figure output directory.
    - Locate the project root (parent of workload_code)
    - Create results/figures/ under root if it does not exist
    - Return the Path object of that directory for later filename concatenation

    Note: If you prefer saving outside the project directory, 
    you can change the return to:
      return Path("../figures").resolve()
    """
    # __file__ -> current file; parents[1] -> project root (two levels up)
    project_root = Path(__file__).resolve().parents[1]
    # Standard output directory: <project_root>/results/figures
    out_dir = project_root / "results" / "figures"
    # Ensure the directory exists (parents=True allows recursive creation)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _check_required(params: Dict[str, Any], keys: tuple[str, ...]) -> None:
    """
    Check that required parameters are present:
    - params: external parameter dictionary (usually from user input/default config)
    - keys: tuple of required parameter names
    - If any required key is missing, raise KeyError to expose configuration issues early
    """
    # Find missing keys
    missing = [k for k in keys if k not in params]
    if missing:
        # Raise error with clear message about which parameters are missing
        raise KeyError(f"Missing required parameters: {missing}")


def run_simulation(**params: Any) -> None:
    """
    Main simulation orchestration function: generates three types of figures
      1) Figure 3: Efficiency–Workload (zones + ΔW)
      2) Figure 10: β ± Δβ comparison curves
      3) Two time-series plots: Efficiency/Stress vs Time (β ± Δβ), marking first completion time t*

    Required parameters:
      beta, sigma_max, epsilon_max, total_time, delta_tau, total_workload

    Notes:
      - This function does not perform numerical computation directly.
        All computation is handled in the analysis layer and called by visualization.
      - Responsibilities of this function: validate parameters, manage output directories,
        call plotting functions, print user-friendly info, and log events.
    """
    # Enforce required keys in params
    required = ("beta", "sigma_max", "epsilon_max", "total_time", "delta_tau", "total_workload")
    _check_required(params, required)

    # Log simulation parameters (for reproducibility and debugging)
    logger.info("[Simulation Engine] start with params: %s", params)

    # Get unified output directory (results/figures/)
    out_dir = _get_output_dir()

    # ---------- Figure 3 ----------
    # Compose filename for Figure 3, include β value for differentiation
    fig3_path = out_dir / f"figure3_efficiency_vs_workload_beta_{params['beta']:.1f}.png"
    # Call plotting function (computation handled internally)
    plot_efficiency_vs_workload(
        beta=params["beta"],
        sigma_max=params["sigma_max"],
        epsilon_max=params["epsilon_max"],
        output_path=fig3_path,
        show_plot=True,  # Display window as well (set False if saving only)
    )
    # Log + console feedback
    logger.info("Figure 3 saved: %s", fig3_path)
    print(f"✅ Human vs Ideal Efficiency comparison figure generated: {fig3_path}")

    # ---------- Figure 10 ----------
    # Compose filename for Figure 10, include base β value
    fig10_path = out_dir / f"figure10_beta_variation_beta={params['beta']:.1f}.png"
    # Call plotting function for β ± Δβ comparison
    plot_beta_variation_comparison(
        base_beta=params["beta"],
        sigma_max=params["sigma_max"],
        epsilon_max=params["epsilon_max"],
        output_path=fig10_path,
        show_plot=True,
    )
    logger.info("Figure 10 saved: %s", fig10_path)
    print(f"✅ Comparison of β ± delta_beta efficiency curves with ideal line generated: {fig10_path}")

    # ---------- Time-series plots (β ± Δβ) ----------
    # Generate two time-series plots (Efficiency/Stress), internally calls batch simulation
    ts_paths = generate_beta_variation_time_series(
        base_beta=params["beta"],                # Central β
        total_workload=params["total_workload"], # Total workload (used for completion check)
        total_time=params["total_time"],         # Total time steps
        delta_tau=params["delta_tau"],           # Time step size
        sigma_max=params["sigma_max"],           # Stress upper limit
        epsilon_max=params["epsilon_max"],       # Efficiency upper limit
        output_dir=out_dir,                      # Output directory for both plots
        delta_beta=0.3,                          # Perturbation size (consistent with Fig. 10)
        dpi=300,                                 # Image resolution
        show_plot=True,                          # Whether to display in window
        # Example for fixed y-axis range (uncomment if needed):
        # ylim_eff=(0, params['epsilon_max'] * 1.1),
        # ylim_stress=(0, params['sigma_max'] + 10),
        title_stub=None,                         # None -> auto-generate "(β=..., WT=...)"
    )
    # Log time-series plot paths
    logger.info("Time-series figures saved: %s", ts_paths)
    print(f"✅ Work Efficiency vs Time (β ± 0.3) (a) generated: {ts_paths['efficiency_png']}")
    print(f"✅ Mental Stress vs Time (β ± 0.3) (b) generated: {ts_paths['stress_png']}")
