"""
Forecast cache and orchestration service.

Coordinates between the ECMWF client, GRIB processor, and data store.
Provides high-level forecast retrieval with graceful degradation:
- If live data download fails, returns clear error state (no fake data).
- Processes GRIB2 files only if cfgrib is available.
- Falls back to cached/sample data when explicitly enabled.
"""

from __future__ import annotations
import logging
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from app.config import settings
from app.services.ecmwf_client import ecmwf_client, ECMWFDataUnavailableError, MODEL_CONFIG
from app.services.precipitation import (
    accumulated_to_incremental,
    compute_period_accumulation,
    classify_rainfall_intensity,
    metres_to_mm,
)
from app.schemas import (
    ForecastMetadata,
    PrecipitationStep,
    RainfallForecast,
    ForecastSummary,
)

logger = logging.getLogger(__name__)


class ForecastService:
    """High-level forecast orchestration service."""

    async def get_forecast_summary(self, model: str = "ifs") -> ForecastSummary:
        """Get a quick summary of the latest available forecast."""
        try:
            date, cycle = ecmwf_client.get_latest_cycle(model)
            ecmwf_ok = await ecmwf_client.check_ecmwf_accessible()

            # Check if we have cached data
            cached = ecmwf_client.get_cached_forecast(model, date, cycle, ["tp"])
            has_data = cached is not None

            return ForecastSummary(
                model=model.upper(),
                init_datetime=f"{date}T{cycle:02d}:00Z",
                india_mean_mm=0.0,
                india_max_mm=0.0,
                heavy_rain_grid_cells=0,
                total_grid_cells=0,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                is_fresh=has_data,
                data_available=ecmwf_ok,
                error_message=None if ecmwf_ok else "ECMWF data server not accessible",
            )
        except Exception as e:
            logger.error("Error getting forecast summary: %s", e)
            return ForecastSummary(
                model=model.upper(),
                init_datetime="",
                india_mean_mm=0.0,
                india_max_mm=0.0,
                heavy_rain_grid_cells=0,
                total_grid_cells=0,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                is_fresh=False,
                data_available=False,
                error_message=str(e),
            )

    async def get_location_forecast(
        self,
        latitude: float,
        longitude: float,
        model: str = "ifs",
        date: Optional[str] = None,
        cycle: Optional[int] = None,
        max_step: int = 72,
    ) -> Dict:
        """
        Download and process a point forecast for a specific location.

        Returns processed forecast data or raises ECMWFDataUnavailableError.
        """
        # Download GRIB2
        forecast_meta = await ecmwf_client.download_forecast(
            model=model,
            date=date,
            cycle=cycle,
            parameters=["tp"],
            max_step=max_step,
        )

        grib_path = Path(forecast_meta["file_path"])

        # Process precipitation
        try:
            from app.services.grib_processor import process_precipitation_forecast
            result = process_precipitation_forecast(
                grib_file=grib_path,
                target_lat=latitude,
                target_lon=longitude,
                max_step=max_step,
                subset_india=False,  # Point extraction — no need to subset
            )
        except Exception as e:
            logger.error("GRIB processing failed: %s", e)
            raise

        # Build structured forecast response
        steps = result["steps"]
        init_date = forecast_meta["init_date"]
        init_cycle = forecast_meta["init_cycle"]
        init_dt_str = f"{init_date}T{init_cycle:02d}:00Z"

        precip_steps = []
        for s in steps:
            precip_steps.append(PrecipitationStep(
                step_hours=s["step_hours"],
                valid_time=datetime.fromisoformat(
                    f"{init_date}T{init_cycle:02d}:00:00"
                ).replace(tzinfo=timezone.utc).isoformat(),
                accumulated_mm=s["accumulated_mm"],
                incremental_mm=s["incremental_mm"],
                accumulation_period_h=s["accumulation_period_h"],
            ))

        cfg = MODEL_CONFIG[model]
        metadata = ForecastMetadata(
            model=model.upper(),
            init_date=init_date,
            init_cycle=init_cycle,
            init_datetime=init_dt_str,
            resolution_deg=0.25,
            max_step_hours=max(s["step_hours"] for s in steps) if steps else 0,
            retrieved_at=forecast_meta["retrieved_at"],
            parameters=forecast_meta["parameters"],
        )

        total_24h = compute_period_accumulation(steps, 24)
        total_48h = compute_period_accumulation(steps, 48)
        total_72h = compute_period_accumulation(steps, 72)
        all_increments = [s["incremental_mm"] for s in steps]
        max_mm = max(all_increments) if all_increments else 0.0
        mean_mm = sum(all_increments) / len(all_increments) if all_increments else 0.0

        return {
            "forecast": RainfallForecast(
                metadata=metadata,
                steps=precip_steps,
                total_24h_mm=total_24h,
                total_48h_mm=total_48h,
                total_72h_mm=total_72h,
                max_step_mm=max_mm,
                mean_mm=round(mean_mm, 4),
            ),
            "raw_steps": steps,
            "grid_data": result.get("grid_data"),
            "statistics": result.get("statistics"),
        }

    async def get_india_grid_forecast(
        self,
        model: str = "ifs",
        date: Optional[str] = None,
        cycle: Optional[int] = None,
        step_hours: int = 24,
    ) -> Dict:
        """
        Get gridded rainfall data for the India domain.
        Returns lat/lon arrays and rainfall values for map rendering.
        """
        forecast_meta = await ecmwf_client.download_forecast(
            model=model,
            date=date,
            cycle=cycle,
            parameters=["tp"],
            max_step=step_hours,
        )

        grib_path = Path(forecast_meta["file_path"])

        from app.services.grib_processor import process_precipitation_forecast
        result = process_precipitation_forecast(
            grib_file=grib_path,
            target_lat=None,
            target_lon=None,
            max_step=step_hours,
            subset_india=True,
        )

        return {
            "model": model.upper(),
            "init_date": forecast_meta["init_date"],
            "init_cycle": forecast_meta["init_cycle"],
            "step_hours": step_hours,
            "lats": result["lats"],
            "lons": result["lons"],
            "steps": result["steps"],
            "statistics": result["statistics"],
            "grid_data_available": bool(result.get("grid_data")),
        }


forecast_service = ForecastService()
