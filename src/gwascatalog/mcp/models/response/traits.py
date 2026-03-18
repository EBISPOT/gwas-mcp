from __future__ import annotations

from pydantic import BaseModel

from gwascatalog.mcp.models.results import TraitResult


class EfoTraitResponse(BaseModel):
    efo_id: str
    efo_trait: str
    uri: str | None = None

    def to_result(self) -> TraitResult:
        return TraitResult(
            efo_id=self.efo_id,
            efo_trait=self.efo_trait,
            uri=self.uri,
        )
