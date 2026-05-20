def get_default_params() -> dict:
    
    return {
    
    "beta": 1.0,                # Individual mental capacity levels (β)
    "sigma_max": 200,           # Maximum tolerable mental stress (σ_max)
    "epsilon_max": 100,         # # Maximum efficiency under unit mental effort (ε_max)
    "total_workload": 10000,    # Total workload assigned (W_T)
    "total_time": 100,          # Total duration of simulation (T)
    "delta_tau": 1.0,           # Time step (Δτ)
}
