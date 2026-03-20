"""Ancestry result model."""

from __future__ import annotations

from pydantic import Field

from gwascatalog.mcp.models.results.baseresult import BaseResult


class AncestryResult(BaseResult):
    """A single ancestry entry for a study."""

    type: str | None = None
    n: int | None = None
    ancestral_groups: list[str] = Field(default_factory=list)
    recruitment_countries: list[str] = Field(default_factory=list)
