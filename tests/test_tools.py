"""Unit tests for GWAS Catalog MCP tools."""

from __future__ import annotations

from gwascatalog.mcp.server import (
    gwascatalog_get_associations,
    gwascatalog_get_studies,
    gwascatalog_get_traits,
)


# ---- Traits tests ----


async def test_get_traits_list(mock_ctx, mock_client):
    mock_client.get_efo_traits.return_value = {
        "_embedded": {
            "efo_traits": [
                {
                    "efo_trait": "celiac disease",
                    "uri": "http://www.ebi.ac.uk/efo/EFO_0001060",
                    "efo_id": "EFO_0001060",
                },
                {
                    "efo_trait": "type 2 diabetes mellitus",
                    "uri": "http://www.ebi.ac.uk/efo/EFO_0001360",
                    "efo_id": "EFO_0001360",
                },
            ]
        },
        "page": {
            "size": 10,
            "totalElements": 2,
            "totalPages": 1,
            "number": 0,
        },
    }

    result = await gwascatalog_get_traits(mock_ctx, efo_trait="diabetes")
    assert "EFO_0001060" in result
    assert "celiac disease" in result
    assert "Page 1 of 1" in result


async def test_get_traits_detail(mock_ctx, mock_client):
    mock_client.get_efo_traits.return_value = {
        "efo_trait": "celiac disease",
        "uri": "http://www.ebi.ac.uk/efo/EFO_0001060",
        "efo_id": "EFO_0001060",
    }

    result = await gwascatalog_get_traits(
        mock_ctx, efo_id="EFO_0001060",
    )
    assert "EFO_0001060" in result
    assert "celiac disease" in result
    assert "Page" not in result


async def test_get_traits_empty(mock_ctx, mock_client):
    mock_client.get_efo_traits.return_value = {
        "_embedded": {"efo_traits": []},
        "page": {
            "size": 10,
            "totalElements": 0,
            "totalPages": 0,
            "number": 0,
        },
    }

    result = await gwascatalog_get_traits(
        mock_ctx, efo_trait="nonexistent_xyz",
    )
    assert "No traits found" in result


# ---- Studies tests ----


async def test_get_studies_list(mock_ctx, mock_client):
    mock_client.get_studies.return_value = {
        "_embedded": {
            "studies": [
                {
                    "accession_id": "GCST000854",
                    "initial_sample_size": "4,533 cases",
                    "disease_trait": "Celiac disease",
                    "pubmed_id": 21399633,
                    "efo_traits": [
                        {
                            "efo_id": "EFO_0001060",
                            "efo_trait": "celiac disease",
                        }
                    ],
                    "discovery_ancestry": [
                        "4533 European (U.K.)"
                    ],
                }
            ]
        },
        "page": {
            "size": 10,
            "totalElements": 1,
            "totalPages": 1,
            "number": 0,
        },
    }

    result = await gwascatalog_get_studies(
        mock_ctx, efo_trait="celiac disease",
    )
    assert "GCST000854" in result
    assert "Celiac disease" in result
    assert "Page 1 of 1" in result


async def test_get_studies_detail(mock_ctx, mock_client):
    mock_client.get_studies.return_value = {
        "accession_id": "GCST000854",
        "initial_sample_size": "4,533 cases",
        "disease_trait": "Celiac disease",
        "pubmed_id": 21399633,
        "efo_traits": [
            {
                "efo_id": "EFO_0001060",
                "efo_trait": "celiac disease",
            }
        ],
        "discovery_ancestry": ["4533 European (U.K.)"],
    }
    mock_client.get_study_ancestries.return_value = {
        "_embedded": {
            "ancestries": [
                {
                    "type": "initial",
                    "number_of_individuals": 4533,
                    "ancestral_groups": [
                        {"ancestral_group": "European"}
                    ],
                    "country_of_origin": [],
                    "country_of_recruitment": [
                        {"country_name": "U.K."}
                    ],
                }
            ]
        }
    }

    result = await gwascatalog_get_studies(
        mock_ctx, accession_id="GCST000854",
    )
    assert "GCST000854" in result
    assert "Celiac disease" in result
    assert "European" in result
    assert "Page" not in result


async def test_get_studies_empty(mock_ctx, mock_client):
    mock_client.get_studies.return_value = {
        "_embedded": {"studies": []},
        "page": {
            "size": 10,
            "totalElements": 0,
            "totalPages": 0,
            "number": 0,
        },
    }

    result = await gwascatalog_get_studies(
        mock_ctx, efo_trait="nonexistent_xyz",
    )
    assert "No studies found" in result


# ---- Associations tests ----


async def test_get_associations_list(mock_ctx, mock_client):
    mock_client.get_associations.return_value = {
        "_embedded": {
            "associations": [
                {
                    "association_id": 188116214,
                    "risk_frequency": "0.28",
                    "p_value": 2e-13,
                    "beta": "0.25 unit decrease",
                    "range": "[0.18-0.33]",
                    "mapped_genes": ["HLA-DPB2"],
                    "locations": ["6:33114046"],
                    "efo_traits": [
                        {
                            "efo_id": "EFO_0001060",
                            "efo_trait": "celiac disease",
                        }
                    ],
                    "accession_id": "GCST90468120",
                    "snp_effect_allele": ["rs9277626-G"],
                    "snp_allele": [
                        {
                            "rs_id": "rs9277626",
                            "effect_allele": "G",
                        }
                    ],
                }
            ]
        },
        "page": {
            "size": 10,
            "totalElements": 1,
            "totalPages": 1,
            "number": 0,
        },
    }

    result = await gwascatalog_get_associations(
        mock_ctx, efo_trait="celiac disease",
    )
    assert "rs9277626" in result
    assert "HLA-DPB2" in result
    assert "2e-13" in result
    assert "Page 1 of 1" in result


async def test_get_associations_detail(mock_ctx, mock_client):
    mock_client.get_associations.return_value = {
        "association_id": 188116214,
        "risk_frequency": "0.28",
        "p_value": 2e-13,
        "beta": "0.25 unit decrease",
        "range": "[0.18-0.33]",
        "mapped_genes": ["HLA-DPB2"],
        "locations": ["6:33114046"],
        "efo_traits": [
            {
                "efo_id": "EFO_0001060",
                "efo_trait": "celiac disease",
            }
        ],
        "accession_id": "GCST90468120",
        "snp_effect_allele": ["rs9277626-G"],
        "snp_allele": [
            {"rs_id": "rs9277626", "effect_allele": "G"}
        ],
    }
    mock_client.get_association_loci.return_value = {
        "_embedded": {"loci": []}
    }

    result = await gwascatalog_get_associations(
        mock_ctx, association_id=188116214,
    )
    assert "188116214" in result
    assert "rs9277626" in result
    assert "HLA-DPB2" in result
    assert "Page" not in result


async def test_get_associations_empty(mock_ctx, mock_client):
    mock_client.get_associations.return_value = {
        "_embedded": {"associations": []},
        "page": {
            "size": 10,
            "totalElements": 0,
            "totalPages": 0,
            "number": 0,
        },
    }

    result = await gwascatalog_get_associations(
        mock_ctx, efo_trait="nonexistent_xyz",
    )
    assert "No associations found" in result
