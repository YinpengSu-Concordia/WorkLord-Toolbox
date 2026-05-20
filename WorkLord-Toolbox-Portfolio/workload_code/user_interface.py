# workload_code/user_interface.py
from __future__ import annotations
from typing import Dict, Any, Tuple, Optional
import logging

from config.default_simulation_config import get_default_params
from .simulation_engine import run_simulation

logger = logging.getLogger(__name__)

# ========= Parameter semantics and suggested ranges =========
PARAM_SPECS: Dict[str, Dict[str, Any]] = {
    "beta": {
        "desc": "Mental capacity coefficient, representing ability/regulation level; larger values usually mean higher efficiency and stronger stress resistance under the same workload.",
        "unit": "Dimensionless (typical values {0.7, 1.0, 1.3})",
        "range": (0.1, 3.0),
        "suggest": "Commonly 0.7 / 1.0 / 1.3; too small → early exhaustion, too large → overly optimistic curve.",
        "too_small": "β too small: efficiency peak arrives earlier and lower, easier to fall into fatigue zone, higher failure probability.",
        "too_large": "β too large: curve too idealized, may hide actual stress rise risks (results overly optimistic).",
        "type": float,
    },
    "epsilon_max": {
        "desc": "Maximum efficiency limit (upper bound of unit-time output under ideal conditions).",
        "unit": "Task units per time (commonly 100; sometimes 130 / 70 used for comparison plots)",
        "range": (10.0, 1000.0),
        "suggest": "Commonly 100; too small lowers the whole efficiency curve, too large results in unrealistic productivity.",
        "too_small": "ε_max too small: task completion is hard even within capacity zone, curve stays low overall.",
        "too_large": "ε_max too large: efficiency overestimated, may shift capacity zone too far right, unrealistic.",
        "type": float,
    },
    "sigma_max": {
        "desc": "Maximum tolerable mental stress; beyond this, enters fatigue/collapse state.",
        "unit": "Custom unit (commonly 200; sometimes 260/140 in comparison plots)",
        "range": (20.0, 1000.0),
        "suggest": "Commonly 200; too low → premature fatigue, too high → risk hidden.",
        "too_small": "σ_max too small: collapse occurs too early, efficiency falls quickly.",
        "too_large": "σ_max too large: model insensitive to risk, curve looks stable but unrealistic.",
        "type": float,
    },
    "total_workload": {
        "desc": "Objective total workload WT (total amount of work to complete).",
        "unit": "Task units (typically 2.5K ~ 15K)",
        "range": (100.0, 100000.0),
        "suggest": "Recommended 2,500 ~ 15,000; larger → higher subjective load within given T.",
        "too_small": "WT too small: task too easy, may always remain laid-back, losing comparative meaning.",
        "too_large": "WT too large: pressure rises quickly within given T, leading to failure.",
        "type": float,
    },
    "total_time": {
        "desc": "Total available time T (discrete steps, simulation x-axis length).",
        "unit": "Time steps (commonly 100)",
        "range": (10, 100000),
        "suggest": "Commonly 100; smaller → more time pressure, faster stress increase.",
        "too_small": "T too small: extreme time shortage, W(t) rises quickly, efficiency collapses.",
        "too_large": "T too large: time too relaxed, harder to show capacity/fatigue boundaries.",
        "type": int,
    },
    "delta_tau": {
        "desc": "Time step Δτ (real time width represented by each step).",
        "unit": "Proportion factor in same unit as T (>0)",
        "range": (1e-6, 1e6),
        "suggest": "Should match T; too large → cumulative output too coarse, too small → higher computational cost.",
        "too_small": "Δτ too small: cumulative efficiency updates too slow, stable but costly.",
        "too_large": "Δτ too large: cumulative output too coarse, completion time t* unstable.",
        "type": float,
    },
}

HELP_BANNER = """
--------------------------------------------------
Each parameter comes with meaning, typical range, and consequences of being too large/small.
"""

def _coerce_type_like(value_str: str, spec_type: type, default_val: Any) -> Tuple[bool, Any]:
    """
    Convert string input to the specified type.
    Return (ok, value):
      - ok=False: parsing failed → caller should re-prompt user
      - ok=True: parsing succeeded; value is converted value
    Empty string means "keep default value".
    """
    if value_str == "":
        return True, default_val
    try:
        if spec_type is bool:
            lowered = value_str.strip().lower()
            if lowered in {"true", "t", "1", "y", "yes"}:
                return True, True
            if lowered in {"false", "f", "0", "n", "no"}:
                return True, False
            raise ValueError("invalid bool")
        return True, spec_type(value_str)
    except Exception:
        return False, default_val

def _validate_range(key: str, value: Any) -> Tuple[bool, Optional[str]]:
    """
    Check if value is within suggested range. Return (in_range, warn_msg).
    If in_range=False, warn_msg is returned (for warning and user choice).
    """
    spec = PARAM_SPECS.get(key)
    if not spec or "range" not in spec:
        return True, None
    lo, hi = spec["range"]
    try:
        v = float(value)
        if v < lo:
            return False, f"⚠️ {key}={value} below suggested range [{lo}, {hi}]. {spec.get('too_small','')}"
        if v > hi:
            return False, f"⚠️ {key}={value} above suggested range [{lo}, {hi}]. {spec.get('too_large','')}"
        return True, None
    except Exception:
        return True, None  # Non-numeric values not checked

def _print_param_help(key: str, default_val: Any) -> None:
    """Print detailed description and suggested range of a single parameter."""
    spec = PARAM_SPECS.get(key, {})
    desc = spec.get("desc", "(no description)")
    unit = spec.get("unit", "")
    sugg = spec.get("suggest", "")
    rng = spec.get("range", None)
    rng_txt = f"[{rng[0]}, {rng[1]}]" if isinstance(rng, tuple) else "(not specified)"
    print(f"""
— Parameter: {key}
  Description: {desc}
  Unit/Range: {unit}
  Suggested Range: {rng_txt}
  Suggested Values: {sugg}
  Default: {default_val}
(Enter a value; or type 'h'/'?' for help, press Enter to keep default)
""")

def start_console_app() -> None:
    """
    Console interaction entry: with help, validation, and retry mechanism.
    """
    default_params: Dict[str, Any] = get_default_params()

    print("""🎉 Welcome to the WorkLord Workload Simulation Toolbox
--------------------------------------------------
You can choose to use default parameters or input your own.

Note: During input, type 'h' or '?' to view detailed info for each parameter, 
otherwise enter 'y' to directly use defaults.
""")
    choice = input("Use default parameters? (y/n): ").strip().lower()

    if choice == 'y':
        print("\n✅ Using default parameters:")
        for k, v in default_params.items():
            print(f"  {k}: {v}")
        logger.info("Using default params: %s", default_params)
        run_simulation(**default_params)
        return

    print(HELP_BANNER)
    print("\n🛠️ Start entering custom parameters (press Enter to keep default; invalid input will re-prompt):")

    user_params: Dict[str, Any] = {}
    for key, default in default_params.items():
        spec = PARAM_SPECS.get(key, {})
        spec_type = spec.get("type", type(default))
        # Short inline hint
        if spec:
            brief = spec.get("desc", "")
            suggest = spec.get("suggest", "")
            rng = spec.get("range", None)
            rng_txt = f"[{rng[0]}, {rng[1]}]" if isinstance(rng, tuple) else "(not specified)"
            print(f"\n➡ {key}: {brief} | Suggested range: {rng_txt} | {suggest}")

        while True:
            raw = input(f"Enter {key} (default {default}): ").strip()
            if raw.lower() in {"h", "?", "help"}:
                _print_param_help(key, default)
                continue

            ok, val = _coerce_type_like(raw, spec_type, default)
            if not ok:
                print("❌ Invalid input format, please try again (or press Enter to use default).")
                continue  # retry

            # Range validation: warn if out of range and ask user to confirm
            in_range, warn = _validate_range(key, val)
            if not in_range and warn:
                print(warn)
                logger.warning(warn)
                ans = input("Still use this value? (y=use / n=re-enter, default n): ").strip().lower()
                if ans != "y":
                    continue  # re-enter

            user_params[key] = val
            break  # parameter accepted

    final_params = {**default_params, **user_params}

    print("\n📦 Final parameters in use:")
    for k, v in final_params.items():
        print(f"  {k}: {v}")
    logger.info("Using final params: %s", final_params)

    run_simulation(**final_params)
