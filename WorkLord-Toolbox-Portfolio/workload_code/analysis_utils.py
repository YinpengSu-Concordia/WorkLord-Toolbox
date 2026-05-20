# workload_code/analysis_utils.py

# Import common type annotations from typing for readability and static type checking
from typing import List, Dict, Any, Tuple, Optional

# Import numpy for numerical computations (vector/array operations, interpolation, cumulative sums, etc.)
import numpy as np

# Import model formulas from formulas_and_variables module in the same directory
from .formulas_and_variables import (
    efficiency_from_workload,        # Given workload W and parameters, compute human efficiency ε(W)
    ideal_efficiency,                # Ideal efficiency function (baseline/ideal line for comparison)
    dynamic_subjective_workload,     # Dynamic subjective workload model (depends on time & history)
    simplified_stress_effort_model,  # Simplified stress–effort relationship model σ(W, β)
)

# __all__ defines which symbols are exported when using "from ... import *"
__all__ = [
    "find_intersections",
    "compute_efficiency_curves",
    "compute_beta_variation_curves",
    "simulate_time_series_single_beta",
    "simulate_time_series_for_betas",
]

# ------------------------------
# 1) More robust intersection search (parameterized)
# ------------------------------
def find_intersections(
    W_range: np.ndarray,      # Workload x-axis sample points (e.g., np.linspace(...))
    beta: float,              # Model parameter β (individual differences/sensitivity)
    sigma_max: float,         # Stress limit σ_max (for clipping/constraints)
    epsilon_max: float,       # Efficiency limit ε_max (upper bound for efficiency function)
    *,
    threshold: float = 1.0,   # Tolerance in y-axis for intersection check |eff - ideal| < threshold
    ignore_below: float = 5.0,# Ignore pseudo-intersections at very low workload values near 0
) -> List[float]:
    """
    Find intersections between human efficiency function and the ideal efficiency line (x-coordinates),
    used for marking Capacity zone boundaries.

    Parameters
    ----------
    W_range : np.ndarray
        Workload sampling points (x-axis).
    beta, sigma_max, epsilon_max : float
        Model parameters.
    threshold : float
        Absolute tolerance for y-value difference between two curves.
    ignore_below : float
        Ignore intersections with workload < this value (to avoid false intersections near 0).

    Returns
    -------
    List[float]
        [W1, W2] two intersection x-coordinates; if none found, return [].
    """
    eff = np.array([efficiency_from_workload(w, beta, sigma_max, epsilon_max) for w in W_range])
    ideal = np.array([ideal_efficiency(w) for w in W_range])
    diff = np.abs(eff - ideal)

    close_idx = np.where(diff < threshold)[0]
    valid_idx = [i for i in close_idx if W_range[i] >= ignore_below]

    if len(valid_idx) >= 2:
        return [float(W_range[valid_idx[0]]), float(W_range[valid_idx[-1]])]
    return []


# ------------------------------
# 2) Curve data preparation (compute only, no plotting)
# ------------------------------
def compute_efficiency_curves(
    beta: float,                 # β
    sigma_max: float,            # σ_max
    epsilon_max: float,          # ε_max
    n_points: int = 300,         # Number of sampling points (x-axis resolution)
) -> Dict[str, Any]:
    """
    Prepare data for Figure 3 (compute only, no plotting).
    Returns a dictionary with keys:
      - 'W_range': np.ndarray
      - 'eff': np.ndarray
      - 'ideal': np.ndarray
      - 'peak_eff': float
    """
    W_range = np.linspace(0, beta * sigma_max, n_points)
    eff = np.array([efficiency_from_workload(w, beta, sigma_max, epsilon_max) for w in W_range])
    ideal = np.array([ideal_efficiency(w) for w in W_range])
    peak_eff = float(np.max(eff))
    return {"W_range": W_range, "eff": eff, "ideal": ideal, "peak_eff": peak_eff}


def compute_beta_variation_curves(
    base_beta: float,               # Base β (central curve)
    sigma_max: float,               # σ_max
    epsilon_max: float,             # ε_max
    *,
    delta_beta: float = 0.3,        # Symmetric perturbation for β (±delta_beta)
    n_points: int = 500,            # Number of sampling points (higher resolution)
    beta_bounds: Tuple[float, float] = (0.1, 3.0),  # Global bounds for β values
) -> Dict[str, Any]:
    """
    Prepare curve data for multi-β comparison (compute only, no plotting).
    Returns a dictionary with keys:
      - 'beta_list': List[float]
      - 'W_range': np.ndarray
      - 'curves': Dict[beta, np.ndarray]  efficiency curve for each β
      - 'ideal': np.ndarray
    """
    min_b, max_b = beta_bounds
    beta_low = max(base_beta - delta_beta, min_b)
    beta_high = min(base_beta + delta_beta, max_b)
    beta_list = sorted({beta_low, base_beta, beta_high})

    W_max = max(beta_list) * sigma_max
    W_range = np.linspace(0, W_max, n_points)

    curves: Dict[float, np.ndarray] = {}
    for b in beta_list:
        curves[b] = np.array([efficiency_from_workload(w, b, sigma_max, epsilon_max) for w in W_range])

    ideal = np.array([ideal_efficiency(w) for w in W_range])
    return {"beta_list": beta_list, "W_range": W_range, "curves": curves, "ideal": ideal}


# ------------------------------
# 3) Time-series simulation (compute only, no plotting)
# ------------------------------
def simulate_time_series_single_beta(
    beta: float,                   # β
    total_workload: float,         # Total workload (cumulative efficiency * Δτ reaching this means completion)
    total_time: int,               # Total time steps (discrete time: 0,1,...,total_time-1)
    delta_tau: float,              # Time step width Δτ (must match the time unit of time_steps)
    sigma_max: float,              # σ_max (stress limit)
    epsilon_max: float,            # ε_max (efficiency limit)
) -> Dict[str, Any]:
    """
    Run time-stepped simulation for a single β.
    Returns:
      - 'time_steps': np.ndarray[int]
      - 'efficiency_series': np.ndarray[float]
      - 'stress_series': np.ndarray[float]
      - 'cumulative_done': np.ndarray[float]
      - 'completed': bool
      - 't_complete': Optional[int]

    Notes:
      - Units of time_steps and delta_tau must be consistent, otherwise cumulative results will be distorted.
      - total_workload is the total task demand (aligned with units of ε output/time).
    """
    if total_time <= 0:
        raise ValueError("total_time must be > 0")
    if delta_tau <= 0:
        raise ValueError("delta_tau must be > 0")
    if sigma_max <= 0 or epsilon_max <= 0:
        raise ValueError("sigma_max and epsilon_max must be > 0")

    time_steps = np.arange(0, total_time, 1)
    efficiency_series: List[float] = []
    stress_series: List[float] = []
    epsilon_history: List[float] = []

    for t in time_steps:
        W_t = dynamic_subjective_workload(
            t_index=t,
            total_time=total_time,
            total_workload=total_workload,
            epsilon_series=epsilon_history,
            delta_tau=delta_tau,
        )
        eps_t = efficiency_from_workload(W_t, beta, sigma_max, epsilon_max)
        efficiency_series.append(eps_t)
        epsilon_history.append(eps_t)

        sigma_t = min(simplified_stress_effort_model(W_t, beta), sigma_max)
        stress_series.append(sigma_t)

    efficiency_series = np.asarray(efficiency_series, dtype=float)
    stress_series = np.asarray(stress_series, dtype=float)
    cumulative_done = np.cumsum(efficiency_series) * float(delta_tau)

    completed = bool(np.any(cumulative_done >= total_workload))
    t_complete: Optional[int] = int(np.argmax(cumulative_done >= total_workload)) if completed else None

    return {
        "time_steps": time_steps,
        "efficiency_series": efficiency_series,
        "stress_series": stress_series,
        "cumulative_done": cumulative_done,
        "completed": completed,
        "t_complete": t_complete,
    }


def simulate_time_series_for_betas(
    beta_list: List[float],    # Multiple β values (may contain duplicates/unsorted)
    total_workload: float,     # Total workload
    total_time: int,           # Total time steps
    delta_tau: float,          # Time step Δτ
    sigma_max: float,          # σ_max
    epsilon_max: float,        # ε_max
) -> Dict[str, Any]:
    """
    Run batch simulation for a set of β values, return time-series results and completion status.
    Returns:
      - 'time_steps': np.ndarray[int]
      - 'results': Dict[beta, {series...}]
    """
    unique_betas = sorted(set(beta_list))
    results_per_beta: Dict[float, Dict[str, Any]] = {}
    time_steps_ref = None

    for beta in unique_betas:
        res = simulate_time_series_single_beta(
            beta=beta,
            total_workload=total_workload,
            total_time=total_time,
            delta_tau=delta_tau,
            sigma_max=sigma_max,
            epsilon_max=epsilon_max,
        )
        results_per_beta[beta] = res
        if time_steps_ref is None:
            time_steps_ref = res["time_steps"]

    return {
        "time_steps": time_steps_ref,
        "results": results_per_beta,  # { beta: {series...} }
    }
