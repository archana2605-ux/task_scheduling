"""Location search and point-forecast API router."""

from __future__ import annotations
import logging
import csv
import io
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.data.india_locations import search_locations, INDIA_CITIES, INDIA_STATES
from app.services.ecmwf_client import ecmwf_client, ECMWFDataUnavailableError
from app.services.forecast_service import forecast_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/search")
async def search_india_locations(
    q: str = Query(..., min_length=1, description="City/state/district name"),
    limit: int = Query(10, ge=1, le=50),
):
    """Search India cities, districts, and states."""
    results = search_locations(q, limit)
    return {"query": q, "results": results, "count": len(results)}


@router.get("/states")
async def list_states():
    """List all Indian states."""
    return {"states": INDIA_STATES}


@router.get("/cities")
async def list_cities(
    state: Optional[str] = Query(None, description="Filter by state name"),
    limit: int = Query(50, ge=1, le=200),
):
    """List Indian cities, optionally filtered by state."""
    cities = INDIA_CITIES
    if state:
        state_lower = state.lower()
        cities = [c for c in cities if c["state"].lower() == state_lower]
    return {"cities": cities[:limit], "count": len(cities[:limit])}


@router.get("/forecast")
async def get_location_forecast(
    lat: float = Query(..., ge=6.0, le=38.0, description="Latitude"),
    lon: float = Query(..., ge=68.0, le=98.0, description="Longitude"),
    model: str = Query("ifs", pattern="^(ifs|aifs)$"),
    date: Optional[str] = Query(None),
    cycle: Optional[int] = Query(None, ge=0, le=18),
    max_step: int = Query(72, ge=6, le=240),
):
    """
    Get point rainfall forecast for a specific lat/lon coordinate.
    Downloads and processes ECMWF data for the nearest grid point.
    """
    try:
        result = await forecast_service.get_location_forecast(
            latitude=lat,
            longitude=lon,
            model=model,
            date=date,
            cycle=cycle,
            max_step=max_step,
        )
        return {
            "location": {"latitude": lat, "longitude": lon},
            "forecast": result["forecast"],
            "statistics": result.get("statistics"),
        }
    except ECMWFDataUnavailableError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ECMWF data unavailable: {e}"
        )
    except Exception as e:
        logger.error("Location forecast error: %s", e)
        raise HTTPException(status_code=500, detail=f"Forecast processing failed: {e}")


@router.get("/forecast/csv")
async def export_location_forecast_csv(
    lat: float = Query(..., ge=6.0, le=38.0),
    lon: float = Query(..., ge=68.0, le=98.0),
    model: str = Query("ifs", pattern="^(ifs|aifs)$"),
    max_step: int = Query(72, ge=6, le=240),
    location_name: str = Query("", description="Optional location name for CSV header"),
):
    """Export location forecast as CSV download."""
    try:
        result = await forecast_service.get_location_forecast(
            latitude=lat, longitude=lon,
            model=model, max_step=max_step,
        )
    except ECMWFDataUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    forecast = result["forecast"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "# RainCast AI — Forecast Export",
        f"Model: {forecast.metadata.model}",
        f"Init: {forecast.metadata.init_datetime}",
        f"Location: {location_name or f'{lat:.4f}N, {lon:.4f}E'}",
    ])
    writer.writerow([])
    writer.writerow([
        "Step (hours)", "Valid Time", "Incremental Rain (mm)",
        "Accumulated Rain (mm)", "Period (hours)", "Intensity Category"
    ])

    from app.services.precipitation import classify_rainfall_intensity
    for step in forecast.steps:
        writer.writerow([
            step.step_hours,
            step.valid_time,
            round(step.incremental_mm, 2),
            round(step.accumulated_mm, 2),
            step.accumulation_period_h,
            classify_rainfall_intensity(step.incremental_mm),
        ])

    output.seek(0)
    filename = f"raincast_{model}_{lat:.2f}N_{lon:.2f}E.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
