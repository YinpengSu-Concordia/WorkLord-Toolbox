# 8.simulation_figure5a,b.py

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add ../code directory to path for module imports
sys.path.append(str(Path(__file__).resolve().parents[1] / "code"))

# Import formulas and config
from formulas_and_variables import (
    efficiency_from_workload,
    simplified_stress_effort_model,
    dynamic_subjective_workload
)
import simulation_config as cfg

# Time configuration
time_steps = np.arange(0, cfg.TOTAL_TIME)  # From 0 to TOTAL_TIME-1
delta_tau = cfg.DELTA_TAU

# Line styles for each β
colors = ['gray', 'black', 'red']
linestyles = [':', '-', '--']

# Storage for simulation results
efficiency_all = []
stress_all = []

# Simulation for each β value
for idx, beta in enumerate(cfg.BETA_LIST):
    efficiency_series = []
    stress_series = []
    epsilon_history = []

    for t in range(cfg.TOTAL_TIME):
        # Compute W(t) using Formula 7
        W_t = dynamic_subjective_workload(
            t_index=t,
            total_time=cfg.TOTAL_TIME,
            total_workload=cfg.TOTAL_WORKLOAD[4],  # WT = 12500
            epsilon_series=epsilon_history,
            delta_tau=delta_tau
        )

        # Compute ε(t) using Formula 5
        epsilon_t = efficiency_from_workload(W_t, beta, cfg.SIGMA_MAX, cfg.EPSILON_MAX)
        efficiency_series.append(epsilon_t)
        epsilon_history.append(epsilon_t)

        # Compute σ(t) using Formula 2
        sigma_t = min(simplified_stress_effort_model(W_t, beta), cfg.SIGMA_MAX)
        stress_series.append(sigma_t)

    efficiency_all.append((beta, efficiency_series))
    stress_all.append((beta, stress_series))

# ------------------------ Plotting ------------------------

# Figure 5(a): Work Efficiency over Time
plt.figure(figsize=(10, 5))
for i, (beta, eff_curve) in reversed(list(enumerate(efficiency_all))):
    plt.plot(time_steps, eff_curve, color=colors[i], linestyle=linestyles[i],
             label=f'β = {beta}', linewidth=2.5)

plt.title("Figure 5(a) Work Efficiency over Time at WT = 12.5K", fontsize=14)
plt.xlabel("Time (t)", fontsize=12)
plt.ylabel("Work Efficiency ε(t)", fontsize=12)
plt.legend()
plt.tight_layout()

# Save Figure 5a
output_path_5a = "../figures/figure5a_work_efficiency_vs_time_WT12.5K.png"
plt.savefig(output_path_5a, dpi=300)
print(f"✅ Image saved: {output_path_5a}")
plt.show()

# Figure 5(b): Mental Stress over Time
plt.figure(figsize=(10, 5))
for i, (beta, stress_curve) in enumerate(stress_all):
    plt.plot(time_steps, stress_curve, color=colors[i], linestyle=linestyles[i],
             label=f'β = {beta}', linewidth=2.5)

plt.title("Figure 5(b) Mental Stress over Time at WT = 12.5K", fontsize=14)
plt.xlabel("Time (t)", fontsize=12)
plt.ylabel("Mental Stress σ(t)", fontsize=12)
plt.ylim(60, cfg.SIGMA_MAX + 5)
plt.legend()
plt.tight_layout()

# Save Figure 5b
output_path_5b = "../figures/figure5b_mental_stress_vs_time_WT12.5K.png"
plt.savefig(output_path_5b, dpi=300)
print(f"✅ Image saved: {output_path_5b}")
plt.show()
