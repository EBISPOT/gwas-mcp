"""Cached GWAS Catalog OpenAPI schema resource fetched daily."""

from __future__ import annotations

import asyncio
import logging
import time

import httpx

from gwascatalog.mcp.constants import HTTP_PROXY

logger = logging.getLogger(__name__)

_SCHEMA_URL = "https://www.ebi.ac.uk/gwas/rest/api/v2/rest-api-doc.yaml"
_CACHE_TTL_SECONDS = 86_400  # 24 hours

_cache_lock = asyncio.Lock()
_cached_data: str | None = None
_cached_at: float = 0.0


async def fetch_schema() -> str:
    """Return the GWAS Catalog REST API v2 OpenAPI schema as YAML.

    The result is refreshed from the upstream URL once per day.
    """
    global _cached_data, _cached_at  # noqa: PLW0603

    now = time.monotonic()
    if _cached_data is not None and (now - _cached_at) < _CACHE_TTL_SECONDS:
        return _cached_data

    async with _cache_lock:
        # Re-check after acquiring lock (another coroutine may have refreshed).
        now = time.monotonic()
        if _cached_data is not None and (now - _cached_at) < _CACHE_TTL_SECONDS:
            return _cached_data

        if HTTP_PROXY is None:
            logger.info("No proxy is set")
        else:
            logger.info(f"{HTTP_PROXY=}")

        try:
            async with httpx.AsyncClient(proxy=HTTP_PROXY) as client:
                response = await client.get(
                    _SCHEMA_URL, timeout=10, follow_redirects=True
                )
                response.raise_for_status()
                _cached_data = response.text
                _cached_at = time.monotonic()
        except Exception:
            logger.exception(
                f"Failed to fetch schema from {_SCHEMA_URL}; using cached data"
            )
            if _cached_data is None:
                raise

    return _cached_data  # type: ignore[return-value]
