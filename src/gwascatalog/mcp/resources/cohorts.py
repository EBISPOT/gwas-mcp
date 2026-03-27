"""Cohort vocabulary resource fetched from PGS Catalog FTP."""

from __future__ import annotations

import logging
from io import StringIO

import httpx

from gwascatalog.mcp.constants import HTTP_PROXY, HTTP_TIMEOUT
from gwascatalog.mcp.resources.static import (
    ColumnarData,
    _csv_to_columnar,
    _read_data_file,
)

logger = logging.getLogger(__name__)

_COHORTS_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/spot/pgs/metadata/pgs_all_metadata_cohorts.csv"
)


async def fetch_cohorts() -> ColumnarData:
    """Return cohort data as columnar data, fetching fresh from upstream each call."""
    if HTTP_PROXY is None:
        logger.info("No proxy is set")
    else:
        logger.info(f"{HTTP_PROXY=}")

    try:
        async with httpx.AsyncClient(proxy=HTTP_PROXY) as client:
            response = await client.get(
                _COHORTS_URL, timeout=HTTP_TIMEOUT, follow_redirects=True
            )
            response.raise_for_status()
            data = _csv_to_columnar(StringIO(response.text))
            # remove the third column to save tokens
            data.pop("Previous/other/additional names", None)
            return data
    except Exception:
        logger.exception(
            f"Failed to fetch cohorts from {_COHORTS_URL}; using bundled data"
        )
        return _read_data_file("cohorts.csv")
