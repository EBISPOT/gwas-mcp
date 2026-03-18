from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from gwascatalog.mcp.models.results import PageSummary


class PaginationInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    total_elements: int = Field(alias="totalElements")
    total_pages: int = Field(alias="totalPages")
    number: int

    def to_summary(self) -> PageSummary:
        return PageSummary(
            page=self.number,
            total_pages=self.total_pages,
            total_results=self.total_elements,
        )

    @property
    def is_truncated(self) -> bool:
        return self.number + 1 < self.total_pages
