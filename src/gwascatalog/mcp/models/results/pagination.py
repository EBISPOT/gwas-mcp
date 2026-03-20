"""Pagination summary result model."""

from __future__ import annotations

from pydantic import BaseModel, computed_field


class PageSummary(BaseModel):
    """Pagination summary for paginated tool responses."""

    page: int
    total_pages: int
    total_results: int
    truncated: bool

    @computed_field
    def has_next_page(self) -> bool:
        return self.page < self.total_pages - 1
