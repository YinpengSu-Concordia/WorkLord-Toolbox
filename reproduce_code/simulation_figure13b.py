# 18.simulation_figure13b.py

import numpy as np
import matplotlib.pyplot as plt
import simulation_config as cfg

# Configuration
BETA_LIST = cfg.BETA_LIST
SIGMA_MAX = 140  # Adjusted σ_max for this figure
EPSILON_MAX = cfg.EPSILON_MAX

# Work efficiency function (Formula 5)
def efficiency_from_workload(W_t, beta, sigma_max, epsilon_max):
    upper_bound = beta * sigma_max
    if 0 <= W_t <= upper_bound:
        return beta * epsilon_max * 0.5 * (1 + np.cos((W_t - 0.5 * upper_bound) / (0.5 * upper_bound) * np.pi))
    else:
        return 0.0

# Ideal efficiency function (Formula 6)
def ideal_efficiency(W_t):
    return W_t

# Find intersections between human and ideal efficiency
def find_intersections(W_range, beta, sigma_max, epsilon_max, threshold=0.5, ignore_below=5):
    efficiency_vals = [efficiency_from_workload(w, beta, sigma_max, epsilon_max) for w in W_range]
    ideal_vals = W_range
    diff = np.abs(np.array(efficiency_vals) - np.array(ideal_vals))
    close_points = np.where(diff < threshold)[0]
    valid_indices = [idx for idx in close_points if W_range[idx] >= ignore_below]
    if len(valid_indices) >= 2:
        return [W_range[valid_indices[0]], W_range[valid_indices[-1]]]
    else:
        return []

# Workload range
W_max = max(BETA_LIST) * SIGMA_MAX
W_range = np.linspace(0, W_max, 500)

# Plot setup
plt.figure(figsize=(10, 6))
colors = ['red', 'green', 'blue']
linestyles = [':', '-', '--']

for i, beta in enumerate(BETA_LIST):
    efficiency_vals = [efficiency_from_workload(w, beta, SIGMA_MAX, EPSILON_MAX) for w in W_range]
    plt.plot(W_range, efficiency_vals, color=colors[i], linestyle=linestyles[i], linewidth=3, label=f'β = {beta}')

ideal_vals = [ideal_efficiency(w) for w in W_range]
plt.plot(W_range, ideal_vals, color='black', linestyle='-', linewidth=2, label='Ideal Efficiency')

# Intersections
intersections = {}
for beta in BETA_LIST:
    pts = find_intersections(W_range, beta, SIGMA_MAX, EPSILON_MAX, threshold=1.0, ignore_below=5)
    if len(pts) == 2:
        intersections[beta] = pts

intersection_colors = {
    0.7: ['darkred', 'orangered'],
    1.0: ['lime', 'darkgreen'],
    1.3: ['navy', 'dodgerblue']
}

for beta, x_vals in intersections.items():
    for i, x in enumerate(x_vals):
        y = ideal_efficiency(x)
        point_color = intersection_colors[beta][i]
        plt.scatter(x, y, color=point_color, zorder=5)
        plt.text(x, y + 25, f'W={x:.1f}', ha='center', fontsize=8, color=point_color)

# Capacity range labels
for beta, x_vals in intersections.items():
    if len(x_vals) == 2:
        w_left, w_right = x_vals
        delta_w = w_right - w_left
        mid_x = (w_left + w_right) / 2
        mid_y = 130
        range_label = f"Range:\nΔW = {delta_w:.1f}"
        label_color = intersection_colors[beta][0]
        plt.text(mid_x, mid_y, range_label, fontsize=9, color=label_color, ha='center')

# Final plot settings
plt.title("Figure 13b. Comparing Mental Capacities β = 0.7, 1.0, 1.3 under σ_max = 140", fontsize=14)
plt.xlabel("Workload W(t)", fontsize=12)
plt.ylabel("Work Efficiency ε(t)", fontsize=12)
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save figure
output_path = "../figures/figure13b_workload_efficiency_beta_0.7_1.0_1.3_sigmax140.png"
plt.savefig(output_path, dpi=300)
print(f"✅ Image saved: {output_path}")
plt.show()
