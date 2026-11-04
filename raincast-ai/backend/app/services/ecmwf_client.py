"""
ECMWF Open Data client service.

Fetches genuine ECMWF forecast data using the official ecmwf-opendata
Python client. Handles IFS and AIFS models, cycle discovery, file
caching, retries with exponential backoff, and metadata recording.

Supported parameters (subset available in ECMWF open data):
  IFS:  tp, cp, tcc, 2t, r, tcwv, sp, 10u, 10v
  AIFS: tp, 2t, 10u, 10v, msl

ECMWF open data reference:
  https://confluence.ecmwf.int/display/DAC/ECMWF+open+data
"""

from __future__ import annotations
import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# ─── ECMWF model configuration ───────────────────────────────────────────────

MODEL_CONFIG: Dict[str, Dict] = {
    "ifs": {
        "stream": "oper",
        "type": "fc",
        "resolutions": ["0p25"],
        "default_resolution": "0p25",
        "cycles": [0, 6, 12, 18],
        # Steps available in open data (subset; full range 0-240 at 0,6,12,18 UTC)
        "steps_short": list(range(0, 145, 3)),   # 0–144h every 3h
        "steps_long": list(range(0, 241, 6)),    # 0–240h every 6h (00/12 UTC)
        "parameters": {
            "tp": "total precipitation",
            "2t": "2m temperature",
            "sp": "surface pressure",
            "tcc": "total cloud cover",
            "10u": "10m U wind",
            "10v": "10m V wind",
        },
    },
    "aifs": {
        "stream": "oper",
        "type": "fc",
        "resolutions": ["0p25"],
        "default_resolution": "0p25",
        "cycles": [0, 6, 12, 18],
        "steps_short": list(range(0, 145, 6)),
        "steps_long": list(range(0, 361, 6)),
        "parameters": {
            "tp": "total precipitation",
            "2t": "2m temperature",
            "10u": "10m U wind",
            "10v": "10m V wind",
            "msl": "mean sea level pressure",
        },
    },
}

# Parameters that are cumulative accumulatons (require diff to get incremental)
CUMULATIVE_PARAMS = {"tp", "cp"}


class ECMWFDataUnavailableError(Exception):
    """Raised when no ECMWF forecast data can be found/downloaded."""


class ECMWFClient:
    """
    Service class for downloading and caching ECMWF Open Data forecasts.
    """

    def __init__(self):
        self.cache_dir = settings.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_file = self.cache_dir / "forecast_index.json"
        self._index: Dict[str, Dict] = self._load_index()

    # ─── Index helpers ───────────────────────────────────────────────────────

    def _load_index(self) -> Dict:
        if self._metadata_file.exists():
            try:
                return json.loads(self._metadata_file.read_text())
            except Exception:
                return {}
        return {}

    def _save_index(self):
        self._metadata_file.write_text(json.dumps(self._index, indent=2, default=str))

    def _cache_key(self, model: str, date: str, cycle: int, params: List[str], step: int) -> str:
        raw = f"{model}:{date}:{cycle:02d}:{','.join(sorted(params))}:{step}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    # ─── Cycle discovery ─────────────────────────────────────────────────────

    def get_latest_cycle(self, model: str = "ifs") -> Tuple[str, int]:
        """
        Discover the most recent available forecast init cycle.
        ECMWF open data has ~6–8 hour lag after init time.

        Returns (date_str YYYY-MM-DD, cycle_hour 0|6|12|18)
        """
        now_utc = datetime.now(timezone.utc)
        # Data availability lag: typically 6h after init for IFS, ~8h for AIFS
        lag_hours = 7 if model == "aifs" else 6
        available_cutoff = now_utc - timedelta(hours=lag_hours)

        # Find the most recent cycle before the cutoff
        cycle_hour = (available_cutoff.hour // 6) * 6
        date = available_cutoff.date()

        return date.strftime("%Y-%m-%d"), cycle_hour

    def get_steps_for_cycle(self, model: str, cycle: int, max_step: int = 72) -> List[int]:
        """Return the available forecast steps for this model/cycle combination."""
        cfg = MODEL_CONFIG[model]
        # 00 and 12 UTC IFS runs have longer step ranges
        if model == "ifs" and cycle in (0, 12):
            all_steps = cfg["steps_long"]
        else:
            all_steps = cfg["steps_short"]
        return [s for s in all_steps if s <= max_step]

    # ─── Cache checking ───────────────────────────────────────────────────────

    def get_cached_forecast(
        self,
        model: str,
        date: str,
        cycle: int,
        params: List[str],
    ) -> Optional[Dict]:
        """
        Return metadata for a cached forecast if it exists and is valid.
        """
        key = f"{model}:{date}:{cycle:02d}:{','.join(sorted(params))}"
        entry = self._index.get(key)
        if not entry:
            return None

        filepath = Path(entry["file_path"])
        if not filepath.exists():
            del self._index[key]
            self._save_index()
            return None

        # Check TTL
        retrieved = datetime.fromisoformat(entry["retrieved_at"])
        age_hours = (datetime.utcnow() - retrieved).total_seconds() / 3600
        if age_hours > settings.cache_ttl_hours:
            logger.info("Cached forecast expired (%.1fh old): %s", age_hours, key)
            return None

        return entry

    # ─── Download with retry ─────────────────────────────────────────────────

    async def download_forecast(
        self,
        model: str = "ifs",
        date: Optional[str] = None,
        cycle: Optional[int] = None,
        parameters: Optional[List[str]] = None,
        max_step: int = 72,
    ) -> Dict:
        """
        Download ECMWF open data forecast. Returns metadata dict with file_path.

        Uses ecmwf-opendata client which accesses:
          https://data.ecmwf.int/forecasts/

        Implements exponential backoff retry on failure.
        """
        if model not in MODEL_CONFIG:
            raise ValueError(f"Unknown model: {model}. Supported: {list(MODEL_CONFIG)}")

        cfg = MODEL_CONFIG[model]

        # Resolve date/cycle
        if date is None or cycle is None:
            latest_date, latest_cycle = self.get_latest_cycle(model)
            date = date or latest_date
            cycle = cycle if cycle is not None else latest_cycle

        # Resolve parameters
        if parameters is None:
            parameters = ["tp"]
        # Filter to what's available for this model
        available_params = set(cfg["parameters"].keys())
        parameters = [p for p in parameters if p in available_params]
        if not parameters:
            parameters = ["tp"]

        # Check cache first
        cached = self.get_cached_forecast(model, date, cycle, parameters)
        if cached:
            logger.info("Using cached forecast: %s", cached["cache_key"])
            return cached

        # Prepare steps
        steps = self.get_steps_for_cycle(model, cycle, max_step)

        # Download with retries
        last_error = None
        for attempt in range(settings.ecmwf_max_retries):
            try:
                result = await self._do_download(
                    model=model,
                    date=date,
                    cycle=cycle,
                    parameters=parameters,
                    steps=steps,
                )
                return result
            except Exception as e:
                last_error = e
                delay = settings.ecmwf_retry_delay * (2 ** attempt)
                logger.warning(
                    "ECMWF download attempt %d/%d failed: %s. Retrying in %.1fs",
                    attempt + 1, settings.ecmwf_max_retries, e, delay
                )
                if attempt < settings.ecmwf_max_retries - 1:
                    await asyncio.sleep(delay)

        raise ECMWFDataUnavailableError(
            f"Failed to download {model} forecast for {date}/{cycle:02d}UTC "
            f"after {settings.ecmwf_max_retries} attempts: {last_error}"
        )

    async def _do_download(
        self,
        model: str,
        date: str,
        cycle: int,
        parameters: List[str],
        steps: List[int],
    ) -> Dict:
        """Perform the actual ECMWF open data download using the official client."""
        try:
            from ecmwf.opendata import Client as ECMWFOpenDataClient
        except ImportError:
            raise ECMWFDataUnavailableError(
                "ecmwf-opendata package not installed. "
                "Install with: pip install ecmwf-opendata"
            )

        cfg = MODEL_CONFIG[model]
        output_filename = (
            f"{model}_{date.replace('-', '')}_{cycle:02d}z"
            f"_{'_'.join(sorted(parameters))}.grib2"
        )
        output_path = self.cache_dir / output_filename

        # ecmwf-opendata uses "source" to pick the endpoint
        # "ecmwf" = data.ecmwf.int (requires no login for open data)
        client = ECMWFOpenDataClient(source="ecmwf")

        # Build the request
        request = {
            "date": date,
            "time": cycle,
            "stream": cfg["stream"],
            "type": cfg["type"],
            "param": parameters,
            "step": steps,
        }

        if model == "aifs":
            request["model"] = "aifs"

        logger.info(
            "Downloading ECMWF %s forecast: %s/%02dUTC steps=%d..%d params=%s",
            model.upper(), date, cycle, min(steps), max(steps), parameters
        )

        # Run the blocking download in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: client.retrieve(
                **request,
                target=str(output_path),
            )
        )

        if not output_path.exists() or output_path.stat().st_size < 100:
            raise ECMWFDataUnavailableError(
                f"Download produced empty or missing file: {output_path}"
            )

        file_size = output_path.stat().st_size
        logger.info(
            "Downloaded %s: %.1f MB to %s",
            model.upper(), file_size / 1e6, output_path
        )

        metadata = {
            "cache_key": f"{model}:{date}:{cycle:02d}:{','.join(sorted(parameters))}",
            "model": model,
            "init_date": date,
            "init_cycle": cycle,
            "parameters": parameters,
            "steps": steps,
            "file_path": str(output_path),
            "file_size_bytes": file_size,
            "retrieved_at": datetime.utcnow().isoformat(),
            "is_valid": True,
        }

        # Update index
        self._index[metadata["cache_key"]] = metadata
        self._save_index()

        return metadata

    # ─── Availability probe ──────────────────────────────────────────────────

    async def check_ecmwf_accessible(self) -> bool:
        """Probe ECMWF data server availability."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.head("https://data.ecmwf.int/forecasts/")
                return r.status_code < 500
        except Exception:
            return False

    def list_cached_forecasts(self) -> List[Dict]:
        """Return all valid cached forecast entries."""
        result = []
        for key, entry in self._index.items():
            fp = Path(entry.get("file_path", ""))
            if fp.exists():
                result.append(entry)
        return result


# Singleton instance
ecmwf_client = ECMWFClient()
