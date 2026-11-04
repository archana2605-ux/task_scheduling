"""Analytics and regional statistics router."""

from __future__ import annotations
import logging
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
import numpy as np

from app.services.ecmwf_client import ecmwf_client
from app.services.precipitation import classify_rainfall_intensity, classify_grid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/rainfall-categories")
async def get_rainfall_categories():
    """Return IMD rainfall intensity classification thresholds."""
    return {
        "source": "India Meteorological Department (IMD) categories",
        "note": "These are display thresholds, not official warnings.",
        "categories": [
            {"label": "No rainfall", "min_mm": 0, "max_mm": 0, "color": "#f0f4ff"},
            {"label": "Very light", "min_mm": 0.1, "max_mm": 2.5, "color": "#b3d9ff"},
            {"label": "Light", "min_mm": 2.5, "max_mm": 15.0, "color": "#66b3ff"},
            {"label": "Moderate", "min_mm": 15.0, "max_mm": 64.5, "color": "#0080ff"},
            {"label": "Heavy", "min_mm": 64.5, "max_mm": 115.5, "color": "#0040cc"},
            {"label": "Very heavy", "min_mm": 115.5, "max_mm": 204.5, "color": "#8000ff"},
            {"label": "Extremely heavy", "min_mm": 204.5, "max_mm": None, "color": "#ff0080"},
        ],
    }


@router.get("/model-parameters")
async def get_model_parameters():
    """Return available parameters per model."""
    from app.services.ecmwf_client import MODEL_CONFIG
    return {
        model: {
            "parameters": list(cfg["parameters"].keys()),
            "cycles": cfg["cycles"],
            "resolutions": cfg["resolutions"],
        }
        for model, cfg in MODEL_CONFIG.items()
    }


@router.get("/india-regions")
async def get_india_regions():
    """Return major meteorological sub-regions of India with bounding boxes."""
    return {
        "regions": [
            {
                "name": "North India",
                "states": ["Delhi", "Uttar Pradesh", "Haryana", "Punjab", "Himachal Pradesh", "Uttarakhand"],
                "bbox": {"lat_min": 25.0, "lat_max": 36.0, "lon_min": 73.0, "lon_max": 85.0},
                "color": "#4a90d9",
            },
            {
                "name": "Northeast India",
                "states": ["Assam", "Arunachal Pradesh", "Meghalaya", "Nagaland", "Manipur", "Mizoram", "Tripura", "Sikkim"],
                "bbox": {"lat_min": 21.0, "lat_max": 29.5, "lon_min": 88.0, "lon_max": 97.5},
                "color": "#7ed321",
            },
            {
                "name": "East India",
                "states": ["West Bengal", "Bihar", "Jharkhand", "Odisha"],
                "bbox": {"lat_min": 19.0, "lat_max": 27.5, "lon_min": 83.0, "lon_max": 90.0},
                "color": "#f5a623",
            },
            {
                "name": "Central India",
                "states": ["Madhya Pradesh", "Chhattisgarh"],
                "bbox": {"lat_min": 17.5, "lat_max": 26.5, "lon_min": 74.0, "lon_max": 85.0},
                "color": "#d0021b",
            },
            {
                "name": "West India",
                "states": ["Maharashtra", "Gujarat", "Goa"],
                "bbox": {"lat_min": 14.0, "lat_max": 25.0, "lon_min": 68.0, "lon_max": 78.0},
                "color": "#9b59b6",
            },
            {
                "name": "South India",
                "states": ["Karnataka", "Tamil Nadu", "Andhra Pradesh", "Telangana", "Kerala"],
                "bbox": {"lat_min": 6.5, "lat_max": 18.5, "lon_min": 74.0, "lon_max": 82.0},
                "color": "#1abc9c",
            },
            {
                "name": "Northwest India",
                "states": ["Rajasthan", "Jammu & Kashmir", "Ladakh"],
                "bbox": {"lat_min": 23.0, "lat_max": 36.5, "lon_min": 68.0, "lon_max": 78.5},
                "color": "#e67e22",
            },
        ]
    }
