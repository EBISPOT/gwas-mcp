"""ToolResponse wrapper model."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from gwascatalog.mcp.models.params.base import Params
from gwascatalog.mcp.models.response.pagination import PaginationInfo
from gwascatalog.mcp.models.results.pagination import PageSummary

T = TypeVar("T")

_PAGINATION_FIELDS = frozenset({"page", "size", "sort", "direction"})


def _active_filters(params: Params) -> dict[str, Any]:
    """Return non-None filter parameters (excluding pagination/sorting)."""
    return {
        k: v
        for k, v in params.model_dump(exclude_none=True).items()
        if k not in _PAGINATION_FIELDS
    }


def _build_suggestions(
    params: Params,
    result_count: int,
    pagination: PageSummary,
) -> list[str]:
    """Generate actionable suggestions based on query outcome."""
    suggestions: list[str] = []
    filters = _active_filters(params)

    if result_count == 0:
        if filters:
            suggestions.append(
                "No results matched your filters. Try removing some filters "
                "to broaden the search."
            )
        else:
            suggestions.append(
                "No results found. Try a different search term or parameter."
            )
        if "efo_trait" in filters:
            suggestions.append(
                "Tip: use gwascatalog_get_traits with efo_trait to explore "
                "matching EFO terms first, then use the efo_id for precise "
                "filtering."
            )

    if pagination.truncated:
        suggestions.append(
            f"Results are truncated ({pagination.total_results} total). "
            f"Request page={pagination.page + 1} for more results, or "
            f"add filters to narrow the result set."
        )
        if len(filters) <= 1:
            suggestions.append(
                "Consider adding filters to narrow results "
                "(e.g. efo_id, mapped_gene, pubmed_id)."
            )

    return suggestions


class ToolResponse[T](BaseModel):
    """Standard wrapper for all MCP tool responses."""

    model_config = ConfigDict(frozen=True)

    query: dict[str, Any]
    data: list[T]
    pagination: PageSummary
    message: str | None = None
    suggestions: list[str] = Field(default_factory=list)

    @classmethod
    def from_results(
        cls,
        results: list[T],
        params: Params,
        page_data: dict[str, Any] | None = None,
    ) -> ToolResponse[T]:
        """Build a ToolResponse from results and optional raw page data.

        When page_data is None (single-item lookup), a non-paginated summary
        is created automatically.
        """
        if page_data is None:
            pagination = PageSummary(
                page=0,
                total_pages=1 if results else 0,
                total_results=len(results),
                truncated=False,
            )
            message = "No results found in the GWAS Catalog." if not results else None
            return cls(
                query=params.model_dump(exclude_none=True),
                data=results,
                pagination=pagination,
                message=message,
                suggestions=_build_suggestions(params, len(results), pagination),
            )
        page_info = PaginationInfo.model_validate(page_data)
        pagination = page_info.to_summary()
        message = "No results found in the GWAS Catalog." if not results else None
        return cls(
            query=params.model_dump(exclude_none=True),
            data=results,
            pagination=pagination,
            message=message,
            suggestions=_build_suggestions(params, len(results), pagination),
        )
