"""
Precipitation conversion utilities.

ECMWF total precipitation (tp) is a CUMULATIVE field:
  - It accumulates from forecast step 0 (init time).
  - Each step value represents total rain since init, in metres.
  - To get rain in a specific period, subtract consecutive steps.

Convention:
  incremental[n] = accumulated[n] - accumulated[n-1]  for n > 0
  incremental[0] = accumulated[0]                      (usually ~0)

Unit conversion: metres → millimetres (multiply by 1000).

This module contains all accumulation-to-incremental logic, including
edge-case handling (negatives, missing steps, resets).
"""

from __future__ import annotations
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def metres_to_mm(value_m: float | np.ndarray) -> float | np.ndarray:
    """Convert metres of water equivalent to millimetres."""
    return np.asarray(value_m) * 1000.0


def accumulated_to_incremental(
    steps: List[int],
    accumulated_mm: List[float],
    allow_small_negative: float = -0.01,
) -> List[Dict]:
    """
    Convert a list of (step, accumulated_mm) pairs into incremental values.

    Parameters
    ----------
    steps : list of int
        Forecast hours (must be sorted ascending).
    accumulated_mm : list of float
        Corresponding accumulated precipitation values in mm.
    allow_small_negative : float
        Tolerance for floating-point rounding errors (mm). Differences
        below this threshold are clamped to 0 rather than flagged as errors.

    Returns
    -------
    list of dict with keys:
        step_hours, valid_hour_start, valid_hour_end,
        accumulated_mm, incremental_mm, accumulation_period_h, warning
    """
    if len(steps) != len(accumulated_mm):
        raise ValueError("steps and accumulated_mm must have the same length")

    if not steps:
        return []

    # Sort by step
    pairs = sorted(zip(steps, accumulated_mm), key=lambda x: x[0])
    sorted_steps, sorted_acc = zip(*pairs)
    sorted_steps = list(sorted_steps)
    sorted_acc = list(sorted_acc)

    results = []

    for i, (step, acc) in enumerate(zip(sorted_steps, sorted_acc)):
        if i == 0:
            prev_step = 0
            prev_acc = 0.0
            if step == 0:
                # Step 0 is always zero or near-zero (no rain yet)
                incremental = max(0.0, acc)
                period_h = 0
            else:
                # First step > 0: treat accumulated as incremental for this period
                incremental = max(0.0, acc)
                period_h = step
        else:
            prev_step = sorted_steps[i - 1]
            prev_acc = sorted_acc[i - 1]
            period_h = step - prev_step
            diff = acc - prev_acc

            if diff < allow_small_negative:
                logger.warning(
                    "Negative precipitation increment at step %d→%d: %.4f mm. "
                    "This may indicate accumulation reset or bad data.",
                    prev_step, step, diff
                )
                incremental = 0.0
                warning = f"Negative increment ({diff:.4f} mm) clamped to 0"
            elif diff < 0:
                # Very small negative — likely floating-point noise
                incremental = 0.0
                warning = None
            else:
                incremental = diff
                warning = None

        results.append({
            "step_hours": step,
            "valid_hour_start": prev_step if i > 0 else 0,
            "valid_hour_end": step,
            "accumulated_mm": round(acc, 4),
            "incremental_mm": round(incremental, 4),
            "accumulation_period_h": period_h,
            "warning": warning if i > 0 else None,
        })

    return results


def accumulated_grid_to_incremental(
    step_data: Dict[int, np.ndarray],
) -> Dict[int, np.ndarray]:
    """
    Convert a dict of {step: 2D array of accumulated mm}
    into incremental arrays for each step.

    Parameters
    ----------
    step_data : dict
        Keys are forecast hours (int). Values are 2D NumPy arrays (mm).

    Returns
    -------
    dict
        Same keys, with incremental precipitation arrays.
    """
    if not step_data:
        return {}

    sorted_steps = sorted(step_data.keys())
    result = {}

    for i, step in enumerate(sorted_steps):
        current = step_data[step]
        if i == 0:
            prev = np.zeros_like(current)
        else:
            prev = step_data[sorted_steps[i - 1]]

        diff = current - prev
        # Clamp tiny negatives from rounding
        diff = np.where(diff < -0.01, np.nan, diff)
        diff = np.where(diff < 0, 0.0, diff)
        result[step] = diff

    return result


def compute_period_accumulation(
    incremental: List[Dict],
    period_hours: int,
    start_step: int = 0,
) -> float:
    """
    Sum incremental precipitation over a time window.

    Parameters
    ----------
    incremental : list of dicts from accumulated_to_incremental()
    period_hours : int
        How many forecast hours to sum (e.g. 24, 48, 72)
    start_step : int
        Starting forecast hour (default 0 = from init time)

    Returns
    -------
    float : Total mm over the period
    """
    end_step = start_step + period_hours
    total = 0.0
    for entry in incremental:
        sh = entry["step_hours"]
        if start_step < sh <= end_step:
            total += entry["incremental_mm"]
    return round(total, 2)


def classify_rainfall_intensity(mm: float) -> str:
    """
    Classify rainfall intensity using IMD categories.
    These are display classifications only, not official warnings.
    """
    if mm <= 0:
        return "No rainfall"
    elif mm < 2.5:
        return "Very light"
    elif mm < 15.0:
        return "Light"
    elif mm < 64.5:
        return "Moderate"
    elif mm < 115.5:
        return "Heavy"
    elif mm < 204.5:
        return "Very heavy"
    else:
        return "Extremely heavy"


def classify_grid(arr: np.ndarray) -> np.ndarray:
    """
    Classify a 2D rainfall array into IMD intensity categories (0–6).
    0=none, 1=very light, 2=light, 3=moderate, 4=heavy, 5=very heavy, 6=extremely heavy
    """
    categories = np.zeros_like(arr, dtype=np.int8)
    categories = np.where(arr > 0, 1, categories)
    categories = np.where(arr >= 2.5, 2, categories)
    categories = np.where(arr >= 15.0, 3, categories)
    categories = np.where(arr >= 64.5, 4, categories)
    categories = np.where(arr >= 115.5, 5, categories)
    categories = np.where(arr >= 204.5, 6, categories)
    return categories
