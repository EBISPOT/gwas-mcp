"""ToolResponse wrapper model."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

from gwascatalog.mcp.models.params.base import Params
from gwascatalog.mcp.models.response.pagination import PaginationInfo
from gwascatalog.mcp.models.results.pagination import PageSummary

T = TypeVar("T")


class ToolResponse[T](BaseModel):
    """Standard wrapper for all MCP tool responses."""

    model_config = ConfigDict(frozen=True)

    query: dict[str, Any]
    data: list[T]
    pagination: PageSummary

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
            return cls(
                query=params.model_dump(exclude_none=True),
                data=results,
                pagination=PageSummary(
                    page=0, total_pages=1, total_results=len(results), truncated=False
                ),
            )
        page_info = PaginationInfo.model_validate(page_data)
        return cls(
            query=params.model_dump(exclude_none=True),
            data=results,
            pagination=page_info.to_summary(),
        )
