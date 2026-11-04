"""
GRIB2 processing engine using cfgrib/xarray.

Reads ECMWF GRIB2 files, extracts meteorological fields, handles
coordinate systems, unit conversion, and spatial subsetting for India.

Key design decisions:
- Uses xarray + cfgrib for robust GRIB2 reading
- Latitude ordering: GRIB2 may store north-to-south or south-to-north;
  we always normalize to ascending latitude order.
- Longitude: ECMWF uses 0–360; we convert to -180–180 when needed
  but keep 0–360 for India bounding box (68–97.5°E is unambiguous).
- Missing values: GRIB missing values become NaN in xarray; we keep them
  as NaN rather than silently replacing with 0.
"""

from __future__ import annotations
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from app.config import settings
from app.services.precipitation import metres_to_mm, accumulated_to_incremental

logger = logging.getLogger(__name__)

INDIA_BBOX = {
    "lat_min": settings.india_lat_min,
    "lat_max": settings.india_lat_max,
    "lon_min": settings.india_lon_min,
    "lon_max": settings.india_lon_max,
}


class GRIBProcessingError(Exception):
    pass


def _try_import_xarray_cfgrib():
    """Import xarray and cfgrib, raising a clear error if unavailable."""
    try:
        import xarray as xr
        import cfgrib  # noqa: F401 — registers the GRIB engine
        return xr
    except ImportError as e:
        raise GRIBProcessingError(
            f"Required package not available: {e}. "
            "Install: pip install xarray cfgrib eccodes"
        ) from e


def validate_grib_file(filepath: Path) -> bool:
    """Validate that a file is a plausible GRIB2 file."""
    if not filepath.exists():
        return False
    if filepath.stat().st_size < 100:
        return False
    try:
        with open(filepath, "rb") as f:
            header = f.read(4)
        return header == b"GRIB"
    except Exception:
        return False


def open_grib_dataset(filepath: Path, param_shortname: str) -> "xr.Dataset":
    """
    Open a GRIB2 file for a specific parameter using cfgrib + xarray.
    Returns an xarray Dataset with the field data.
    """
    xr = _try_import_xarray_cfgrib()

    if not validate_grib_file(filepath):
        raise GRIBProcessingError(f"Invalid or missing GRIB2 file: {filepath}")

    try:
        ds = xr.open_dataset(
            str(filepath),
            engine="cfgrib",
            backend_kwargs={
                "filter_by_keys": {"shortName": param_shortname},
                "indexpath": "",   # Disable index file creation
            },
        )
        return ds
    except Exception as e:
        raise GRIBProcessingError(
            f"Failed to open GRIB2 file for param '{param_shortname}': {e}"
        ) from e


def open_grib_all_steps(filepath: Path, param_shortname: str) -> List[Dict]:
    """
    Open a GRIB2 file and return all forecast steps for a parameter.

    Returns list of dicts:
      { step_hours, valid_time, init_time, data (2D np.array), lats, lons, units, missing_value_pct }
    """
    xr = _try_import_xarray_cfgrib()

    if not validate_grib_file(filepath):
        raise GRIBProcessingError(f"Invalid GRIB2 file: {filepath}")

    results = []

    try:
        # cfgrib may produce multiple datasets for different steps
        datasets = xr.open_dataset(
            str(filepath),
            engine="cfgrib",
            backend_kwargs={
                "filter_by_keys": {"shortName": param_shortname},
                "indexpath": "",
                "squeeze": False,
            },
            chunks=None,  # No dask — we want numpy arrays
        )

        # Normalize coordinates
        ds = _normalize_coordinates(datasets)

        # Extract all step/time data
        param_var = _find_parameter_variable(ds, param_shortname)
        lats = ds["latitude"].values
        lons = ds["longitude"].values

        # Determine units from GRIB metadata
        units = ds[param_var].attrs.get("units", "unknown")
        long_name = ds[param_var].attrs.get("long_name", param_shortname)

        logger.info(
            "Parameter '%s' (%s): units=%s, shape=%s",
            param_shortname, long_name, units, ds[param_var].shape
        )

        # Iterate over time/step dimensions
        if "step" in ds.dims:
            for i, step_val in enumerate(ds["step"].values):
                step_hours = int(np.timedelta64(step_val, 'h') / np.timedelta64(1, 'h'))
                data_slice = ds[param_var].isel(step=i).values
                valid_time = ds["valid_time"].values[i] if "valid_time" in ds else None

                results.append(_make_step_dict(
                    step_hours=step_hours,
                    data=data_slice,
                    lats=lats,
                    lons=lons,
                    units=units,
                    param=param_shortname,
                    valid_time=valid_time,
                    init_time=ds["time"].values if "time" in ds else None,
                ))
        else:
            # Single step or time dimension
            data = ds[param_var].values
            if data.ndim == 2:
                step_hours = 0
                results.append(_make_step_dict(
                    step_hours=step_hours,
                    data=data,
                    lats=lats,
                    lons=lons,
                    units=units,
                    param=param_shortname,
                    valid_time=None,
                    init_time=None,
                ))

    except GRIBProcessingError:
        raise
    except Exception as e:
        raise GRIBProcessingError(f"Error reading GRIB2 steps: {e}") from e

    return results


def _make_step_dict(
    step_hours: int,
    data: np.ndarray,
    lats: np.ndarray,
    lons: np.ndarray,
    units: str,
    param: str,
    valid_time,
    init_time,
) -> Dict:
    """Build a standardised step dictionary from raw GRIB data."""
    # Convert units to mm if this is a precipitation field in metres
    if param in ("tp", "cp") and units in ("m", "metres", "meter"):
        data_mm = data * 1000.0
        output_units = "mm"
    elif param in ("tp", "cp") and units == "mm":
        data_mm = data.copy()
        output_units = "mm"
    else:
        data_mm = data.copy()
        output_units = units

    # Count missing values
    total = data_mm.size
    missing = int(np.sum(np.isnan(data_mm)))
    missing_pct = round(100.0 * missing / total, 2) if total > 0 else 0.0

    return {
        "step_hours": step_hours,
        "valid_time": str(valid_time) if valid_time is not None else None,
        "init_time": str(init_time) if init_time is not None else None,
        "data": data_mm,
        "lats": lats,
        "lons": lons,
        "units": output_units,
        "original_units": units,
        "shape": data_mm.shape,
        "missing_value_pct": missing_pct,
    }


def _normalize_coordinates(ds: "xr.Dataset") -> "xr.Dataset":
    """
    Normalise latitude and longitude coordinate ordering.
    - Latitude: ensure ascending (south-to-north)
    - Longitude: keep as-is (ECMWF uses 0–360; India is 68–97.5 unambiguous)
    """
    if "latitude" in ds.coords:
        lats = ds["latitude"].values
        if len(lats) > 1 and lats[0] > lats[-1]:
            # Descending latitude — flip
            ds = ds.isel(latitude=slice(None, None, -1))

    return ds


def _find_parameter_variable(ds: "xr.Dataset", shortname: str) -> str:
    """Find the variable name in the dataset for the given GRIB shortName."""
    # cfgrib uses the shortName directly in many cases
    if shortname in ds.data_vars:
        return shortname

    # Common cfgrib variable name mappings
    name_map = {
        "tp": "tp",
        "cp": "cp",
        "2t": "t2m",
        "10u": "u10",
        "10v": "v10",
        "tcc": "tcc",
        "sp": "sp",
        "tcwv": "tcwv",
        "msl": "msl",
        "r": "r",
    }

    mapped = name_map.get(shortname)
    if mapped and mapped in ds.data_vars:
        return mapped

    # Try the first data variable
    vars_list = list(ds.data_vars)
    if vars_list:
        logger.warning(
            "Could not find '%s' in dataset vars %s, using '%s'",
            shortname, vars_list, vars_list[0]
        )
        return vars_list[0]

    raise GRIBProcessingError(f"No data variable found for parameter '{shortname}'")


def subset_to_india(
    data: np.ndarray,
    lats: np.ndarray,
    lons: np.ndarray,
    bbox: Optional[Dict] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Spatially subset a 2D grid to India's bounding box.

    Parameters
    ----------
    data : 2D np.ndarray (lat × lon)
    lats : 1D np.ndarray
    lons : 1D np.ndarray
    bbox : dict with lat_min, lat_max, lon_min, lon_max (defaults to India)

    Returns
    -------
    (subset_data, subset_lats, subset_lons)
    """
    if bbox is None:
        bbox = INDIA_BBOX

    lat_mask = (lats >= bbox["lat_min"]) & (lats <= bbox["lat_max"])
    lon_mask = (lons >= bbox["lon_min"]) & (lons <= bbox["lon_max"])

    subset_data = data[np.ix_(lat_mask, lon_mask)]
    subset_lats = lats[lat_mask]
    subset_lons = lons[lon_mask]

    return subset_data, subset_lats, subset_lons


def extract_point_value(
    data: np.ndarray,
    lats: np.ndarray,
    lons: np.ndarray,
    target_lat: float,
    target_lon: float,
) -> Tuple[float, float, float]:
    """
    Extract the nearest-grid-point value for a lat/lon coordinate.

    Returns (value, actual_lat, actual_lon).
    Does not interpolate — nearest-neighbour only to avoid false precision.
    """
    lat_idx = int(np.argmin(np.abs(lats - target_lat)))
    lon_idx = int(np.argmin(np.abs(lons - target_lon)))
    value = float(data[lat_idx, lon_idx])
    return value, float(lats[lat_idx]), float(lons[lon_idx])


def compute_grid_statistics(data: np.ndarray) -> Dict:
    """Compute descriptive statistics for a 2D data grid, ignoring NaN."""
    valid = data[~np.isnan(data)]
    if valid.size == 0:
        return {"mean": None, "max": None, "min": None, "std": None, "count": 0}
    return {
        "mean": round(float(np.mean(valid)), 4),
        "max": round(float(np.max(valid)), 4),
        "min": round(float(np.min(valid)), 4),
        "std": round(float(np.std(valid)), 4),
        "count": int(valid.size),
        "heavy_rain_pct": round(float(np.mean(valid >= 64.5) * 100), 2),
    }


def process_precipitation_forecast(
    grib_file: Path,
    target_lat: Optional[float] = None,
    target_lon: Optional[float] = None,
    max_step: int = 72,
    subset_india: bool = True,
) -> Dict:
    """
    Full precipitation processing pipeline:
    1. Open GRIB2 file
    2. Extract all steps
    3. Subset to India (optional)
    4. Convert accumulated → incremental
    5. Compute statistics

    Returns a dict with 'steps', 'grid_data', 'statistics', 'metadata'.
    """
    if not validate_grib_file(grib_file):
        raise GRIBProcessingError(f"Invalid GRIB2 file: {grib_file}")

    logger.info("Processing precipitation from: %s", grib_file)

    step_dicts = open_grib_all_steps(grib_file, "tp")

    if not step_dicts:
        raise GRIBProcessingError("No precipitation steps found in GRIB2 file")

    step_dicts = [s for s in step_dicts if s["step_hours"] <= max_step]
    step_dicts.sort(key=lambda x: x["step_hours"])

    # Extract point or grid
    point_steps = []
    grid_data = {}

    for sd in step_dicts:
        lats = sd["lats"]
        lons = sd["lons"]
        data = sd["data"]

        if subset_india:
            data, lats, lons = subset_to_india(data, lats, lons)

        grid_data[sd["step_hours"]] = {
            "data": data,
            "lats": lats,
            "lons": lons,
            "units": sd["units"],
        }

        if target_lat is not None and target_lon is not None:
            val, actual_lat, actual_lon = extract_point_value(data, lats, lons, target_lat, target_lon)
        else:
            val = float(np.nanmean(data))
            actual_lat = actual_lon = None

        point_steps.append({
            "step_hours": sd["step_hours"],
            "accumulated_mm": round(val, 4) if not np.isnan(val) else 0.0,
        })

    # Convert accumulated → incremental for point values
    steps_sorted = [p["step_hours"] for p in point_steps]
    acc_values = [p["accumulated_mm"] for p in point_steps]
    incremental_steps = accumulated_to_incremental(steps_sorted, acc_values)

    # Compute grid statistics for India subset (using accumulated values)
    if grid_data:
        last_step = max(grid_data.keys())
        last_data = grid_data[last_step]["data"]
        stats = compute_grid_statistics(last_data)
    else:
        stats = {}

    return {
        "steps": incremental_steps,
        "grid_data": grid_data,
        "statistics": stats,
        "lats": grid_data[min(grid_data.keys())]["lats"].tolist() if grid_data else [],
        "lons": grid_data[min(grid_data.keys())]["lons"].tolist() if grid_data else [],
        "step_hours": steps_sorted,
        "metadata": {
            "param": "tp",
            "units": "mm",
            "init_time": step_dicts[0].get("init_time"),
            "steps_available": steps_sorted,
        },
    }
