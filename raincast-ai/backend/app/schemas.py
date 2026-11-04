"""Pydantic schemas for API request/response validation."""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ─── Forecast Models ────────────────────────────────────────────────────────

class ForecastRequest(BaseModel):
    model: str = Field("ifs", pattern="^(ifs|aifs)$")
    date: Optional[str] = None          # "YYYY-MM-DD", defaults to latest
    cycle: Optional[int] = None         # 0, 6, 12, 18 — defaults to latest
    parameters: List[str] = ["tp"]
    max_step: int = Field(72, ge=0, le=240)
    resolution: Optional[str] = None   # "0p25" | "0p1"


class PrecipitationStep(BaseModel):
    step_hours: int
    valid_time: datetime
    accumulated_mm: float       # Cumulative from init
    incremental_mm: float       # Rain in this period only
    accumulation_period_h: int  # Hours this increment covers


class GridPoint(BaseModel):
    latitude: float
    longitude: float
    value: float


class ForecastMetadata(BaseModel):
    model: str
    init_date: str
    init_cycle: int
    init_datetime: str
    resolution_deg: float
    max_step_hours: int
    retrieved_at: str
    parameters: List[str]
    source: str = "ECMWF Open Data"


class RainfallForecast(BaseModel):
    metadata: ForecastMetadata
    steps: List[PrecipitationStep]
    total_24h_mm: float
    total_48h_mm: float
    total_72h_mm: float
    max_step_mm: float
    mean_mm: float


class GridForecast(BaseModel):
    metadata: ForecastMetadata
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
    lat_resolution: float
    lon_resolution: float
    latitudes: List[float]
    longitudes: List[float]
    # step -> list of grid values (flattened row-major)
    rainfall_mm: Dict[str, List[float]]
    units: str = "mm"


# ─── Location ────────────────────────────────────────────────────────────────

class LocationQuery(BaseModel):
    name: str
    latitude: float
    longitude: float
    state: Optional[str] = None
    district: Optional[str] = None


class LocationForecastResponse(BaseModel):
    location: LocationQuery
    forecast: RainfallForecast
    temperature_2m_c: Optional[List[Dict[str, Any]]] = None
    relative_humidity: Optional[List[Dict[str, Any]]] = None


# ─── Model Comparison ────────────────────────────────────────────────────────

class ModelComparisonResponse(BaseModel):
    ifs: Optional[RainfallForecast] = None
    aifs: Optional[RainfallForecast] = None
    comparison_valid: bool
    notes: List[str] = []
    max_diff_mm: Optional[float] = None
    mean_diff_mm: Optional[float] = None


# ─── Analytics ───────────────────────────────────────────────────────────────

class RegionalStats(BaseModel):
    region: str
    mean_mm: float
    max_mm: float
    min_mm: float
    std_mm: float
    heavy_rain_pct: float   # % grid cells > 64.5 mm
    total_mm: float


class ForecastSummary(BaseModel):
    model: str
    init_datetime: str
    india_mean_mm: float
    india_max_mm: float
    heavy_rain_grid_cells: int
    total_grid_cells: int
    retrieved_at: str
    is_fresh: bool
    data_available: bool
    error_message: Optional[str] = None


# ─── Status ──────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    ecmwf_accessible: bool
    latest_ifs_run: Optional[str] = None
    latest_aifs_run: Optional[str] = None
    cache_entries: int = 0
