from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class EfoTraitResponse(BaseModel):
    efo_id: str
    efo_trait: str
    uri: str | None = None

    def format_detail(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "efo_id": self.efo_id,
            "efo_trait": self.efo_trait,
        }
        if self.uri is not None:
            result["uri"] = self.uri
        return result
