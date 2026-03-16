# Plan: GWAS Catalog MCP Server — MVP Implementation

Implement 3 MCP tools + 1 internal trait resolver wrapping the GWAS Catalog REST API V2. Tools return CSV for lists and structured text for detail lookups. Pydantic models for both parameters and responses.

---

## Tools

### 1. `gwascatalog_get_associations`

**Purpose:** Find variant-trait associations with statistical details. Core evidence tool.

**Parameters** (all optional):
- `association_id` — single association lookup
- `efo_trait` — EFO trait label (passed through to REST API)
- `efo_id` — EFO trait ID (e.g. `EFO_0001060`)
- `rs_id` — variant filter (e.g. `rs7903146`)
- `mapped_gene` — gene filter (e.g. `TCF7L2`)
- `accession_id` — study filter (e.g. `GCST000854`)
- `pubmed_id` — publication filter
- `full_pvalue_set`, `show_child_trait` — boolean filters
- `page` (default 0), `size` (default 10), `sort`, `direction`

**REST endpoints:**
- List: `GET /v2/associations` with query params
- Detail: `GET /v2/associations/{association_id}`
- Enrichment (detail only): `GET /v2/associations/{association_id}/loci`

**CSV columns (list mode):**
`association_id, rs_id, mapped_gene, p_value, odds_ratio, beta, ci, risk_allele, efo_trait, study_accession`

### 2. `gwascatalog_get_studies`

**Purpose:** Find GWAS studies by trait, ancestry, gene, or accession.

**Parameters** (all optional):
- `accession_id` — single study lookup
- `efo_trait` — EFO trait label (passed through to REST API)
- `efo_id` — EFO trait ID
- `disease_trait` — free-text trait description
- `mapped_gene` — gene filter
- `pubmed_id` — publication filter
- `ancestral_group` — ancestry filter (e.g. `European`)
- `cohort` — cohort filter (e.g. `UKB`)
- `full_pvalue_set`, `gxe`, `show_child_trait` — boolean filters
- `page` (default 0), `size` (default 10), `sort`, `direction`

**REST endpoints:**
- List: `GET /v2/studies` with query params
- Detail: `GET /v2/studies/{accession_id}`
- Enrichment (detail only): `GET /v2/studies/{accession_id}/ancestries`

**CSV columns (list mode):**
`accession_id, disease_trait, efo_trait, first_author, date, journal, sample_size, ancestral_groups`

### 3. `gwascatalog_get_traits`

**Purpose:** Search and browse EFO trait ontology terms. Also used internally by other tools.

**Parameters** (all optional):
- `efo_id` — single trait lookup (e.g. `EFO_0001060`)
- `efo_trait` — trait label keyword search (e.g. `diabetes`)
- `mapped_gene` — traits associated with a gene
- `pubmed_id` — traits from a publication
- `uri` — trait URI
- `page` (default 0), `size` (default 10), `sort`, `direction`

**REST endpoints:**
- List: `GET /v2/efo-traits` with query params
- Detail: `GET /v2/efo-traits/{efo_id}`

**CSV columns (list mode):**
`efo_id, efo_trait, uri`

### Internal: `_resolve_traits()`

**Purpose:** Convert an `efo_trait` keyword to EFO IDs when the downstream REST endpoint doesn't support `efo_trait` natively.

**Behaviour:**
- Called internally by tools when needed (not currently needed for MVP since studies, associations, and efo-traits all support `efo_trait` natively)
- Calls `GET /v2/efo-traits?efo_trait=<keyword>` to resolve
- Returns list of matching EFO IDs or empty list with a helpful message

---

## Response Format

### List mode (multiple results)
- CSV text with header row + curated columns (per tool above)
- `page X of Y (Z total results)` footer
- When paginated: footer includes advice on refining query or fetching next page

### Detail mode (single-item lookup via ID parameter)
- Structured key: value text
- Includes enrichment data inline (ancestries for studies, loci for associations)
- Omits null values, HAL links, internal IDs

---

## Architecture

### File structure

```
src/gwascatalog/mcp/
├── __init__.py          (exists, empty)
├── client.py            (exists, MODIFY — add typed endpoint methods)
├── config.py            (exists, no changes)
├── constants.py         (exists, no changes)
├── models.py            (CREATE — Pydantic parameter + response models)
├── server.py            (exists, MODIFY — add tool functions + _resolve_traits)
└── formatters.py        (CREATE — CSV/detail text formatting helpers)
tests/
├── __init__.py          (CREATE)
├── conftest.py          (CREATE — shared fixtures, mock client)
├── test_tools.py        (CREATE — unit tests with mocked responses)
└── test_live.py         (CREATE — live smoke tests, marked for optional run)
```

### Pydantic constrained types (in models.py)
- `EfoId` — `Annotated[str, Field(pattern=r"^EFO_\d+$")]`
- `AccessionId` — `Annotated[str, Field(pattern=r"^GCST\d+$")]`
- `RsId` — `Annotated[str, Field(pattern=r"^rs\d+$")]`
- `PubmedId` — `Annotated[str, Field(pattern=r"^\d+$")]`
- `Chromosome` — `Annotated[str, Field(pattern=r"^(1[0-9]|2[0-2]|[1-9]|X|Y|MT)$")]`

### Parameter models (in models.py)
One Pydantic model per tool, all fields optional (except noted):
- `GetAssociationsParams` — maps to gwascatalog_get_associations parameters
- `GetStudiesParams` — maps to gwascatalog_get_studies parameters
- `GetTraitsParams` — maps to gwascatalog_get_traits parameters

### Response models (in models.py)
Pydantic models matching the API's JSON response structure:
- `PaginationInfo` — from API's `page` object (`size`, `total_elements`, `total_pages`, `number`)
- `EfoTraitResponse` — `efo_id`, `efo_trait`, `uri`
- `AssociationResponse` — `association_id`, `accession_id`, `pubmed_id`, `efo_traits[]`, `p_value`, `pvalue_mantissa`, `pvalue_exponent`, `or_per_copy_num`, `beta_num`, `beta_unit`, `beta_direction`, `ci_lower`, `ci_upper`, `range`, `snp_allele[]`, `locations[]`, `mapped_genes[]`, `risk_frequency`, `multi_snp_haplotype`, `snp_interaction`
- `StudyResponse` — `accession_id`, `pubmed_id`, `disease_trait`, `efo_traits[]`, `initial_sample_size`, `replication_sample_size`, `discovery_ancestry[]`, `replication_ancestry[]`, `snp_count`, `platforms`, `genotyping_technologies[]`, `cohort[]`, `full_summary_stats_available`, `gxe`, `gxg`
- `AncestryResponse` — `type`, `number_of_individuals`, `ancestral_groups[]`, `country_of_origin[]`, `country_of_recruitment[]`
- `LocusResponse` — `haplotype_snp_count`, risk alleles
- `PagedResponse[T]` — generic wrapper with `content: list[T]`, `page: PaginationInfo`

### Client methods (in client.py)
Add typed methods to `GwasCatalogClient`:
- `get_studies(params) -> dict` — `GET /v2/studies` or `/v2/studies/{accession_id}`
- `get_study_ancestries(accession_id) -> dict` — `GET /v2/studies/{accession_id}/ancestries`
- `get_associations(params) -> dict` — `GET /v2/associations` or `/v2/associations/{association_id}`
- `get_association_loci(association_id) -> dict` — `GET /v2/associations/{association_id}/loci`
- `get_efo_traits(params) -> dict` — `GET /v2/efo-traits` or `/v2/efo-traits/{efo_id}`

Each method builds the path + query params from the parameter model, calls `self.get()`, returns raw dict. Pydantic parsing happens in the tool layer.

### Tool functions (in server.py)
Each tool function follows this pattern:
1. Extract `GwasCatalogClient` from context lifespan state
2. Determine mode: detail (ID provided) vs. list (filter query)
3. Call client method
4. Parse response into Pydantic model
5. If detail mode: make enrichment call, merge data, return structured text
6. If list mode: format as CSV with pagination footer

### Formatter functions (in formatters.py)
- `format_csv(rows: list[dict], columns: list[str]) -> str` — select columns, write CSV
- `format_pagination_footer(page_info: PaginationInfo) -> str` — "page X of Y (Z total)"
- `format_detail(data: dict, enrichment: dict | None) -> str` — structured key:value text

---

## Implementation Phases

### Phase 1: Models & Types
1. Create `src/gwascatalog/mcp/models.py`
   - Define constrained types: `EfoId`, `AccessionId`, `RsId`, `PubmedId`, `Chromosome`
   - Define parameter models: `GetAssociationsParams`, `GetStudiesParams`, `GetTraitsParams`
   - Define response models: `PaginationInfo`, `EfoTraitResponse`, `AssociationResponse`, `StudyResponse`, `AncestryResponse`, `LocusResponse`
   - Add `PagedResponse[T]` generic wrapper

### Phase 2: Formatters
2. Create `src/gwascatalog/mcp/formatters.py`
   - `format_csv()` — takes list of response model instances + column spec, produces CSV string
   - `format_pagination_footer()` — produces footer line from PaginationInfo
   - `format_detail()` — produces structured text from a single response model

### Phase 3: Client Methods
3. Extend `src/gwascatalog/mcp/client.py`
   - Add `get_studies()`, `get_study_ancestries()`, `get_associations()`, `get_association_loci()`, `get_efo_traits()` methods
   - Each method builds URL path and query params, delegates to `self.get()`

### Phase 4: Tool Implementations (*depends on phases 1-3*)
4. Implement `_resolve_traits()` in `server.py`
5. Implement `gwascatalog_get_traits` tool — simplest tool, good first target
6. Implement `gwascatalog_get_studies` tool — with ancestry enrichment on detail
7. Implement `gwascatalog_get_associations` tool — with loci enrichment on detail

### Phase 5: Testing (*parallel with phase 4*)
8. Create `tests/conftest.py` — mock client fixture using `httpx.MockTransport` or `respx`
9. Create `tests/test_tools.py` — ≥3 unit tests per tool:
   - List mode with filters
   - Detail mode with enrichment
   - Empty results / no matches
10. Create `tests/test_live.py` — smoke tests against live API (marked `@pytest.mark.live`):
    - `get_studies(accession_id="GCST000854")` returns known study
    - `get_associations(efo_trait="celiac disease", size=1)` returns ≥1 result
    - `get_traits(efo_id="EFO_0001060")` returns celiac disease

### Phase 6: Verification
11. Run `ruff check src/` and `ty check src/`
12. Run `mcp dev src/gwascatalog/mcp/server.py` — verify all 3 tools visible
13. Test sample queries through MCP Inspector

---

## Tools Summary

| Tool | Key parameters | CSV columns (list mode) | Enrichment (detail) |
|---|---|---|---|
| `gwascatalog_get_associations` | `efo_trait`, `efo_id`, `rs_id`, `mapped_gene`, `accession_id`, `pubmed_id` | `association_id, rs_id, mapped_gene, p_value, odds_ratio, beta, ci, risk_allele, efo_trait, study_accession` | Loci |
| `gwascatalog_get_studies` | `efo_trait`, `efo_id`, `disease_trait`, `mapped_gene`, `ancestral_group`, `cohort`, `pubmed_id` | `accession_id, disease_trait, efo_trait, first_author, date, journal, sample_size, ancestral_groups` | Ancestries |
| `gwascatalog_get_traits` | `efo_trait`, `efo_id`, `mapped_gene`, `pubmed_id`, `uri` | `efo_id, efo_trait, uri` | None |

---

## Verification Checklist

- [ ] `ruff check src/` and `ty check src/` pass clean
- [ ] `pytest tests/test_tools.py` — all mocked unit tests pass (≥9 tests total)
- [ ] `pytest tests/test_live.py -m live` — smoke tests pass against live API
- [ ] `mcp dev src/gwascatalog/mcp/server.py` — all 3 tools visible and callable
- [ ] Manual test: `get_traits(efo_trait="diabetes")` returns matching EFO traits as CSV
- [ ] Manual test: `get_associations(efo_trait="type 2 diabetes mellitus", size=5)` returns top associations
- [ ] Manual test: `get_studies(accession_id="GCST000854")` returns detail with ancestry enrichment

---

## Decisions

- **3 tools for MVP** — associations, studies, traits. Publications, variants, genes are out of scope and can be added later.
- **Traits: both exposed + internal** — `gwascatalog_get_traits` is a standalone browsing tool AND an internal resolver for other tools.
- **CSV for list output** — token-efficient, scannable. Page footer with navigation hints.
- **Auto-enrich detail lookups** — study detail includes ancestries, association detail includes loci.
- **Pydantic response models** — parse upstream JSON into typed models before formatting.
- **Ancestry filtering** — exposed as `ancestral_group` parameter on `get_studies` (REST API supports it natively).
- **Default page size: 10** — low limit per plan's architectural patterns; REST API defaults to 20.

---

## Further Considerations

1. **EFO ID pattern**: The current constraint `^EFO_\d+$` may be too strict — some traits use `MONDO_`, `Orphanet_`, `HP_` prefixes. Recommend relaxing to `^[A-Za-z]+_\d+$` or removing the constraint for MVP.
2. **Sort field names**: Need to verify exact field names the API accepts for sorting (e.g. is it `p_value` or `pValue`?). The OpenAPI spec doesn't enumerate valid sort fields — discovery via live testing.
3. **Error messaging for no results**: When a trait search returns 0 matches, the tool should return a helpful message suggesting the agent try a different term, not just an empty CSV.
