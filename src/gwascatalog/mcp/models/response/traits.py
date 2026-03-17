from __future__ import annotations

from typing import Any, ClassVar

from gwascatalog.mcp.models.response._helpers import _format_detail
from gwascatalog.mcp.models.response.abc import GwasCatalogResponse


class EfoTraitResponse(GwasCatalogResponse):
    CSV_COLUMNS: ClassVar[list[str]] = ["efo_id", "efo_trait", "uri"]

    efo_id: str
    efo_trait: str
    uri: str | None = None

    def to_csv_row(self) -> dict[str, Any]:
        """Return a flat dict suitable for CSV output."""
        return {
            "efo_id": self.efo_id,
            "efo_trait": self.efo_trait,
            "uri": self.uri,
        }

    def format_detail(self) -> str:
        """Format this trait as structured key: value text."""
        return _format_detail(
            {
                "EFO ID": self.efo_id,
                "Trait": self.efo_trait,
                "URI": self.uri,
            }
        )
