"""FastAPI routers for forecast endpoints."""

from __future__ import annotations
import logging
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
import csv
import io

from app.schemas import (
    ForecastSummary,
    RainfallForecast,
    ForecastRequest,
    HealthResponse,
)
from app.services.ecmwf_client import ecmwf_client, ECMWFDataUnavailableError, MODEL_CONFIG
from app.services.forecast_service import forecast_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/forecasts", tags=["forecasts"])


@router.get("/summary", response_model=ForecastSummary)
async def get_forecast_summary(
    model: str = Query("ifs", pattern="^(ifs|aifs)$"),
):
    """Get a quick summary of the latest available forecast."""
    return await forecast_service.get_forecast_summary(model)


@router.get("/latest-cycle")
async def get_latest_cycle(
    model: str = Query("ifs", pattern="^(ifs|aifs)$"),
):
    """Discover the most recent available ECMWF forecast cycle."""
    date, cycle = ecmwf_client.get_latest_cycle(model)
    ecmwf_ok = await ecmwf_client.check_ecmwf_accessible()
    return {
        "model": model.upper(),
        "latest_date": date,
        "latest_cycle": cycle,
        "init_datetime": f"{date}T{cycle:02d}:00Z",
        "ecmwf_accessible": ecmwf_ok,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/available-steps")
async def get_available_steps(
    model: str = Query("ifs", pattern="^(ifs|aifs)$"),
    cycle: int = Query(0, ge=0, le=18),
    max_step: int = Query(72, ge=0, le=240),
):
    """Return the forecast step list available for a model/cycle combination."""
    steps = ecmwf_client.get_steps_for_cycle(model, cycle, max_step)
    return {
        "model": model.upper(),
        "cycle": cycle,
        "max_step": max_step,
        "steps": steps,
        "count": len(steps),
    }


@router.get("/available-parameters")
async def get_available_parameters(
    model: str = Query("ifs", pattern="^(ifs|aifs)$"),
):
    """Return parameters available for a given model."""
    cfg = MODEL_CONFIG[model]
    return {
        "model": model.upper(),
        "parameters": [
            {"shortname": k, "description": v}
            for k, v in cfg["parameters"].items()
        ],
        "cycles": cfg["cycles"],
        "resolutions": cfg["resolutions"],
    }


@router.get("/cache")
async def list_cached_forecasts():
    """List all cached forecast metadata."""
    cached = ecmwf_client.list_cached_forecasts()
    return {"count": len(cached), "forecasts": cached}


@router.post("/download")
async def trigger_forecast_download(
    model: str = Query("ifs", pattern="^(ifs|aifs)$"),
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    cycle: Optional[int] = Query(None, ge=0, le=18),
    max_step: int = Query(72, ge=0, le=240),
    background_tasks: BackgroundTasks = None,
):
    """
    Trigger a forecast download (non-blocking background task).
    Returns immediately with job metadata.
    """
    resolved_date, resolved_cycle = ecmwf_client.get_latest_cycle(model)
    if date is None:
        date = resolved_date
    if cycle is None:
        cycle = resolved_cycle

    # For now synchronous — in production use a task queue
    try:
        meta = await ecmwf_client.download_forecast(
            model=model,
            date=date,
            cycle=cycle,
            parameters=["tp"],
            max_step=max_step,
        )
        return {
            "status": "success",
            "model": model.upper(),
            "date": date,
            "cycle": cycle,
            "file_path": meta.get("file_path"),
            "file_size_bytes": meta.get("file_size_bytes"),
            "retrieved_at": meta.get("retrieved_at"),
        }
    except ECMWFDataUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error("Download error: %s", e)
        raise HTTPException(status_code=500, detail=f"Download failed: {e}")
