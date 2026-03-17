from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class PaginationInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    total_elements: int = Field(alias="totalElements")
    total_pages: int = Field(alias="totalPages")
    number: int

    def format_footer(self) -> str:
        """Format pagination info as a footer line."""
        footer = (
            f"Page {self.number + 1} of {self.total_pages} "
            f"({self.total_elements} total results)"
        )
        if self.number + 1 < self.total_pages:
            footer += (
                ". Use page parameter to fetch the next page, or refine your query."
            )
        return footer


T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    content: list[T]
    page: PaginationInfo
