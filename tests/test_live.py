"""Live smoke tests against the GWAS Catalog API.

Run with: pytest tests/test_live.py -m live
"""

from __future__ import annotations

import pytest

from gwascatalog.mcp.client import GwasCatalogClient
from gwascatalog.mcp.models import GetAssociationsParams, GetStudiesParams, GetTraitsParams

pytestmark = pytest.mark.live


@pytest.fixture
async def client():
    c = GwasCatalogClient("https://www.ebi.ac.uk/gwas/rest/api", 30)
    yield c
    await c.close()


async def test_get_studies_by_accession(client):
    params = GetStudiesParams(accession_id="GCST000854")
    data = await client.get_studies(params)
    assert data["accession_id"] == "GCST000854"


async def test_get_associations_by_trait(client):
    params = GetAssociationsParams(efo_trait="celiac disease", size=1)
    data = await client.get_associations(params)
    items = data.get("_embedded", {}).get("associations", [])
    assert len(items) >= 1


async def test_get_traits_by_id(client):
    params = GetTraitsParams(efo_id="EFO_0001060")
    data = await client.get_efo_traits(params)
    assert data["efo_id"] == "EFO_0001060"
    assert "celiac" in data["efo_trait"].lower()
