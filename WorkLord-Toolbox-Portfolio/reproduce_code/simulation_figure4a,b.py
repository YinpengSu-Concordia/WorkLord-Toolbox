# 7.simulation_figure4a,b.py

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add ../code directory to path for imports
sys.path.append(str(Path(__file__).resolve().parents[1] / "code"))

# Import formulas and configuration
from formulas_and_variables import (
    efficiency_from_workload,
    simplified_stress_effort_model,
    dynamic_subjective_workload
)
import simulation_config as cfg

# Time configuration
time_steps = np.arange(0, cfg.TOTAL_TIME)  # From 0 to TOTAL_TIME-1
delta_tau = cfg.DELTA_TAU

# Plot styling for each β level
colors = ['gray', 'black', 'black']
linestyles = [':', '-', '--']

# Storage for efficiency and stress curves
efficiency_all = []
stress_all = []

# Simulation loop for each β value
for idx, beta in enumerate(cfg.BETA_LIST):
    efficiency_series = []
    stress_series = []
    epsilon_history = []

    for t in range(cfg.TOTAL_TIME):
        # Compute subjective workload W(t) using Formula 7
        W_t = dynamic_subjective_workload(
            t_index=t,
            total_time=cfg.TOTAL_TIME,
            total_workload=cfg.TOTAL_WORKLOAD[5],  # WT = 15000
            epsilon_series=epsilon_history,
            delta_tau=delta_tau
        )

        # Compute work efficiency ε(t) using Formula 5
        epsilon_t = efficiency_from_workload(W_t, beta, cfg.SIGMA_MAX, cfg.EPSILON_MAX)
        efficiency_series.append(epsilon_t)
        epsilon_history.append(epsilon_t)

        # Compute mental stress σ(t) using Formula 2
        sigma_t = min(simplified_stress_effort_model(W_t, beta), cfg.SIGMA_MAX)
        stress_series.append(sigma_t)

    # Store results for plotting
    efficiency_all.append((beta, efficiency_series))
    stress_all.append((beta, stress_series))

# ------------------------ Plotting ------------------------

# Figure 4(a): Work Efficiency over Time
plt.figure(figsize=(10, 5))
for i, (beta, eff_curve) in reversed(list(enumerate(efficiency_all))):
    plt.plot(time_steps, eff_curve, color=colors[i], linestyle=linestyles[i],
             label=f'β = {beta}', linewidth=2.5)

plt.title("Figure 4(a) Work Efficiency over Time at WT = 15K", fontsize=14)
plt.xlabel("Time (t)", fontsize=12)
plt.ylabel("Work Efficiency ε(t)", fontsize=12)
plt.legend()
plt.tight_layout()

# Save Figure 4a
output_path_4a = "../figures/figure4a_work_efficiency_vs_time_WT15K.png"
plt.savefig(output_path_4a, dpi=300)
print(f"✅ Image saved: {output_path_4a}")
plt.show()

# Figure 4(b): Mental Stress over Time
plt.figure(figsize=(10, 5))
for i, (beta, stress_curve) in enumerate(stress_all):
    plt.plot(time_steps, stress_curve, color=colors[i], linestyle=linestyles[i],
             label=f'β = {beta}', linewidth=2.5)

plt.title("Figure 4(b) Mental Stress over Time at WT = 15K", fontsize=14)
plt.xlabel("Time (t)", fontsize=12)
plt.ylabel("Mental Stress σ(t)", fontsize=12)
plt.ylim(110, cfg.SIGMA_MAX + 5)
plt.legend()
plt.tight_layout()

# Save Figure 4b
output_path_4b = "../figures/figure4b_mental_stress_vs_time_WT15K.png"
plt.savefig(output_path_4b, dpi=300)
print(f"✅ Image saved: {output_path_4b}")
plt.show()
