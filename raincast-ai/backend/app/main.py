"""
RainCast AI — FastAPI Application Entry Point

Production-quality ECMWF-based rainfall forecasting platform.
"""

from __future__ import annotations
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("RainCast AI starting up...")
    await init_db()
    logger.info("Database initialized.")
    logger.info("Cache directory: %s", settings.cache_dir)
    yield
    logger.info("RainCast AI shutting down.")


app = FastAPI(
    title="RainCast AI",
    description=(
        "ECMWF-Based Intelligent Rainfall Forecasting and Analysis Platform. "
        "Retrieves genuine ECMWF IFS and AIFS forecast data, processes GRIB2 files, "
        "and provides interactive rainfall analysis for India."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─── Middleware ───────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# ─── Routers ──────────────────────────────────────────────────────────────────

from app.routers import forecasts, locations, comparison, analytics

app.include_router(forecasts.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(comparison.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


# ─── Root and health endpoints ────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "RainCast AI",
        "version": settings.app_version,
        "description": "ECMWF-Based Rainfall Forecasting Platform",
        "docs": "/api/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health():
    """Health check with ECMWF connectivity probe."""
    from app.services.ecmwf_client import ecmwf_client
    ecmwf_ok = await ecmwf_client.check_ecmwf_accessible()
    cached = ecmwf_client.list_cached_forecasts()

    latest_ifs = None
    latest_aifs = None
    for c in cached:
        if c.get("model") == "ifs":
            latest_ifs = c.get("retrieved_at")
        elif c.get("model") == "aifs":
            latest_aifs = c.get("retrieved_at")

    return {
        "status": "healthy",
        "version": settings.app_version,
        "ecmwf_accessible": ecmwf_ok,
        "latest_ifs_run": latest_ifs,
        "latest_aifs_run": latest_aifs,
        "cache_entries": len(cached),
    }


# ─── Exception handlers ───────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
