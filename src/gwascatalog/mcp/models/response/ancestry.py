from __future__ import annotations

from pydantic import BaseModel, Field

from gwascatalog.mcp.models.results import AncestryResult


class AncestryResponse(BaseModel):
    type: str | None = None
    number_of_individuals: int | None = None
    ancestral_groups: list[AncestralGroups] = Field(default_factory=list)
    country_of_origin: list[dict] = Field(default_factory=list)
    country_of_recruitment: list[CountryOfRecruitment] = Field(
        default_factory=list,
    )

    def to_summary(self) -> AncestryResult:
        return AncestryResult(
            type=self.type,
            n=self.number_of_individuals,
            ancestral_groups=[
                g.ancestral_group for g in self.ancestral_groups if g.ancestral_group
            ],
            recruitment_countries=[
                c.country_name for c in self.country_of_recruitment if c.country_name
            ],
        )


class CountryOfRecruitment(BaseModel):
    major_area: str | None = None
    region: str | None = None
    country_name: str | None = None


class AncestralGroups(BaseModel):
    ancestral_group: str | None = None
