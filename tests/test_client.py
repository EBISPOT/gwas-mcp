"""Unit tests for the GWAS Catalog API client."""

from __future__ import annotations

import httpx

from gwascatalog.mcp.client import GwasCatalogClient
from gwascatalog.mcp.models import GetAssociationsParams, GetStudiesParams


async def test_get_studies_maps_accession_id_sort_to_rest_field():
    seen_sort: str | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_sort
        seen_sort = request.url.params["sort"]
        return httpx.Response(200, json={"_embedded": {"studies": []}, "page": {}})

    client = GwasCatalogClient("https://example.test/gwas/rest/api", 30)
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        base_url="https://example.test/gwas/rest/api",
        transport=httpx.MockTransport(handler),
    )

    await client.get_studies(GetStudiesParams(sort="accession_id"))
    await client.close()

    assert seen_sort == "accession_Id"


async def test_get_associations_omits_default_direction_for_risk_frequency_sort():
    seen_params: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_params.update(request.url.params)
        return httpx.Response(200, json={"_embedded": {"associations": []}, "page": {}})

    client = GwasCatalogClient("https://example.test/gwas/rest/api", 30)
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        base_url="https://example.test/gwas/rest/api",
        transport=httpx.MockTransport(handler),
    )

    await client.get_associations(GetAssociationsParams(sort="risk_frequency"))
    await client.close()

    assert seen_params["sort"] == "risk_frequency"
    assert "direction" not in seen_params
