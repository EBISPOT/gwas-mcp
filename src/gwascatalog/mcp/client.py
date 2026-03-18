"""Async GWAS Catalog API client."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from gwascatalog.mcp.models import (
        GetAssociationsParams,
        GetStudiesParams,
        GetTraitsParams,
    )


class _RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: float) -> None:
        self._rate = rate
        self._tokens = rate
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
            self._last_refill = now
            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0


def _to_query_params(
    params: Any,
    exclude_fields: set[str] | None = None,
) -> dict[str, Any]:
    """Convert a parameter model to API query params with camelCase keys."""
    exclude = exclude_fields or set()
    result: dict[str, Any] = {}
    for field_name, value in params.model_dump(exclude_none=True).items():
        if field_name in exclude:
            continue
        # snake_case -> camelCase
        parts = field_name.split("_")
        camel = parts[0] + "".join(p.capitalize() for p in parts[1:])
        if isinstance(value, bool):
            result[camel] = str(value).lower()
        else:
            result[camel] = value
    return result


class GwasCatalogClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds),
            headers={"Accept": "application/json"},
        )
        self._rate_limiter = _RateLimiter(rate=15.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        await self._rate_limiter.acquire()
        response = await self._client.get(path, params=params)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"GWAS API request failed ({exc.response.status_code})"
                f" for {path}: {exc.response.text}"
            ) from exc
        return response.json()

    async def get_studies(self, params: GetStudiesParams) -> dict[str, Any]:
        if params.accession_id is not None:
            return await self.get(f"/v2/studies/{params.accession_id}")
        query = _to_query_params(params, exclude_fields={"accession_id"})
        return await self.get("/v2/studies", params=query)

    async def get_study_ancestries(self, accession_id: str) -> dict[str, Any]:
        return await self.get(f"/v2/studies/{accession_id}/ancestries")

    async def get_associations(self, params: GetAssociationsParams) -> dict[str, Any]:
        if params.association_id is not None:
            return await self.get(f"/v2/associations/{params.association_id}")
        query = _to_query_params(params, exclude_fields={"association_id"})
        return await self.get("/v2/associations", params=query)

    async def get_association_loci(self, association_id: int) -> dict[str, Any]:
        return await self.get(f"/v2/associations/{association_id}/loci")

    async def get_efo_traits(self, params: GetTraitsParams) -> dict[str, Any]:
        if params.efo_id is not None:
            return await self.get(f"/v2/efo-traits/{params.efo_id}")
        query = _to_query_params(params, exclude_fields={"efo_id"})
        return await self.get("/v2/efo-traits", params=query)
