# 14.simulation_figure11.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from formulas_and_variables import efficiency_from_workload, ideal_efficiency
import simulation_config as cfg

def plot_efficiency_curve():
    beta = cfg.BETA_LIST[0]  # β = 0.7
    W_range = np.linspace(0, beta * cfg.SIGMA_MAX, 300)

    efficiency_values = [
        efficiency_from_workload(W, beta, cfg.SIGMA_MAX, cfg.EPSILON_MAX)
        for W in W_range
    ]

    ideal_efficiency_values = [ideal_efficiency(W) for W in W_range]

    # Find intersection points between human and ideal efficiency curves
    raw_indices = np.where(
        np.isclose(efficiency_values, ideal_efficiency_values, atol=0.232)
    )[0]
    intersection_indices = [i for i in raw_indices if efficiency_values[i] > 5]

    first_idx, second_idx = intersection_indices[0], intersection_indices[-1]
    first_intersect = (W_range[first_idx], efficiency_values[first_idx])
    second_intersect = (W_range[second_idx], efficiency_values[second_idx])
    print(first_intersect, second_intersect)

    # Plot setup
    plt.figure(figsize=(9, 5))
    plt.plot(W_range, efficiency_values, color='blue', linewidth=2, label='Human workload-effort modeling')
    plt.plot(W_range, ideal_efficiency_values, color='green', linewidth=2, label='Ideal Efficiency modeling')

    # Fill zones
    plt.axvspan(W_range[0], first_intersect[0], color='skyblue', alpha=0.25, label='Laid-back Zone')
    plt.axvspan(first_intersect[0], second_intersect[0], color='lightgreen', alpha=0.3, label='Capacity Zone')
    plt.axvspan(second_intersect[0], W_range[-1], color='salmon', alpha=0.25, label='Fatigue Zone')

    # Mark intersection points
    plt.scatter(*first_intersect, color='red', zorder=10)
    plt.scatter(*second_intersect, facecolors='none', edgecolors='red', s=80, linewidths=2, zorder=10)

    # Vertical lines at zone boundaries
    plt.axvline(first_intersect[0], color='black', linestyle='--')
    plt.axvline(second_intersect[0], color='black', linestyle='--')

    # Zone labels
    plt.text(18, 120, 'Laid-back Zone', color='blue', fontsize=12, ha='center')
    plt.text(53, 120, 'Capacity Zone', color='green', fontsize=12, ha='center')
    plt.text(98, 120, 'Fatigue Zone', color='red', fontsize=12, ha='center')

    # Add curved arrows
    def draw_curved_arrow(ax, xy_start, xy_end, color='red', rad=0.25, linewidth=2):
        arrow = FancyArrowPatch(
            xy_start, xy_end,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle='-|>',
            color=color,
            mutation_scale=15,
            linewidth=linewidth
        )
        ax.add_patch(arrow)

    ax = plt.gca()

    draw_curved_arrow(ax, (first_intersect[0] - 30, first_intersect[1] - 37),
                      (first_intersect[0] - 3, first_intersect[1] - 10),
                      color='black', rad=0.2)

    draw_curved_arrow(ax, (first_intersect[0] + 15, first_intersect[1] + 30),
                      (first_intersect[0] + 2, first_intersect[1] + 7),
                      color='red', rad=0.1)

    draw_curved_arrow(ax, (second_intersect[0] - 3, second_intersect[0] + 5),
                      (first_intersect[0] + 17, first_intersect[1] + 32),
                      color='red', rad=0.2)

    draw_curved_arrow(ax, (second_intersect[0] + 10, second_intersect[1] - 10),
                      (second_intersect[0] + 45, second_intersect[1] - 65),
                      color='black', rad=-0.1)

    # Titles and labels
    plt.title("Figure 11. Human vs Ideal Workload–Efficiency at β = 0.7", fontsize=14)
    plt.xlabel("Workload W(t)", fontsize=12)
    plt.ylabel("Work Efficiency ε(t)", fontsize=12)
    plt.legend()
    plt.tight_layout()

    # Save figure
    output_path = "../figures/figure11_capacity_zone_trends_beta_0.7.png"
    plt.savefig(output_path, dpi=300)
    print(f"✅ Image saved: {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_efficiency_curve()
