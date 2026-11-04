"""SQLAlchemy ORM models for forecast metadata and cache tracking."""

from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ForecastRun(Base):
    """Tracks a retrieved ECMWF forecast run."""
    __tablename__ = "forecast_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(16))           # "ifs" | "aifs"
    init_date: Mapped[str] = mapped_column(String(10))        # "YYYY-MM-DD"
    init_cycle: Mapped[int] = mapped_column(Integer)          # 0, 6, 12, 18
    resolution: Mapped[str] = mapped_column(String(8))        # "0p25" | "0p1"
    parameters: Mapped[str] = mapped_column(Text)             # comma-separated param list
    max_step: Mapped[int] = mapped_column(Integer)            # max forecast hour
    file_path: Mapped[str] = mapped_column(Text)             # local cache file
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class LocationFavorite(Base):
    """User-saved locations for quick forecast access."""
    __tablename__ = "location_favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    state: Mapped[str] = mapped_column(String(64), nullable=True)
    district: Mapped[str] = mapped_column(String(64), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
