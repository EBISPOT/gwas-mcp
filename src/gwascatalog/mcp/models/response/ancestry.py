from __future__ import annotations

from pydantic import BaseModel, Field


class AncestryResponse(BaseModel):
    type: str | None = None
    number_of_individuals: int | None = None
    ancestral_groups: list[AncestralGroups] = Field(default_factory=list)
    country_of_origin: list[dict] = Field(default_factory=list)
    country_of_recruitment: list[CountryOfRecruitment] = Field(
        default_factory=list,
    )


class CountryOfRecruitment(BaseModel):
    major_area: str | None = None
    region: str | None = None
    country_name: str | None = None


class AncestralGroups(BaseModel):
    ancestry_group: str | None = None
