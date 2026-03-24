"""GWAS Catalog MCP server."""

from __future__ import annotations

import argparse
import logging
import time
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Literal

from gwascatalog.mcp.telemetry import (
    init_telemetry,
    record_resource_access,
    record_tool_call,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from gwascatalog.mcp.client import GwasCatalogClient
from gwascatalog.mcp.config import Settings
from gwascatalog.mcp.constants import (
    GWASCATALOG_MCP_INSTRUCTIONS,
    TRAIT_SEARCH_GUIDANCE,
)
from gwascatalog.mcp.models import (
    URI,
    AccessionId,
    AncestralGroup,
    AssociationId,
    AssociationResult,
    AssociationSortKeyField,
    Cohort,
    DiseaseTrait,
    EfoId,
    EfoTrait,
    FullPValueSet,
    GetAssociationsParams,
    GetStudiesParams,
    GetTraitsParams,
    GxE,
    MappedGene,
    PageField,
    PubmedId,
    RsId,
    ShowChildTrait,
    SizeField,
    SortDirectionField,
    StudyResult,
    StudySortKeyField,
    ToolResponse,
    TraitResult,
    TraitSortKeyField,
)
from gwascatalog.mcp.resources import (
    fetch_cohorts,
    read_ancestry_labels,
    read_countries,
    read_variant_consequences,
)
from gwascatalog.mcp.tools import get_associations, get_studies, get_traits
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

logger = logging.getLogger(__name__)
settings = Settings()
MCP_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True
)


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
    streamable_http_path=settings.streamable_http_path,
    lifespan=lifespan,
)


def _get_client(ctx: Context) -> GwasCatalogClient:
    return ctx.request_context.lifespan_context["client"]


# ---- Resources ----


@mcp.resource(
    "gwascatalog://cohorts",
    name="cohorts",
    title="GWAS Catalog Cohorts",
    description=(
        "Controlled vocabulary of cohort identifiers and names from the GWAS Catalog. "
        "Updated weekly; cached for 24 hours."
    ),
    mime_type="application/json",
)
async def gwascatalog_cohorts() -> dict:
    record_resource_access("cohorts")
    return await fetch_cohorts()


@mcp.resource(
    "gwascatalog://ancestry-labels",
    name="ancestry_labels",
    title="GWAS Catalog Ancestry Labels",
    description=(
        "Ancestry categories used to classify study participants in the GWAS Catalog, "
        "from Morales et al. 2018 (doi:10.1186/s13059-018-1396-2). "
        "Includes broad ancestral group labels, descriptions, "
        "and example sub-populations."
    ),
    mime_type="application/json",
)
def gwascatalog_ancestry_labels() -> dict:
    record_resource_access("ancestry_labels")
    return read_ancestry_labels()


@mcp.resource(
    "gwascatalog://variant-consequences",
    name="variant_consequences",
    title="Ensembl Variant Consequences",
    description=(
        "Sequence Ontology (SO) consequence terms used to annotate variant effects "
        "on transcripts, ordered by severity. Sourced from Ensembl. "
        "Includes SO term, accession, display name, and IMPACT rating."
    ),
    mime_type="application/json",
)
def gwascatalog_variant_consequences() -> dict:
    record_resource_access("variant_consequences")
    return read_variant_consequences()


@mcp.resource(
    "gwascatalog://countries",
    name="countries",
    title="GWAS Catalog Countries of Recruitment",
    description=(
        "Valid country names accepted by the GWAS Catalog for the "
        "'country of recruitment' field in study metadata."
    ),
    mime_type="application/json",
)
def gwascatalog_countries() -> dict:
    record_resource_access("countries")
    return read_countries()


# ---- Traits tool ----

TRAIT_TOOL_DESCRPTION = """
Search and browse Experimental Factor Ontology (EFO) terms in the GWAS Catalog.

This tool can be helpful to explore the traits present in the GWAS Catalog. If
the trait is present in the GWAS Catalog, there will be studies
and associations linked with it.

If a trait doesn't appear in the GWAS Catalog, try searching with efo_trait which
will return any traits including the term. efo_id is most precise.
"""


@mcp.tool(annotations=MCP_TOOL_ANNOTATIONS, description=TRAIT_TOOL_DESCRPTION)
async def gwascatalog_get_traits(
    ctx: Context,
    efo_id: EfoId | None = None,
    efo_trait: EfoTrait | None = None,
    mapped_gene: MappedGene | None = None,
    pubmed_id: PubmedId | None = None,
    uri: URI | None = None,
    page: PageField = 0,
    size: SizeField = 10,
    sort: TraitSortKeyField | None = None,
    direction: SortDirectionField = "asc",
) -> ToolResponse[TraitResult]:
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
    t0 = time.perf_counter()
    try:
        result = await get_traits(client=_get_client(ctx), params=params)
    except Exception:
        logger.exception("gwascatalog_get_traits internal error")
        record_tool_call(
            "get_traits",
            result_count=0,
            duration_s=time.perf_counter() - t0,
            error=True,
        )
        raise
    record_tool_call(
        "get_traits", result_count=len(result.data), duration_s=time.perf_counter() - t0
    )
    return result


# ---- Studies tool ----

STUDY_TOOL_DESCRIPTION = f"""
Find GWAS Catalog studies by trait, ancestry, gene, or accession.

Trait search guidance:

{TRAIT_SEARCH_GUIDANCE}
"""


@mcp.tool(annotations=MCP_TOOL_ANNOTATIONS, description=STUDY_TOOL_DESCRIPTION)
async def gwascatalog_get_studies(
    ctx: Context,
    accession_id: AccessionId | None = None,
    efo_trait: EfoTrait | None = None,
    efo_id: EfoId | None = None,
    disease_trait: DiseaseTrait | None = None,
    mapped_gene: MappedGene | None = None,
    pubmed_id: PubmedId | None = None,
    ancestral_group: AncestralGroup | None = None,
    cohort: Cohort | None = None,
    full_pvalue_set: FullPValueSet | None = None,
    gxe: GxE | None = None,
    show_child_trait: ShowChildTrait | None = None,
    page: PageField = 0,
    size: SizeField = 10,
    sort: StudySortKeyField | None = None,
    direction: SortDirectionField = "asc",
) -> ToolResponse[StudyResult]:
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

    t0 = time.perf_counter()
    try:
        result = await get_studies(client=_get_client(ctx), params=params)
    except Exception:
        logger.exception("gwascatalog_get_studies internal error")
        record_tool_call(
            "get_studies",
            result_count=0,
            duration_s=time.perf_counter() - t0,
            error=True,
        )
        raise
    record_tool_call(
        "get_studies",
        result_count=len(result.data),
        duration_s=time.perf_counter() - t0,
    )
    return result


# ---- Associations tool ----

ASSOCATION_TOOL_DESCRIPTION = f"""
Find variant-trait associations with statistical details from the GWAS Catalog.

Trait search guidance:

{TRAIT_SEARCH_GUIDANCE}
"""


@mcp.tool(annotations=MCP_TOOL_ANNOTATIONS, description=ASSOCATION_TOOL_DESCRIPTION)
async def gwascatalog_get_associations(
    ctx: Context,
    association_id: AssociationId | None = None,
    efo_trait: EfoTrait | None = None,
    efo_id: EfoId | None = None,
    rs_id: RsId | None = None,
    mapped_gene: MappedGene | None = None,
    accession_id: AccessionId | None = None,
    pubmed_id: PubmedId | None = None,
    full_pvalue_set: FullPValueSet | None = None,
    show_child_trait: ShowChildTrait | None = None,
    page: PageField = 0,
    size: SizeField = 10,
    sort: AssociationSortKeyField | None = None,
    # desc default suggested for snp count
    direction: SortDirectionField = "desc",
) -> ToolResponse[AssociationResult]:
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

    t0 = time.perf_counter()
    try:
        result = await get_associations(
            client=_get_client(ctx),
            params=params,
        )
    except Exception:
        logger.exception("gwascatalog_get_associations internal error")
        record_tool_call(
            "get_associations",
            result_count=0,
            duration_s=time.perf_counter() - t0,
            error=True,
        )
        raise
    record_tool_call(
        "get_associations",
        result_count=len(result.data),
        duration_s=time.perf_counter() - t0,
    )
    return result


# ---- CLI ----


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GWAS Catalog MCP server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "http"),
        default="stdio",
        help="Transport mode: stdio or streamable HTTP.",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host address to bind to. Use 0.0.0.0 for containers.",
    )
    parser.add_argument(
        "--port",
        default=None,
        help="Port to bind to. Defaults to 8000.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    transport: Literal["streamable-http", "stdio"] = (
        "streamable-http" if args.transport == "http" else "stdio"
    )

    if transport == "streamable-http":
        logger.info("Starting telemetry server")
        init_telemetry()

    logger.info(
        "Starting MCP server: transport=%s host=%s port=%s",
        transport,
        mcp.settings.host,
        mcp.settings.port,
    )
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
