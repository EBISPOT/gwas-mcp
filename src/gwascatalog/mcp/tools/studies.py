"""Implementation for the gwascatalog_get_studies MCP tool."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    AncestryResult,
    GetStudiesParams,
    StudyResult,
    ToolResponse,
)

if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def _enrich(client: GwasCatalogClient, study: StudyResult) -> StudyResult:
    """Resolve ancestries for a study."""
    try:
        ancestry_items = await client.get_study_ancestries(study.accession_id)
    except RuntimeError:
        ancestry_items = []
    ancestries = [AncestryResult.model_validate(a) for a in ancestry_items]
    return study.model_copy(update={"ancestries": ancestries})


async def get_studies(
    client: GwasCatalogClient, params: GetStudiesParams
) -> ToolResponse[StudyResult]:
    fetch = await client.get_studies(params)
    studies = [StudyResult.model_validate(item) for item in fetch["items"]]
    results = await asyncio.gather(*[_enrich(client, s) for s in studies])
    return ToolResponse.from_results(list(results), params, fetch["page"])
