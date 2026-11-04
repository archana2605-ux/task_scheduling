"""Model comparison API router — IFS vs AIFS side-by-side."""

from __future__ import annotations
import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
import numpy as np

from app.services.ecmwf_client import ecmwf_client, ECMWFDataUnavailableError, MODEL_CONFIG
from app.services.forecast_service import forecast_service
from app.schemas import ModelComparisonResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/comparison", tags=["model-comparison"])


@router.get("/", response_model=ModelComparisonResponse)
async def compare_models(
    lat: float = Query(20.5937, ge=6.0, le=38.0),
    lon: float = Query(78.9629, ge=68.0, le=98.0),
    max_step: int = Query(72, ge=6, le=240),
    ifs_date: Optional[str] = Query(None),
    ifs_cycle: Optional[int] = Query(None, ge=0, le=18),
    aifs_date: Optional[str] = Query(None),
    aifs_cycle: Optional[int] = Query(None, ge=0, le=18),
):
    """
    Compare IFS and AIFS rainfall forecasts for the same location.
    Returns both forecasts plus difference metrics.

    Note: IFS and AIFS are independent forecasting systems. We compare
    comparable init times but acknowledge they may differ.
    """
    notes = []
    ifs_result = None
    aifs_result = None
    errors = []

    # Fetch IFS
    try:
        ifs_data = await forecast_service.get_location_forecast(
            latitude=lat, longitude=lon,
            model="ifs", date=ifs_date, cycle=ifs_cycle, max_step=max_step,
        )
        ifs_result = ifs_data["forecast"]
    except ECMWFDataUnavailableError as e:
        errors.append(f"IFS: {e}")
        notes.append("IFS data not available for comparison.")
    except Exception as e:
        errors.append(f"IFS processing error: {e}")

    # Fetch AIFS
    try:
        aifs_data = await forecast_service.get_location_forecast(
            latitude=lat, longitude=lon,
            model="aifs", date=aifs_date, cycle=aifs_cycle, max_step=max_step,
        )
        aifs_result = aifs_data["forecast"]
    except ECMWFDataUnavailableError as e:
        errors.append(f"AIFS: {e}")
        notes.append("AIFS data not available for comparison.")
    except Exception as e:
        errors.append(f"AIFS processing error: {e}")

    # Compute comparison metrics if both available
    max_diff = None
    mean_diff = None
    comparison_valid = False

    if ifs_result and aifs_result:
        ifs_init = ifs_result.metadata.init_datetime
        aifs_init = aifs_result.metadata.init_datetime

        if ifs_init != aifs_init:
            notes.append(
                f"WARNING: Comparing mismatched init times — "
                f"IFS: {ifs_init}, AIFS: {aifs_init}. "
                "Results represent forecasts from different model runs."
            )

        # Find matching steps
        ifs_steps = {s.step_hours: s.incremental_mm for s in ifs_result.steps}
        aifs_steps = {s.step_hours: s.incremental_mm for s in aifs_result.steps}
        common_steps = sorted(set(ifs_steps.keys()) & set(aifs_steps.keys()))

        if common_steps:
            diffs = [ifs_steps[s] - aifs_steps[s] for s in common_steps]
            max_diff = round(max(abs(d) for d in diffs), 4)
            mean_diff = round(float(np.mean(diffs)), 4)
            comparison_valid = True
            notes.append(
                f"Compared {len(common_steps)} matching forecast steps "
                f"({min(common_steps)}–{max(common_steps)}h)."
            )
            notes.append(
                "IFS uses a physics-based numerical weather prediction model. "
                "AIFS uses machine learning. They are independent systems."
            )
        else:
            notes.append("No matching forecast steps found between IFS and AIFS.")

    if errors:
        notes.extend(errors)

    return ModelComparisonResponse(
        ifs=ifs_result,
        aifs=aifs_result,
        comparison_valid=comparison_valid,
        notes=notes,
        max_diff_mm=max_diff,
        mean_diff_mm=mean_diff,
    )


@router.get("/info")
async def get_model_info():
    """Return factual information about IFS and AIFS models."""
    return {
        "models": {
            "IFS": {
                "full_name": "Integrated Forecasting System",
                "type": "Numerical Weather Prediction (NWP)",
                "developer": "ECMWF",
                "resolution": "0.25° global (open data)",
                "cycles": [0, 6, 12, 18],
                "max_lead_time_hours": 240,
                "description": (
                    "Physics-based NWP model using spectral methods. "
                    "Gold standard for medium-range weather forecasting."
                ),
            },
            "AIFS": {
                "full_name": "Artificial Intelligence / Integrated Forecasting System",
                "type": "Machine Learning Weather Model",
                "developer": "ECMWF",
                "resolution": "0.25° global",
                "cycles": [0, 6, 12, 18],
                "max_lead_time_hours": 360,
                "description": (
                    "Data-driven ML forecasting system. Trained on ERA5 reanalysis. "
                    "Significantly faster than IFS but uses IFS for initial conditions."
                ),
            },
        },
        "note": (
            "RainCast AI retrieves operational ECMWF open data forecasts. "
            "It does not train or modify these models."
        ),
    }
