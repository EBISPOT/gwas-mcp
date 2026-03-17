"""GWAS Catalog MCP server with one tool per resource."""

from __future__ import annotations

import argparse
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from gwascatalog.mcp.client import GwasCatalogClient
from gwascatalog.mcp.config import Settings
from gwascatalog.mcp.constants import GWASCATALOG_MCP_INSTRUCTIONS
from gwascatalog.mcp.models import (
    AncestryResponse,
    AssociationResponse,
    EfoTraitResponse,
    GetAssociationsParams,
    GetStudiesParams,
    GetTraitsParams,
    PaginationInfo,
    StudyResponse,
)
from mcp.server.fastmcp import Context, FastMCP

# Embedded collection keys in the V2 API responses
_EMBEDDED_TRAITS = "efo_traits"
_EMBEDDED_STUDIES = "studies"
_EMBEDDED_ASSOCIATIONS = "associations"
_EMBEDDED_ANCESTRIES = "ancestries"
_EMBEDDED_LOCI = "loci"

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


async def _resolve_traits(client: GwasCatalogClient, efo_trait: str) -> list[str]:
    """Resolve an EFO trait keyword to a list of EFO IDs."""
    params = GetTraitsParams(efo_trait=efo_trait)
    data = await client.get_efo_traits(params)
    items = data.get("_embedded", {}).get("efoTraits", [])
    return [EfoTraitResponse.model_validate(item).efo_id for item in items]


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
) -> str:
    """Search and browse EFO trait ontology terms from the GWAS Catalog.

    Returns matching traits as CSV (list mode) or structured text (detail mode).
    Use efo_id for a single trait lookup, or other parameters to filter/search.

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
    client = _get_client(ctx)
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

    data = await client.get_efo_traits(params)

    # Detail mode
    if efo_id is not None:
        trait = EfoTraitResponse.model_validate(data)
        return trait.format_detail()

    # List mode
    items = data.get("_embedded", {}).get(_EMBEDDED_TRAITS, [])
    if not items:
        return "No traits found. Try a different search term or broader query."

    traits = [EfoTraitResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    csv_text = EfoTraitResponse.to_csv(traits)
    footer = page_info.format_footer()
    return f"{csv_text}\n\n{footer}"


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
) -> str:
    """Find GWAS studies by trait, ancestry, gene, or accession.

    Returns matching studies as CSV (list mode) or structured text with
    ancestry details (detail mode when accession_id is provided).

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
    client = _get_client(ctx)
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

    data = await client.get_studies(params)

    # Detail mode
    if accession_id is not None:
        study = StudyResponse.model_validate(data)
        try:
            ancestry_data = await client.get_study_ancestries(
                accession_id,
            )
            ancestry_items = ancestry_data.get(
                "_embedded",
                {},
            ).get(_EMBEDDED_ANCESTRIES, [])
        except RuntimeError:
            ancestry_items = []
        ancestries = [AncestryResponse.model_validate(a) for a in ancestry_items]
        return study.format_detail(ancestries)

    # List mode
    items = data.get("_embedded", {}).get(_EMBEDDED_STUDIES, [])
    if not items:
        return "No studies found. Try different search terms or broader filters."

    studies = [StudyResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    csv_text = StudyResponse.to_csv(studies)
    footer = page_info.format_footer()
    return f"{csv_text}\n\n{footer}"


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
) -> str:
    """Find variant-trait associations with statistical details from the GWAS Catalog.

    Returns associations as CSV (list mode) or structured text with loci
    details (detail mode when association_id is provided).

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
    client = _get_client(ctx)
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

    data = await client.get_associations(params)

    # Detail mode
    if association_id is not None:
        assoc = AssociationResponse.model_validate(data)
        try:
            loci_data = await client.get_association_loci(
                association_id,
            )
            loci_items = loci_data.get(
                "_embedded",
                {},
            ).get(_EMBEDDED_LOCI, [])
        except RuntimeError:
            loci_items = []
        return assoc.format_detail(loci_items)

    # List mode
    items = data.get("_embedded", {}).get(
        _EMBEDDED_ASSOCIATIONS,
        [],
    )
    if not items:
        return "No associations found. Try different search terms or broader filters."

    associations = [AssociationResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    csv_text = AssociationResponse.to_csv(associations)
    footer = page_info.format_footer()
    return f"{csv_text}\n\n{footer}"


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
    transport = "streamable-http" if args.transport == "http" else "stdio"
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
