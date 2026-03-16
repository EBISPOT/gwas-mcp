"""Formatting helpers for GWAS Catalog MCP tool responses."""

from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gwascatalog.mcp.models import (
        AncestryResponse,
        AssociationResponse,
        EfoTraitResponse,
        PaginationInfo,
        StudyResponse,
    )


def format_csv(rows: list[dict[str, Any]], columns: list[str]) -> str:
    """Format rows as CSV with the specified column headers."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=columns, extrasaction="ignore",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row.get(col, "") for col in columns})
    return output.getvalue().strip()


def format_pagination_footer(page_info: PaginationInfo) -> str:
    """Format pagination info as a footer line."""
    footer = (
        f"Page {page_info.number + 1} of {page_info.total_pages} "
        f"({page_info.total_elements} total results)"
    )
    if page_info.number + 1 < page_info.total_pages:
        footer += (
            ". Use page parameter to fetch the next page,"
            " or refine your query."
        )
    return footer


def format_detail(
    data: dict[str, Any],
    enrichment: dict[str, Any] | None = None,
) -> str:
    """Format a single record as structured key: value text."""
    lines: list[str] = []

    def _append_section(section: dict[str, Any]) -> None:
        for key, value in section.items():
            if value is None or value == "" or value == []:
                continue
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        sub = [
                            f"{k}: {v}"
                            for k, v in item.items()
                            if v is not None
                            and v != ""
                            and v != []
                        ]
                        lines.append(f"  - {', '.join(sub)}")
                    else:
                        lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")

    _append_section(data)
    if enrichment:
        lines.append("")
        _append_section(enrichment)

    return "\n".join(lines)


# --- Flattening helpers ---


def flatten_trait(trait: EfoTraitResponse) -> dict[str, Any]:
    """Flatten an EFO trait response to a dict for CSV."""
    return {
        "efo_id": trait.efo_id,
        "efo_trait": trait.efo_trait,
        "uri": trait.uri,
    }


def flatten_study(study: StudyResponse) -> dict[str, Any]:
    """Flatten a study response to a dict for CSV."""
    efo_trait = "; ".join(t.efo_trait for t in study.efo_traits)
    ancestral_groups = "; ".join(study.discovery_ancestry)

    return {
        "accession_id": study.accession_id,
        "disease_trait": study.disease_trait or "",
        "efo_trait": efo_trait,
        "pubmed_id": (
            study.pubmed_id if study.pubmed_id is not None else ""
        ),
        "sample_size": study.initial_sample_size or "",
        "ancestral_groups": ancestral_groups,
    }


def flatten_association(
    assoc: AssociationResponse,
) -> dict[str, Any]:
    """Flatten an association response to a dict for CSV."""
    rs_ids = [
        a.get("rs_id", "") for a in assoc.snp_allele
    ]

    ci = assoc.range or ""
    if (
        not ci
        and assoc.ci_lower is not None
        and assoc.ci_upper is not None
    ):
        ci = f"[{assoc.ci_lower}-{assoc.ci_upper}]"

    return {
        "association_id": assoc.association_id,
        "rs_id": "; ".join(rs_ids),
        "mapped_gene": "; ".join(assoc.mapped_genes),
        "p_value": (
            assoc.p_value if assoc.p_value is not None else ""
        ),
        "beta": assoc.beta or "",
        "ci": ci,
        "risk_allele": "; ".join(assoc.snp_effect_allele),
        "efo_trait": "; ".join(
            t.efo_trait for t in assoc.efo_traits
        ),
        "study_accession": assoc.accession_id or "",
    }


# --- Detail formatters ---


def format_trait_detail(trait: EfoTraitResponse) -> str:
    """Format a single EFO trait as structured detail text."""
    return format_detail({
        "EFO ID": trait.efo_id,
        "Trait": trait.efo_trait,
        "URI": trait.uri,
    })


def format_study_detail(
    study: StudyResponse, ancestries: list[AncestryResponse],
) -> str:
    """Format a study as detail text with ancestry enrichment."""
    data: dict[str, Any] = {"Accession": study.accession_id}

    if study.disease_trait:
        data["Disease/Trait"] = study.disease_trait
    if study.efo_traits:
        data["EFO Traits"] = [
            f"{t.efo_id} — {t.efo_trait}" for t in study.efo_traits
        ]
    if study.pubmed_id is not None:
        data["PubMed ID"] = study.pubmed_id
    if study.initial_sample_size:
        data["Initial Sample Size"] = study.initial_sample_size
    if study.replication_sample_size:
        data["Replication Sample Size"] = (
            study.replication_sample_size
        )
    if study.discovery_ancestry:
        data["Discovery Ancestry"] = study.discovery_ancestry
    if study.replication_ancestry:
        data["Replication Ancestry"] = study.replication_ancestry
    if study.snp_count:
        data["SNP Count"] = study.snp_count
    if study.genotyping_technologies:
        data["Genotyping Technologies"] = (
            study.genotyping_technologies
        )
    if study.platforms:
        data["Platforms"] = study.platforms
    if study.cohort:
        data["Cohort"] = study.cohort
    if study.gxe:
        data["GxE"] = study.gxe
    if study.gxg:
        data["GxG"] = study.gxg
    if study.full_summary_stats_available:
        data["Full Summary Stats"] = True

    enrichment: dict[str, Any] | None = None
    if ancestries:
        ancestry_lines: list[str] = []
        for a in ancestries:
            parts: list[str] = []
            if a.type:
                parts.append(f"Type: {a.type}")
            groups = [
                g.get("ancestral_group", "")
                for g in a.ancestral_groups
            ]
            groups = [g for g in groups if g]
            if groups:
                parts.append(
                    f"Ancestral Groups: {', '.join(groups)}"
                )
            if a.number_of_individuals:
                parts.append(f"N: {a.number_of_individuals}")
            countries = [
                c.get("country_name", "")
                for c in a.country_of_recruitment
            ]
            countries = [c for c in countries if c]
            if countries:
                parts.append(
                    f"Recruitment: {', '.join(countries)}"
                )
            ancestry_lines.append(", ".join(parts))
        enrichment = {"Ancestries": ancestry_lines}

    return format_detail(data, enrichment)


def format_association_detail(
    assoc: AssociationResponse,
    loci_data: list[dict[str, Any]],
) -> str:
    """Format an association as detail text with loci enrichment."""
    data: dict[str, Any] = {
        "Association ID": assoc.association_id,
    }

    rs_ids = [a.get("rs_id", "") for a in assoc.snp_allele]
    if rs_ids:
        data["Variant(s)"] = "; ".join(rs_ids)
    if assoc.mapped_genes:
        data["Mapped Gene(s)"] = "; ".join(assoc.mapped_genes)
    if assoc.snp_effect_allele:
        data["Risk Allele(s)"] = "; ".join(
            assoc.snp_effect_allele
        )
    if assoc.risk_frequency:
        data["Risk Frequency"] = assoc.risk_frequency
    if assoc.locations:
        data["Location(s)"] = "; ".join(assoc.locations)

    if assoc.p_value is not None:
        data["P-Value"] = assoc.p_value
    if assoc.pvalue_description:
        data["P-Value Context"] = assoc.pvalue_description

    if assoc.beta:
        data["Beta"] = assoc.beta
    ci = assoc.range or ""
    if (
        not ci
        and assoc.ci_lower is not None
        and assoc.ci_upper is not None
    ):
        ci = f"[{assoc.ci_lower}-{assoc.ci_upper}]"
    if ci:
        data["CI"] = ci

    if assoc.efo_traits:
        data["EFO Traits"] = [
            f"{t.efo_id} — {t.efo_trait}"
            for t in assoc.efo_traits
        ]
    if assoc.reported_trait:
        data["Reported Trait"] = "; ".join(assoc.reported_trait)

    if assoc.accession_id:
        data["Study"] = assoc.accession_id
    if assoc.first_author:
        data["First Author"] = assoc.first_author
    if assoc.pubmed_id:
        data["PubMed ID"] = assoc.pubmed_id

    enrichment: dict[str, Any] | None = None
    if loci_data:
        enrichment = {"Loci (detailed)": loci_data}

    return format_detail(data, enrichment)
