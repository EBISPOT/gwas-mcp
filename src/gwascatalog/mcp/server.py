"""GWAS Catalog MCP server."""

from __future__ import annotations

import argparse
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from gwascatalog.mcp.client import GwasCatalogClient
from gwascatalog.mcp.config import Settings
from gwascatalog.mcp.constants import GWASCATALOG_MCP_INSTRUCTIONS
from gwascatalog.mcp.models import (
    AssociationResult,
    GetAssociationsParams,
    GetStudiesParams,
    GetTraitsParams,
    StudyResult,
    ToolResponse,
    TraitResult,
)
from gwascatalog.mcp.tools import get_associations, get_studies, get_traits
from mcp.server.fastmcp import Context, FastMCP

settings = Settings()


@asynccontextmanager
async def lifespan(_: FastMCP) -> AsyncIterator[dict[str, Any]]:
    client = GwasCatalogClient(settings.api_base_url, settings.timeout_seconds)
    try:
        yield {"client": client}
    finally:
        await client.close()


mcp = FastMCP(
    name="gwascatalog",
    instructions=GWASCATALOG_MCP_INSTRUCTIONS,
    host=settings.host,
    port=settings.port,
    mount_path=settings.mount_path,
    streamable_http_path=settings.streamable_http_path,
    lifespan=lifespan,
)


def _get_client(ctx: Context) -> GwasCatalogClient:
    return ctx.request_context.lifespan_context["client"]


# ---- Traits tool ----


@mcp.tool()
async def gwascatalog_get_traits(
    ctx: Context,
    efo_id: str | None = None,
    efo_trait: str | None = None,
    mapped_gene: str | None = None,
    pubmed_id: str | None = None,
    uri: str | None = None,
    page: int = 0,
    size: int = 10,
    sort: str | None = None,
    direction: str | None = None,
) -> ToolResponse[TraitResult]:
    """Search and browse EFO trait ontology terms from the GWAS Catalog.

    Returns matching traits as a structured table (list mode) or a single record
    dict (detail mode). Use efo_id for a single trait lookup, or other parameters
    to filter/search.

    Args:
        efo_id: Single trait lookup by EFO ID (e.g. "EFO_0001060")
        efo_trait: Search by trait label keyword (e.g. "diabetes")
        mapped_gene: Find traits associated with a gene
        pubmed_id: Find traits from a publication
        uri: Filter by trait URI
        page: Page number (0-indexed, default 0)
        size: Results per page (default 10)
        sort: Field to sort by
        direction: Sort direction ("asc" or "desc")
    """
    params = GetTraitsParams(
        efo_id=efo_id,
        efo_trait=efo_trait,
        mapped_gene=mapped_gene,
        pubmed_id=pubmed_id,
        uri=uri,
        page=page,
        size=size,
        sort=sort,
        direction=direction,
    )
    return await get_traits(client=_get_client(ctx), params=params)


# ---- Studies tool ----


@mcp.tool()
async def gwascatalog_get_studies(
    ctx: Context,
    accession_id: str | None = None,
    efo_trait: str | None = None,
    efo_id: str | None = None,
    disease_trait: str | None = None,
    mapped_gene: str | None = None,
    pubmed_id: str | None = None,
    ancestral_group: str | None = None,
    cohort: str | None = None,
    full_pvalue_set: bool | None = None,
    gxe: bool | None = None,
    show_child_trait: bool | None = None,
    page: int = 0,
    size: int = 10,
    sort: str | None = None,
    direction: str | None = None,
) -> ToolResponse[StudyResult]:
    """Find GWAS studies by trait, ancestry, gene, or accession.

    Returns matching studies as a structured table (list mode) or a single record
    dict with ancestry details (detail mode when accession_id is provided).

    Args:
        accession_id: Single study lookup (e.g. "GCST000854")
        efo_trait: EFO trait label filter (e.g. "type 2 diabetes mellitus")
        efo_id: EFO trait ID filter (e.g. "EFO_0001060")
        disease_trait: Free-text trait description filter
        mapped_gene: Gene filter (e.g. "TCF7L2")
        pubmed_id: PubMed ID filter
        ancestral_group: Ancestry filter (e.g. "European")
        cohort: Cohort filter (e.g. "UKB")
        full_pvalue_set: Filter for full p-value set availability
        gxe: Filter for gene-environment interaction studies
        show_child_trait: Include child EFO traits in results
        page: Page number (0-indexed, default 0)
        size: Results per page (default 10)
        sort: Field to sort by
        direction: Sort direction ("asc" or "desc")
    """
    params = GetStudiesParams(
        accession_id=accession_id,
        efo_trait=efo_trait,
        efo_id=efo_id,
        disease_trait=disease_trait,
        mapped_gene=mapped_gene,
        pubmed_id=pubmed_id,
        ancestral_group=ancestral_group,
        cohort=cohort,
        full_pvalue_set=full_pvalue_set,
        gxe=gxe,
        show_child_trait=show_child_trait,
        page=page,
        size=size,
        sort=sort,
        direction=direction,
    )

    return await get_studies(client=_get_client(ctx), params=params)


# ---- Associations tool ----


@mcp.tool()
async def gwascatalog_get_associations(
    ctx: Context,
    association_id: int | None = None,
    efo_trait: str | None = None,
    efo_id: str | None = None,
    rs_id: str | None = None,
    mapped_gene: str | None = None,
    accession_id: str | None = None,
    pubmed_id: str | None = None,
    full_pvalue_set: bool | None = None,
    show_child_trait: bool | None = None,
    page: int = 0,
    size: int = 10,
    sort: str | None = None,
    direction: str | None = None,
) -> ToolResponse[AssociationResult]:
    """Find variant-trait associations with statistical details from the GWAS Catalog.

    Returns associations as a structured table (list mode) or a single record dict
    with loci details (detail mode when association_id is provided).

    Args:
        association_id: Single association lookup by numeric ID
        efo_trait: EFO trait label filter (e.g. "celiac disease")
        efo_id: EFO trait ID filter (e.g. "EFO_0001060")
        rs_id: Variant filter (e.g. "rs7903146")
        mapped_gene: Gene filter (e.g. "TCF7L2")
        accession_id: Study accession filter (e.g. "GCST000854")
        pubmed_id: PubMed ID filter
        full_pvalue_set: Filter for full p-value set
        show_child_trait: Include child EFO traits
        page: Page number (0-indexed, default 0)
        size: Results per page (default 10)
        sort: Field to sort by
        direction: Sort direction ("asc" or "desc")
    """
    params = GetAssociationsParams(
        association_id=association_id,
        efo_trait=efo_trait,
        efo_id=efo_id,
        rs_id=rs_id,
        mapped_gene=mapped_gene,
        accession_id=accession_id,
        pubmed_id=pubmed_id,
        full_pvalue_set=full_pvalue_set,
        show_child_trait=show_child_trait,
        page=page,
        size=size,
        sort=sort,
        direction=direction,
    )

    return await get_associations(
        client=_get_client(ctx),
        params=params,
    )


# ---- CLI ----


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GWAS Catalog MCP server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "http"),
        default="stdio",
        help="Transport mode: stdio or streamable HTTP.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    transport: Literal["streamable-http", "stdio"] = (
        "streamable-http" if args.transport == "http" else "stdio"
    )
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
