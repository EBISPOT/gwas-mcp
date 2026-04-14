"""Live smoke tests against the GWAS Catalog API.

Run with: pytest tests/test_live.py -m live
"""

from __future__ import annotations

import pytest

from gwascatalog.mcp.client import GwasCatalogClient
from gwascatalog.mcp.models import (
    GetAssociationsParams,
    GetStudiesParams,
    GetTraitsParams,
)
from gwascatalog.mcp.tools import get_associations, get_studies

pytestmark = pytest.mark.live


@pytest.fixture
async def client():
    c = GwasCatalogClient("https://www.ebi.ac.uk/gwas/rest/api", 30)
    yield c
    await c.close()


async def test_get_studies_by_accession(client):
    params = GetStudiesParams(accession_id="GCST000854")
    fetch = await client.get_studies(params)
    assert len(fetch["items"]) == 1
    assert fetch["items"][0]["accession_id"] == "GCST000854"
    assert fetch["page"] is None


async def test_get_associations_by_trait(client):
    params = GetAssociationsParams(efo_trait="celiac disease", size=1)
    fetch = await client.get_associations(params)
    assert len(fetch["items"]) >= 1
    assert fetch["page"] is not None


async def test_get_traits_by_id(client):
    params = GetTraitsParams(efo_id="MONDO_0005130")
    fetch = await client.get_efo_traits(params)
    assert len(fetch["items"]) == 1
    assert fetch["items"][0]["efo_id"] == "MONDO_0005130"
    assert "celiac" in fetch["items"][0]["efo_trait"].lower()
    assert fetch["page"] is None


async def test_get_associations_tool(client):
    params = GetAssociationsParams(efo_trait="celiac disease", size=1)
    result = await get_associations(client=client, params=params)
    x = result.model_dump()
    assert x["query"]["efo_trait"] == "celiac disease"
    assert len(result.data) >= 1


async def test_get_studies_tool(client):
    params = GetStudiesParams(efo_id="MONDO_0004979")
    result = await get_studies(client=client, params=params)
    traits = [x.efo_traits for x in result.data]
    flat_list = [x for xs in traits for x in xs]

    # every study must include MONDO_0004979's trait label (asthma)
    assert sum("asthma" in x.efo_trait for x in flat_list) == params.size
