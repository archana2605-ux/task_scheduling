"""Application configuration using Pydantic Settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    app_name: str = "RainCast AI"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")

    # Database
    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR}/raincast.db",
        env="DATABASE_URL"
    )

    # Cache
    cache_dir: Path = Field(default=BASE_DIR / "cache", env="CACHE_DIR")
    cache_ttl_hours: int = Field(default=6, env="CACHE_TTL_HOURS")

    # ECMWF
    ecmwf_timeout_seconds: int = Field(default=300, env="ECMWF_TIMEOUT")
    ecmwf_max_retries: int = Field(default=3, env="ECMWF_MAX_RETRIES")
    ecmwf_retry_delay: float = Field(default=5.0, env="ECMWF_RETRY_DELAY")

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        env="CORS_ORIGINS"
    )

    # India bounding box (default spatial extent)
    india_lat_min: float = 6.5
    india_lat_max: float = 37.5
    india_lon_min: float = 68.0
    india_lon_max: float = 97.5

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Ensure cache directory exists
settings.cache_dir.mkdir(parents=True, exist_ok=True)
