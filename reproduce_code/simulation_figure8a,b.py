# 11.simulation_figure8a,b.py

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add ../code directory to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "code"))

# Import formulas and configuration
from formulas_and_variables import (
    efficiency_from_workload,
    simplified_stress_effort_model,
    dynamic_subjective_workload
)
import simulation_config as cfg

# Time setup
time_steps = np.arange(0, cfg.TOTAL_TIME)
delta_tau = cfg.DELTA_TAU

# Line styles for β values
colors = ['red', 'red', 'red']
linestyles = [':', '-', '--']

# Storage for simulation results
efficiency_all = []
stress_all = []

# Simulate for each β value
for idx, beta in enumerate(cfg.BETA_LIST):
    efficiency_series = []
    stress_series = []
    epsilon_history = []

    for t in range(cfg.TOTAL_TIME):
        # Compute W(t) using Formula 7
        W_t = dynamic_subjective_workload(
            t_index=t,
            total_time=cfg.TOTAL_TIME,
            total_workload=cfg.TOTAL_WORKLOAD[1],  # WT = 5000
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

# Figure 8(a): Work Efficiency over Time
plt.figure(figsize=(10, 5))
for i, (beta, eff_curve) in reversed(list(enumerate(efficiency_all))):
    plt.plot(time_steps, eff_curve, color=colors[i], linestyle=linestyles[i],
             label=f'β = {beta}', linewidth=2.5)

plt.title("Figure 8(a) Work Efficiency over Time at WT = 5K", fontsize=14)
plt.xlabel("Time (t)", fontsize=12)
plt.ylabel("Work Efficiency ε(t)", fontsize=12)
plt.legend()
plt.tight_layout()

# Save Figure 8a
output_path_8a = "../figures/figure8a_work_efficiency_vs_time_WT5K.png"
plt.savefig(output_path_8a, dpi=300)
print(f"✅ Image saved: {output_path_8a}")
plt.show()

# Figure 8(b): Mental Stress over Time
plt.figure(figsize=(10, 5))
for i, (beta, stress_curve) in enumerate(stress_all):
    plt.plot(time_steps, stress_curve, color=colors[i], linestyle=linestyles[i],
             label=f'β = {beta}', linewidth=2.5)

plt.title("Figure 8(b) Mental Stress over Time at WT = 5K", fontsize=14)
plt.xlabel("Time (t)", fontsize=12)
plt.ylabel("Mental Stress σ(t)", fontsize=12)
plt.ylim(35, 73)
plt.legend()
plt.tight_layout()

# Save Figure 8b
output_path_8b = "../figures/figure8b_mental_stress_vs_time_WT5K.png"
plt.savefig(output_path_8b, dpi=300)
print(f"✅ Image saved: {output_path_8b}")
plt.show()
