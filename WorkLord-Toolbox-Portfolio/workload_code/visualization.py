# workload_code/visualization.py
"""
Visualization module (rendering and saving only, no numerical computation).
Depends on: workload_code.analysis_utils for data preparation and simulation functions.
"""

# —— Type hints —— #
from typing import Union, Optional, Dict, Any, List, Tuple
from pathlib import Path
import logging

# —— Scientific computation and plotting —— #
import numpy as np
import matplotlib.pyplot as plt

# —— Numerical computation is fully delegated to analysis_utils (this file does no calculations) —— #
from .analysis_utils import (
    compute_efficiency_curves,      # Compute curve data needed for Figure 3 (W, eff, ideal, peak)
    compute_beta_variation_curves,  # Compute data for multi-β comparison curves
    find_intersections,             # Find approximate intersections on given curve data
    simulate_time_series_for_betas, # Run time-series simulation for multiple β values (compute only, no plotting)
)
# —— For point annotations, need instantaneous value of the ideal line —— #
from .formulas_and_variables import ideal_efficiency  # ideal(W), used for labeling intersections

# —— Module-level logger (integrated with scripts/main.py logging config) —— #
logger = logging.getLogger(__name__)


# ------------------------------
# 1) Figure 3: Efficiency–Workload (plot only, no compute)
# ------------------------------
def plot_efficiency_vs_workload(
    beta: float,                         # β parameter
    sigma_max: float,                    # σ_max (stress limit)
    epsilon_max: float,                  # ε_max (efficiency limit)
    output_path: Union[str, Path],       # Output image file path
    *,
    threshold: float = 1.0,              # Intersection tolerance |eff-ideal| < threshold
    ignore_below: float = 5.0,           # Minimum W to ignore pseudo-intersections in low workload region
    show_plot: bool = True,              # Show window (True) or save only (False)
    dpi: int = 300,                      # Save resolution
    annotate: bool = True,               # Annotate zones and ΔW on the plot
) -> Dict[str, Any]:
    """
    Plot Figure 3: Human efficiency vs ideal efficiency curve for a given β,
    including three zones (Laid-back, Capacity, Fatigue).  
    Even if no intersections are found, draw a complete plot.

    Returns:
        dict: {
            'intersections': [(w_left, eps_left), (w_right, eps_right)] or [],
            'delta_w': float or None,
            'peak_efficiency': float,
            'output_path': Path
        }
    """
    # Normalize output path and ensure directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Compute data from analysis layer: W, eff, ideal, peak_eff
    data = compute_efficiency_curves(beta=beta, sigma_max=sigma_max, epsilon_max=epsilon_max, n_points=300)
    W_range: np.ndarray = data["W_range"]
    eff: np.ndarray = data["eff"]
    ideal: np.ndarray = data["ideal"]
    peak_eff: float = data["peak_eff"]

    # Find intersections (expecting 2; otherwise no zone split)
    points = find_intersections(
        W_range=W_range, beta=beta, sigma_max=sigma_max, epsilon_max=epsilon_max,
        threshold=threshold, ignore_below=ignore_below
    )
    has_int = (len(points) == 2)
    intersections: List[Tuple[float, float]] = []

    if has_int:
        x1, x2 = points
        intersections = [
            (x1, float(np.interp(x1, W_range, eff))),
            (x2, float(np.interp(x2, W_range, eff))),
        ]
    else:
        # Diagnose why no intersections were found
        diff = eff - ideal
        abs_diff = np.abs(diff)
        below_all = np.all(eff + threshold < ideal)
        above_all = np.all(eff - threshold > ideal)
        near_low_ignored = np.any((abs_diff < threshold) & (W_range < ignore_below))
        sign_flip = np.any(np.sign(diff[:-1]) * np.sign(diff[1:]) < 0)
        i_min = int(np.argmin(abs_diff))
        w_min = float(W_range[i_min])
        gap_min = float(abs_diff[i_min])

        msg_lines: List[str] = []
        msg_lines.append("⚠️ No two intersections found. Possible reasons and suggestions:")
        msg_lines.append(f"  • Minimum |ε-ideal| ≈ {gap_min:.3f} at W ≈ {w_min:.2f}.")
        if below_all:
            msg_lines.append("  • Human efficiency curve entirely below ideal line (ε(W) < ideal).")
            msg_lines.append("    Suggest: increase β or ε_max; lower threshold; or increase σ_max to extend W range (β·σ_max).")
        elif above_all:
            msg_lines.append("  • Human efficiency curve entirely above ideal line (ε(W) > ideal).")
            msg_lines.append("    Suggest: decrease β or ε_max; lower ignore_below; or increase threshold.")
        elif near_low_ignored:
            msg_lines.append(f"  • Near-intersection in low workload region (W<{ignore_below}), excluded by ignore_below.")
            msg_lines.append("    Suggest: reduce ignore_below (e.g., set to 0–1) or increase threshold.")
        elif sign_flip and gap_min > threshold:
            msg_lines.append("  • Geometric crossing trend exists but |ε-ideal| > threshold at all points.")
            msg_lines.append("    Suggest: increase threshold (e.g., 1.0 → 2.0), or use finer sampling (n_points).")
        else:
            msg_lines.append("  • No clear crossing observed within sample range.")
            msg_lines.append("    Suggestions: check parameter scales:")
            msg_lines.append("      - If β, ε_max too small: curve too low → increase β/ε_max;")
            msg_lines.append("      - If β, ε_max too large: curve too high → decrease β/ε_max;")
            msg_lines.append("      - If σ_max too small: β·σ_max too short → increase σ_max;")
            msg_lines.append("      - Or adjust threshold/ignore_below to relax intersection condition.")

        detail = "\n".join(msg_lines)
        print(detail)
        logger.warning(detail)

    # Plotting
    plt.figure(figsize=(9, 5))
    plt.plot(W_range, eff,   color='black', linewidth=5, label='Human workload–effort')
    plt.plot(W_range, ideal, color='green', linewidth=5, label='Ideal efficiency')

    label_y = peak_eff * 1.8

    if has_int:
        (x1, y1), (x2, y2) = intersections
        plt.axvspan(W_range[0], x1,        color='skyblue',   alpha=0.25, label='Laid-back Zone')
        plt.axvspan(x1, x2,                 color='lightgreen', alpha=0.30, label='Capacity Zone')
        plt.axvspan(x2, W_range[-1],        color='salmon',     alpha=0.25, label='Fatigue Zone')

        plt.scatter([x1, x2], [y1, y2], color='red', zorder=10)
        plt.axvline(x1, color='black', linestyle='--')
        plt.axvline(x2, color='black', linestyle='--')

        if annotate:
            plt.text((W_range[0] + x1)/2, label_y, 'Laid-back Zone', color='blue',  fontsize=12, ha='center')
            plt.text((x1 + x2)/2,         label_y, 'Capacity Zone',  color='green', fontsize=12, ha='center')
            plt.text((x2 + W_range[-1])/2,label_y, 'Fatigue Zone',   color='red',   fontsize=12, ha='center')

            delta_w = x2 - x1
            mid_x   = (x1 + x2) / 2
            mid_y   = peak_eff * 1.0
            plt.text(
                mid_x, mid_y, f"ΔW = {delta_w:.1f}",
                fontsize=10, color='black', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.5),
                clip_on=True
            )
    else:
        plt.axvspan(W_range[0], W_range[-1], color='lightgray', alpha=0.15, label='Unclassified Region')
        if annotate:
            plt.text(float(np.mean(W_range)), label_y, '⚠️ No intersection found',
                     color='gray', fontsize=12, ha='center')

    plt.title(f"Human vs Ideal Efficiency at β={beta:.1f}, σ_max={sigma_max:.1f}, ε_max={epsilon_max:.1f}", fontsize=14)
    plt.xlabel("Workload W(t)", fontsize=12)
    plt.ylabel("Work Efficiency ε(t)", fontsize=12)
    plt.ylim(0, peak_eff * 2.0)
    plt.grid(True, alpha=0.25)

    handles, labels = plt.gca().get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    plt.legend(uniq.values(), uniq.keys(), loc='best')
    plt.tight_layout()

    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.show() if show_plot else plt.close()

    return {
        "intersections": intersections if has_int else [],
        "delta_w": (intersections[1][0] - intersections[0][0]) if has_int else None,
        "peak_efficiency": peak_eff,
        "output_path": output_path,
    }


# ------------------------------
# 2) Figure 10: β ± Δβ Comparison (plot only, no compute)
# ------------------------------
def plot_beta_variation_comparison(
    base_beta: float,                  # Base β (central curve)
    sigma_max: float,                  # σ_max
    epsilon_max: float,                # ε_max
    output_path: Union[str, Path] = None,  # Output image path (None → default)
    title: Optional[str] = None,           # Custom title (None → default title)
    show_plot: bool = True,                # Show window
    *,
    delta_beta: float = 0.3,               # Perturbation for β (±delta_beta)
    threshold: float = 1.0,                # Intersection tolerance
    ignore_below: float = 5.0,             # Minimum W to ignore low-load pseudo-intersections
    dpi: int = 300,                        # Image resolution
    annotate: bool = True,                 # Annotate intersections and ΔW
) -> Dict[str, Any]:
    """
    Plot Figure 10: Compare β ± delta_beta efficiency curves with the ideal line,
    marking intersections and ΔW.

    Returns:
        dict: {
            'intersections_map': {beta: [w1, w2], ...},
            'output_path': Path
        }
    """
    pack = compute_beta_variation_curves(
        base_beta=base_beta,
        sigma_max=sigma_max,
        epsilon_max=epsilon_max,
        delta_beta=delta_beta,
        n_points=500,
    )
    beta_list: List[float] = pack["beta_list"]
    W_range: np.ndarray = pack["W_range"]
    curves: Dict[float, np.ndarray] = pack["curves"]
    ideal: np.ndarray = pack["ideal"]

    if len(beta_list) < 3:
        logger.warning("β ± Δβ exceeded bounds or was clipped (base=%.2f, Δβ=%.2f); "
                       "red/green/blue curves may be incomplete.", base_beta, delta_beta)

    # Fixed color map: low β → red, base β → green, high β → blue
    color_map = {min(beta_list): 'red', base_beta: 'green', max(beta_list): 'blue'}

    plt.figure(figsize=(10, 6))
    efficiency_max_all: List[float] = []
    intersections_map: Dict[float, List[float]] = {}

    def _diagnose_no_intersections_for_beta(
        b: float,
        W_range: np.ndarray,
        eff_curve: np.ndarray,
        ideal_curve: np.ndarray,
        threshold: float,
        ignore_below: float
    ) -> None:
        """
        Diagnostic messages when two intersections are not found for a given β.
        Prints to console and logs.
        """
        diff = eff_curve - ideal_curve
        abs_diff = np.abs(diff)
        below_all = np.all(eff_curve + threshold < ideal_curve)
        above_all = np.all(eff_curve - threshold > ideal_curve)
        near_low_ignored = np.any((abs_diff < threshold) & (W_range < ignore_below))
        sign_flip = np.any(np.sign(diff[:-1]) * np.sign(diff[1:]) < 0)
        i_min = int(np.argmin(abs_diff))
        w_min = float(W_range[i_min])
        gap_min = float(abs_diff[i_min])

        lines: List[str] = []
        lines.append(f"⚠️ β={b:.2f}: No two intersections found.")
        lines.append(f"  • min|ε-ideal| ≈ {gap_min:.3f}, at W ≈ {w_min:.2f}.")

        if below_all:
            lines.append("  • Entire curve below ideal line (ε(W) < ideal).")
            lines.append("    Suggest: increase β or ε_max; increase σ_max to extend W range (β·σ_max); or increase threshold.")
        elif above_all:
            lines.append("  • Entire curve above ideal line (ε(W) > ideal).")
            lines.append("    Suggest: decrease β or ε_max; lower ignore_below; or increase threshold.")
        elif near_low_ignored:
            lines.append(f"  • Near-intersection detected for W<{ignore_below}, excluded by ignore_below.")
            lines.append("    Suggest: lower ignore_below (e.g., 0–1), or increase threshold.")
        elif sign_flip and gap_min > threshold:
            lines.append("  • Geometric crossing trend exists but |ε-ideal| always > threshold.")
            lines.append("    Suggest: increase threshold (e.g., 1.0→2.0), or increase sampling resolution.")
        else:
            lines.append("  • No clear crossing observed in sample range.")
            lines.append("    Suggestions: check parameter scales:")
            lines.append("      - If β, ε_max too small: curve too low → increase β/ε_max;")
            lines.append("      - If β, ε_max too large: curve too high → decrease β/ε_max;")
            lines.append("      - If σ_max too small: β·σ_max too short → increase σ_max;")
            lines.append("      - Or adjust threshold/ignore_below.")

        detail = "\n".join(lines)
        print(detail)
        logger.warning(detail)

    # Plot efficiency curves for each β
    for b in beta_list:
        eff = curves[b]
        efficiency_max_all.append(float(np.max(eff)))
        plt.plot(
            W_range, eff,
            color=color_map.get(b, 'black'),
            linewidth=3,
            linestyle='-' if np.isclose(b, base_beta) else '--',
            label=f'β = {b:.1f}' + (' (Center)' if np.isclose(b, base_beta) else '')
        )

        pts = find_intersections(
            W_range=W_range, beta=b, sigma_max=sigma_max, epsilon_max=epsilon_max,
            threshold=threshold, ignore_below=ignore_below
        )
        if len(pts) == 2:
            intersections_map[b] = pts
            if annotate:
                for x in pts:
                    y = ideal_efficiency(x)
                    plt.scatter(x, y, color=color_map.get(b, 'black'), zorder=5)
                    plt.text(x, y + np.max(eff)*0.05, f'W={x:.1f}', ha='center', fontsize=8,
                             color=color_map.get(b, 'black'), clip_on=True)
        else:
            _diagnose_no_intersections_for_beta(b, W_range, eff, ideal, threshold, ignore_below)

    plt.plot(W_range, ideal, color='black', linewidth=2, label='Ideal Efficiency')

    if annotate and intersections_map:
        ymax = max(efficiency_max_all) * 1.25
        for b, pts in intersections_map.items():
            if len(pts) != 2:
                continue
            w1, w2 = pts
            delta_w = w2 - w1
            if np.isclose(b, min(beta_list)):
                x_pos = w1
            elif np.isclose(b, max(beta_list)):
                x_pos = w2
            else:
                x_pos = (w1 + w2) / 2
            plt.text(
                x_pos, ymax, f'ΔW = {delta_w:.1f}',
                fontsize=9, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.5),
                color=color_map.get(b, 'black'),
                clip_on=True
            )

    title = title or f"Impact of β = {base_beta:.1f} Variation (±{delta_beta:.1f}) on Human vs Ideal Workload–Efficiency"
    plt.title(title, fontsize=14)
    plt.xlabel("Workload W(t)", fontsize=12)
    plt.ylabel("Work Efficiency ε(t)", fontsize=12)
    plt.ylim(0, max(efficiency_max_all) * 2.0 if efficiency_max_all else 1.0)
    plt.grid(True, alpha=0.25)
    handles, labels = plt.gca().get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    plt.legend(uniq.values(), uniq.keys(), loc='best')
    plt.tight_layout()

    if output_path is None:
        output_dir = Path("results/figures")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"figure10_beta_variation_beta={base_beta:.1f}.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.show() if show_plot else plt.close()

    return {
        "intersections_map": intersections_map,
        "output_path": output_path,
    }



# ------------------------------
# 3) Time-series: β ± Δβ (plot only, no compute)
# ------------------------------
def generate_beta_variation_time_series(
    base_beta: float,                 # Base β (center)
    total_workload: float,            # Total workload (completion if ∑ε·Δτ ≥ WT)
    total_time: int,                  # Total time steps
    delta_tau: float,                 # Time step Δτ
    sigma_max: float,                 # σ_max
    epsilon_max: float,               # ε_max
    output_dir: Union[str, Path],     # Output directory (two figures will be generated)
    *,
    delta_beta: float = 0.3,          # Perturbation (±delta_beta)
    dpi: int = 300,                   # Image resolution
    show_plot: bool = True,           # Show window
    ylim_eff: Optional[Tuple[float, float]] = None,    # Optional y-limits for efficiency plot
    ylim_stress: Optional[Tuple[float, float]] = None, # Optional y-limits for stress plot
    title_stub: Optional[str] = None,                  # Extra title fragment (None → auto)
) -> Dict[str, Path]:
    """
    Generate two time-series plots for β ± Δβ comparison:
      (a) Work Efficiency vs Time
      (b) Mental Stress vs Time

    Color coding for β:
      Low β (base-Δβ, clipped to [0.1,3.0]) : Red
      Base β                               : Green
      High β (base+Δβ, clipped to [0.1,3.0]): Blue

    Line style for task completion:
      Completed (∑ε·Δτ ≥ WT) → Solid line
      Not completed → Dashed line
    """
    min_b, max_b = 0.1, 3.0
    beta_low  = max(base_beta - delta_beta, min_b)
    beta_high = min(base_beta + delta_beta, max_b)
    beta_list = [beta_low, base_beta, beta_high]

    color_map = {beta_low: "red", base_beta: "green", beta_high: "blue"}

    sim_pack = simulate_time_series_for_betas(
        beta_list=beta_list,
        total_workload=total_workload,
        total_time=total_time,
        delta_tau=delta_tau,
        sigma_max=sigma_max,
        epsilon_max=epsilon_max,
    )
    time_steps: np.ndarray = sim_pack["time_steps"]
    res_map: Dict[float, Dict[str, Any]] = sim_pack["results"]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    title_stub = title_stub or f"(β={base_beta:.1f}±{delta_beta:.1f}, WT={int(total_workload):,})"

    # --------- (a) Efficiency vs Time ----------
    plt.figure(figsize=(10, 5))
    ymax_eff = 1.0
    for b in beta_list:
        r = res_map[b]
        eff = np.asarray(r["efficiency_series"], dtype=float)
        ymax_eff = max(ymax_eff, float(np.max(eff)))
        completed = bool(r["completed"])
        ls = "-" if completed else "--"
        color = color_map[b]
        status = "Done" if completed else "UnDone"
        label = f"β={b:.1f}" + (" (Center)" if np.isclose(b, base_beta) else "") + f"｜{status}"
        plt.plot(time_steps, eff, color=color, linestyle=ls, linewidth=2.5, label=label)
        if completed and r["t_complete"] is not None:
            t_star = int(r["t_complete"])
            plt.scatter([t_star], [eff[t_star]], color=color, zorder=5)
            plt.text(t_star, eff[t_star], "  t*", color=color, va="bottom", fontsize=9, clip_on=True)

    plt.title(f"Work Efficiency over Time {title_stub}", fontsize=14)
    plt.xlabel("Time (t)", fontsize=12)
    plt.ylabel("Work Efficiency ε(t)", fontsize=12)
    plt.grid(True, alpha=0.25)
    plt.ylim(*(ylim_eff if ylim_eff is not None else (0, ymax_eff * 1.1)))
    handles, labels = plt.gca().get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    plt.legend(uniq.values(), uniq.keys(), loc="best")
    plt.tight_layout()
    out_a = output_dir / f"figure_time_beta±{delta_beta:.1f}_a_efficiency_beta{base_beta:.1f}_WT{int(total_workload)}.png"
    plt.savefig(out_a, dpi=dpi, bbox_inches="tight")
    plt.show() if show_plot else plt.close()

    # --------- (b) Stress vs Time ----------
    plt.figure(figsize=(10, 5))
    ymax_stress = 1.0
    for b in beta_list:
        r = res_map[b]
        stress = np.asarray(r["stress_series"], dtype=float)
        ymax_stress = max(ymax_stress, float(np.max(stress)))
        completed = bool(r["completed"])
        ls = "-" if completed else "--"
        color = color_map[b]
        status = "Done" if completed else "UnDone"
        label = f"β={b:.1f}" + (" (Center)" if np.isclose(b, base_beta) else "") + f"｜{status}"
        plt.plot(time_steps, stress, color=color, linestyle=ls, linewidth=2.5, label=label)
        if completed and r["t_complete"] is not None:
            t_star = int(r["t_complete"])
            plt.scatter([t_star], [stress[t_star]], color=color, zorder=5)
            plt.text(t_star, stress[t_star], "  t*", color=color, va="bottom", fontsize=9, clip_on=True)

    plt.title(f"Mental Stress over Time {title_stub}", fontsize=14)
    plt.xlabel("Time (t)", fontsize=12)
    plt.ylabel("Mental Stress σ(t)", fontsize=12)
    plt.grid(True, alpha=0.25)
    plt.ylim(*(ylim_stress if ylim_stress is not None else (0, ymax_stress * 1.05)))
    handles, labels = plt.gca().get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    plt.legend(uniq.values(), uniq.keys(), loc="best")
    plt.tight_layout()
    out_b = output_dir / f"figure_time_beta±{delta_beta:.1f}_b_stress_beta{base_beta:.1f}_WT{int(total_workload)}.png"
    plt.savefig(out_b, dpi=dpi, bbox_inches="tight")
    plt.show() if show_plot else plt.close()

    return {"efficiency_png": out_a, "stress_png": out_b}
