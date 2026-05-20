# 5.simulation_figure2.py

import numpy as np
import matplotlib.pyplot as plt

from formulas_and_variables import original_RC_stress_effort_model
import simulation_config as cfg  # Import beta, sigma_max, etc.

'''
Note:
W(t) here refers to perceived workload treated as a variable on the x-axis.
We are plotting a static function curve, not simulating the time-dependent process of W(t).
Thus, W can be treated as a continuous variable ranging from 0 to β × σ_max.
We use np.linspace() to generate W values and compute corresponding effort values to plot an inverted-U relationship.
'''

def plot_figure2_raised_cosine():
    # Generate sigma range from 0 to sigma_max (200), 300 points for smooth curve
    sigma_range = np.linspace(0, cfg.SIGMA_MAX, 300)  # X-axis values
    
    # Compute corresponding E(σ) values; multiply by 100 for scaling as in the paper
    effort_values = [original_RC_stress_effort_model(sigma, cfg.SIGMA_MAX) * 100 for sigma in sigma_range]
    
    # Plot configuration
    plt.figure(figsize=(9, 5))  # Create 9×5 inch figure
    plt.plot(sigma_range, effort_values, linewidth=5, color='black')  # Plot curve
    
    # Add title and labels
    plt.title("Figure 2. Human workload–effort relationship", fontsize=14)
    plt.xlabel("Workload σ(t)", fontsize=12)
    plt.ylabel("Mental effort E(t)", fontsize=12)
    plt.tight_layout()  # Adjust layout to avoid label cutoff
    
    # Save figure
    output_path = "../figures/figure_2_Human_workload_effort_relationship.png"
    plt.savefig(output_path, dpi=300)  # Save at 300 dpi for publication
    print(f"✅ Image saved successfully: {output_path}")
    
    # Display figure
    plt.show()

if __name__ == "__main__":
    plot_figure2_raised_cosine()
