# 2.formulas_and_variables.py

"""
Formulas and Variables Definition Module: formulas_and_variables.py

This module defines the mathematical models and variable meanings used throughout the paper.

Note: All parentheses () in variable names are replaced with underscores (_) for code compatibility, e.g., W(t) -> W_t
"""

"""
# Section: Original Mental Stress-Effort Model (Formula 1)
"""
def original_stress_effort_model(W_t: float, K_t: float, S_t: float, A_t: float) -> float:
    """
    Original Mental Stress-Effort Model (Formula 1):
        σ_t = W_t / ((K_t + S_t) * A_t)

    Description:
        Mental stress σ_t arises from perceived task load W_t and is modulated by individual mental capacity.
        Mental capacity comprises three components:
            - K_t: task-related knowledge and experience;
            - S_t: reasoning ability, thinking style, and strategies;
            - A_t: emotional regulation capacity (the ability to mobilize skills under pressure, including attention and motivation), range ∈ (0, 1)

    Parameters:
        W_t : float
            Perceived task load at current time (W_t), unit: arbitrary task units
        K_t : float
            Current knowledge level relevant to the task (Knowledge); higher values indicate greater proficiency
        S_t : float
            Skill level for the current task (Skill), reflecting reasoning/strategic ability
        A_t : float
            Attention/emotional state (Affect), must be within the range (0, 1)

    Returns:
        σ_t : float
            Current mental stress σ_t; larger values indicate higher stress
    """
    if A_t <= 0 or A_t >= 1:
        raise ValueError("A(t) must be within (0, 1), current value invalid: {}".format(A_t))

    return W_t / ((K_t + S_t) * A_t)


"""
# Section: Simplified Mental Stress Model (Formula 2)
"""

def simplified_stress_effort_model(W_t: float, beta: float) -> float:
    """
    Simplified Mental Stress Model (Formula 2):
        σ_t = W_t / β
        where β = (K + S) * A is the composite mental capacity constant

    Description:
        Under short-duration tasks, knowledge, skills, and emotional state are assumed stable,
        allowing simplification of mental capacity into a constant β.
        β reflects individual resilience: higher β indicates stronger capacity, lower β means more sensitivity to task load.

    Parameters:
        W_t : float
            Perceived task load at current time, unit: arbitrary task units
        β : float
            Mental capacity constant β, defined as (K + S) * A, where:
              - K: knowledge level
              - S: skill level
              - A: attention level ∈ (0, 1)

    Returns:
        σ_t : float
            Current mental stress σ_t; larger values indicate higher stress
    """
    if beta <= 0:
        raise ValueError("β (mental capacity constant) must be positive, current value invalid: {}".format(beta))

    return W_t / beta


"""
# Section: Raised-Cosine Mental Stress-Effort Model (Formula 3)
"""

import numpy as np

def original_RC_stress_effort_model(sigma_t: float, sigma_max: float) -> float:
    """
    Raised-Cosine Mental Stress-Effort Function Model (Formula 3):
        E_t = f(σ_t) = 
            0.5 * [1 + cos( (σ_t - 0.5 * σ_max) / (0.5 * σ_max) * π )],   if 0 ≤ σ(t) ≤ σ_max
            0,                                                           otherwise

    Description:
        Models the nonlinear relationship between mental stress σ(t) and mental effort E(t) as an inverted-U curve.
        Maximum effort is reached when σ(t) = 0.5 * σ_max.
        Too little or too much stress results in reduced effort.

    Parameters:
        σ_t : float
            Current mental stress σ_t (computed from stress models)
        σ_max : float
            Maximum tolerable mental stress σ_max (defines the center and bounds of the inverted-U curve)

    Returns:
        E_t : float
            Current mental effort E_t, range ∈ [0, 1]; higher values indicate higher efficiency
    """
    if 0 <= sigma_t <= sigma_max:
        return 0.5 * (1 + np.cos((sigma_t - 0.5 * sigma_max) / (0.5 * sigma_max) * np.pi))
    else:
        return 0.0


"""
# Section: Simplified Raised-Cosine Stress-Effort Model (Formula 4)
"""

def simplified_RC_stress_effort_model(W_t: float, beta: float, sigma_max: float) -> float:
    """
    Simplified Raised-Cosine Mental Stress-Effort Model (Formula 4):
        E(t) = 
            0.5 * [1 + cos( (W_t - 0.5 * β * σ_max) / (0.5 * β * σ_max) * π )],   if 0 ≤ W(t) ≤ β * σ_max
            0,                                                                   otherwise

    Description:
        Substitutes simplified stress formula (Formula 2) into the RC effort function (Formula 3),
        expressing effort as a function of workload W(t).
        Effort peaks when workload equals half of β * σ_max.

    Parameters:
        W_t : float
            Perceived task load at current time
        β : float
            Mental capacity constant β = (K + S) * A
        σ_max : float
            Maximum tolerable stress σ_max

    Returns:
        E_t : float
            Mental effort E_t, range ∈ [0, 1], follows inverted-U shape over W_t
    """
    if beta <= 0 or sigma_max <= 0:
        raise ValueError("β and σ_max must be positive, invalid inputs: beta={}, sigma_max={}".format(beta, sigma_max))

    upper_bound = beta * sigma_max
    if 0 <= W_t <= upper_bound:
        return 0.5 * (1 + np.cos((W_t - 0.5 * upper_bound) / (0.5 * upper_bound) * np.pi))
    else:
        return 0.0


"""
# Section: Work Efficiency Model with Weighted Mental Capacity (Formula 5)
"""

def efficiency_from_workload(W_t: float, beta: float, sigma_max: float, epsilon_max: float) -> float:
    """
    Work Efficiency Model with Weighted Mental Capacity (Formula 5):
        ε_t = β ⋅ ε_max ⋅ E_t
        Substituting E_t from Formula 4:
        ε_t = 
            β * ε_max * 0.5 * [1 + cos( (W_t - 0.5 * β * σ_max) / (0.5 * β * σ_max) * π )],   if 0 ≤ W(t) ≤ β * σ_max
            0,                                                                               otherwise

    Description:
        Effort E(t) represents mental energy. Weighted by β, this yields the actual task efficiency ε(t).
        Efficiency follows the same inverted-U trend as E(t), modulated by β and ε_max.

    Parameters:
        β : float
            Mental capacity level β = (K + S) * A
        ε_max : float
            Maximum efficiency under unit effort ε_max
        W_t : float
            Perceived workload at current time
        σ_max : float
            Maximum tolerable mental stress

    Returns:
        ε_t : float
            Work efficiency ε_t at current time, range ∈ [0, β * ε_max]
    """
    if beta <= 0 or sigma_max <= 0 or epsilon_max <= 0:
        raise ValueError(f"Invalid input: beta, sigma_max, epsilon_max must be positive. Received: beta={beta}, sigma_max={sigma_max}, epsilon_max={epsilon_max}")

    upper_bound = beta * sigma_max
    if 0 <= W_t <= upper_bound:
        return beta * epsilon_max * 0.5 * (1 + np.cos((W_t - 0.5 * upper_bound) / (0.5 * upper_bound) * np.pi))
    else:
        return 0.0


"""
# Section: Ideal Work Efficiency Model (Formula 6)
"""

def ideal_efficiency(W_t: float) -> float:
    """
    Ideal Work Efficiency Model (Formula 6):
        ε_t = W_t

    Description:
        Under ideal conditions (no human limitations), efficiency equals workload.
        This model serves as a baseline to compare actual efficiency and to classify task zones:
            - Laid-back Zone: underload, low effort, potential slack;
            - Capacity Zone: matched workload-efficiency;
            - Fatigue Zone: overload, decreased efficiency, increased stress.

    Parameters:
        W_t : float
            Perceived task load at current time

    Returns:
        ε_t : float
            Ideal work efficiency, equal to W_t
    """
    return W_t


"""
# Section: Dynamic Subjective Workload Model (Formula 7)
"""

def dynamic_subjective_workload(
    t_index: int,
    total_time: int,
    total_workload: float,
    epsilon_series: list[float],
    delta_tau: float = 1.0
) -> float:
    """
    Dynamic Subjective Workload Model (Formula 7):
        W_t = (W_T - ∑₀ᵗ ε_τ ⋅ Δτ) / (T - t)

    Description:
        Given fixed total workload W_T, subjective workload W(t) at time t is determined by
        completed work and remaining time.
        - More work done → lower W(t)
        - Less time left → higher W(t)

    Parameters:
        t_index : int
            Discrete time index t (starting from 0)
        total_time : int
            Total task duration T
        total_workload : float
            Total assigned workload W_T
        epsilon_series : list[float]
            Efficiency sequence ε(τ) from time 0 to t_index
        delta_tau : float
            Time step Δτ, default is 1.0

    Returns:
        W_t : float
            Current perceived workload W_t
    """
    if not (0 <= t_index <= total_time):
        raise ValueError(f"t_index out of range: should be in [0, {total_time}], got t_index = {t_index}")

    remaining_time = total_time - t_index
    completed_work = sum(epsilon_series[:t_index + 1]) * delta_tau

    if remaining_time > 0:
        return (total_workload - completed_work) / remaining_time
    else:
        return 0.0  # or np.nan if undefined
