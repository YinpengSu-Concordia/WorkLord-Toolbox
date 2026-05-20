# 4.simulation_figure1.py

'''
Figure 1 is not derived from the formulas discussed in the current paper,
but originates from earlier studies by Nguyen & Zeng (2012, 2017),
which utilized a Raised-Cosine curve to model stress-effort relationship.

E(σ) = { 0.5 * [1 + cos( (σ − μ) / r * π )],   μ − r ≤ σ ≤ μ + r
         0,                                   otherwise

    μ: peak position (optimal stress σ_opt)
    r: control range (smaller r leads to sharper peak)
'''

import numpy as np
import matplotlib.pyplot as plt

# Raised-Cosine function: input stress sigma, center point mu, and half-width r
def raised_cosine(sigma, mu, r):
    y = np.zeros_like(sigma)
    # Within [μ − r, μ + r], compute inverted-U shape using cosine function
    # Outside this range, effort is zero
    inside = (sigma >= mu - r) & (sigma <= mu + r)
    y[inside] = 0.5 * (1 + np.cos((sigma[inside] - mu) / r * np.pi))
    return y

# Define σ range from 0 to σ_max = 200 with 300 equally spaced points for smooth plotting
sigma = np.linspace(0, 200, 300)  # X-axis values
mu = 100       # Optimal stress point (center)
r = 75         # Half-width, controls σ_i and σ_h positions

# Compute corresponding E(σ) values
effort = raised_cosine(sigma, mu, r)  # Y-axis values

# Plot configuration
plt.figure(figsize=(9, 5))  # Create 9×5 inch figure

# Plot the curve with specified line width and color
plt.plot(sigma, effort, color='black', linewidth=2)

# Calculate σ_i and σ_h thresholds
sigma_i = mu - 0.7 * r
sigma_h = mu + 0.7 * r

# Add dashed threshold lines at σ_i and σ_h
plt.axvline(sigma_i, linestyle='--', color='black')
plt.axvline(sigma_h, linestyle='--', color='black')

# Add red arrows and annotations
plt.annotate('Low', xy=(sigma_i - 30, 0.5), xytext=(sigma_i - 30, 1),
             arrowprops=dict(arrowstyle='->', color='red'), color='red', ha='center')
plt.annotate('Medium', xy=(mu, 1.0), xytext=(mu, 1.1),
             arrowprops=dict(arrowstyle='->', color='red'), color='red', ha='center')
plt.annotate('High', xy=(sigma_h + 30, 0.5), xytext=(sigma_h + 30, 1),
             arrowprops=dict(arrowstyle='->', color='red'), color='red', ha='center')

# Add title and axis labels
plt.title("Figure 1. The stress–effort model (Nguyen and Zeng 2012, 2017).", fontsize=14)
plt.xlabel('Mental Stress σ(t)', fontsize=12)
plt.ylabel('Mental Effort E(t)', fontsize=12)

# Add math symbol labels below σ_i and σ_h
plt.text(sigma_i, -0.16, r'$\sigma_i$', fontsize=12, ha='center')
plt.text(sigma_h, -0.16, r'$\sigma_h$', fontsize=12, ha='center')

# Clean visual appearance
plt.ylim(-0.1, 1.2)  # Remove whitespace below y=0
plt.xticks([]); plt.yticks([])  # Remove x/y ticks
# plt.box(False)  # Optional: remove frame
# plt.grid(False) # Optional: remove grid lines

plt.tight_layout()  # Auto-adjust layout to prevent label cutoff

# Save figure
output_path = "../figures/figure_1_The_stress–effort model (Nguyen and Zeng 2012, 2017).png"
plt.savefig(output_path, dpi=300)  # Save at 300 dpi (suitable for publication)
print(f"✅ Image saved successfully: {output_path}")
plt.show()  # Display figure
