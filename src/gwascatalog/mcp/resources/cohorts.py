"""Cached cohort vocabulary resource fetched daily from PGS Catalog FTP."""

from __future__ import annotations

import asyncio
import time
from io import StringIO

import httpx

from gwascatalog.mcp.resources.static import ColumnarData, _csv_to_columnar

_COHORTS_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/spot/pgs/metadata/pgs_all_metadata_cohorts.csv"
)
_CACHE_TTL_SECONDS = 86_400  # 24 hours

_cache_lock = asyncio.Lock()
_cached_data: ColumnarData | None = None
_cached_at: float = 0.0


async def fetch_cohorts() -> ColumnarData:
    """Return cohort data as columnar data, refreshing the cache once per day."""
    global _cached_data, _cached_at  # noqa: PLW0603

    now = time.monotonic()
    if _cached_data is not None and (now - _cached_at) < _CACHE_TTL_SECONDS:
        return _cached_data

    async with _cache_lock:
        # Re-check after acquiring lock (another coroutine may have refreshed).
        now = time.monotonic()
        if _cached_data is not None and (now - _cached_at) < _CACHE_TTL_SECONDS:
            return _cached_data

        async with httpx.AsyncClient() as client:
            response = await client.get(_COHORTS_URL, timeout=30)
            response.raise_for_status()
            data = _csv_to_columnar(StringIO(response.text))
            # remove the third column to save tokens
            data.pop("Previous/other/additional names", None)
            _cached_data = data
            _cached_at = time.monotonic()

    return _cached_data
