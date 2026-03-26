"""Ancestry result model."""

from __future__ import annotations

from pydantic import AliasChoices, ConfigDict, Field, field_validator

from gwascatalog.mcp.models.results.baseresult import BaseResult


class AncestryResult(BaseResult):
    """A single ancestry entry for a study."""

    model_config = ConfigDict(populate_by_name=True)

    type: str | None = None
    n: int | None = Field(
        default=None,
        validation_alias=AliasChoices("n", "number_of_individuals"),
    )
    ancestral_groups: list[str] = Field(default_factory=list)
    recruitment_countries: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices(
            "recruitment_countries", "country_of_recruitment"
        ),
    )

    @field_validator("ancestral_groups", mode="before")
    @classmethod
    def _flatten_ancestral_groups(cls, v: list) -> list[str]:
        if v and isinstance(v[0], dict):
            return [g["ancestral_group"] for g in v if g.get("ancestral_group")]
        return v

    @field_validator("recruitment_countries", mode="before")
    @classmethod
    def _flatten_countries(cls, v: list) -> list[str]:
        if v and isinstance(v[0], dict):
            return [c["country_name"] for c in v if c.get("country_name")]
        return v
