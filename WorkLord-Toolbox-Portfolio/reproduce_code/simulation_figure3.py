# 6.simulation_figure3.py

import numpy as np
import matplotlib.pyplot as plt

# Import formula modules and configuration
from formulas_and_variables import efficiency_from_workload, ideal_efficiency
import simulation_config as cfg  # Contains BETA_LIST, SIGMA_MAX, EPSILON_MAX

def plot_efficiency_curve():
    beta = cfg.BETA_LIST[1]  # β = 1.0

    # Workload range W(t) from 0 to β * σ_max
    W_range = np.linspace(0, beta * cfg.SIGMA_MAX, 300)

    # Compute human work efficiency (Formula 5)
    efficiency_values = [
        efficiency_from_workload(W, beta, cfg.SIGMA_MAX, cfg.EPSILON_MAX)
        for W in W_range
    ]

    # Compute ideal efficiency ε(t) = W(t) (Formula 6)
    ideal_efficiency_values = [ideal_efficiency(W) for W in W_range]

    # Find intersection points where human efficiency ≈ ideal efficiency
    raw_indices = np.where(
        np.isclose(efficiency_values, ideal_efficiency_values, atol=0.37)
    )[0]

    # Filter out near-zero intersections (efficiency < 5)
    intersection_indices = [i for i in raw_indices if efficiency_values[i] > 5]

    # Extract first and last intersection points
    first_idx, second_idx = intersection_indices[0], intersection_indices[-1]
    first_intersect = (W_range[first_idx], efficiency_values[first_idx])
    second_intersect = (W_range[second_idx], efficiency_values[second_idx])

    # Plot configuration
    plt.figure(figsize=(9, 5))

    # Plot human efficiency curve
    #plt.plot(W_range, efficiency_values, color='black', linewidth=5, label='Human workload-effort modeling')

    # Plot ideal efficiency curve
    plt.plot(W_range, ideal_efficiency_values, color='green', linewidth=5, label='Ideal Efficiency modeling')

    # Fill task zones with color
    #plt.axvspan(W_range[0], first_intersect[0], color='skyblue', alpha=0.25, label='Laid-back Zone')
    #plt.axvspan(first_intersect[0], second_intersect[0], color='lightgreen', alpha=0.3, label='Capacity Zone')
    #plt.axvspan(second_intersect[0], W_range[-1], color='salmon', alpha=0.25, label='Fatigue Zone')

    # Mark intersection points
    #plt.scatter(*first_intersect, color='red', zorder=10)
    #plt.scatter(*second_intersect, color='red', zorder=10)

    # Vertical lines at intersection points
    #plt.axvline(first_intersect[0], color='black', linestyle='--')
    #plt.axvline(second_intersect[0], color='black', linestyle='--')

    # Zone labels
    #plt.text(25, 120, 'Laid-back Zone', color='blue', fontsize=12, ha='center')
    #plt.text(75, 120, 'Capacity Zone', color='green', fontsize=12, ha='center')
    #plt.text(150, 120, 'Fatigue Zone', color='red', fontsize=12, ha='center')

    # Title and axis labels
    plt.title("Figure 3. Human vs Ideal workload–efficiency at β = 1.0", fontsize=14)
    plt.xlabel("Workload W(t)", fontsize=12)
    plt.ylabel("Work Efficiency ε(t)", fontsize=12)

    # Display legend and layout
    plt.legend()
    plt.tight_layout()

    # Save figure
    output_path = "../figures/figure_3_workload_efficiency_beta_1.0.png"
    plt.savefig(output_path, dpi=300)
    print(f"✅ Image saved successfully: {output_path}")

    plt.show()

if __name__ == "__main__":
    plot_efficiency_curve()
