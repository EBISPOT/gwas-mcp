"""Trait result model."""

from __future__ import annotations

from gwascatalog.mcp.models.results.baseresult import BaseResult


class TraitResult(BaseResult):
    """A single EFO trait result."""

    efo_id: str
    efo_trait: str
