"""Pagination summary result model."""

from __future__ import annotations

from typing import Any

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)


class PageSummary(BaseModel):
    """Pagination summary for paginated tool responses."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    page: int = Field(validation_alias=AliasChoices("page", "number"))
    total_pages: int = Field(validation_alias=AliasChoices("total_pages", "totalPages"))
    total_results: int = Field(
        validation_alias=AliasChoices("total_results", "totalElements"),
    )
    truncated: bool = False

    @model_validator(mode="before")
    @classmethod
    def _compute_truncated(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict) and "truncated" not in data:
            page = data.get("page", data.get("number", 0))
            total_pages = data.get("total_pages", data.get("totalPages", 0))
            data["truncated"] = page + 1 < total_pages
        return data

    @computed_field
    def has_next_page(self) -> bool:
        return self.page < self.total_pages - 1
