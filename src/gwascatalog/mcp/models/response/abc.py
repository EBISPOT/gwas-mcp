from __future__ import annotations

import csv
import io
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Self

from pydantic import BaseModel


class GwasCatalogResponse(BaseModel, ABC):
    """Abstract base for GWAS Catalog API response models."""

    CSV_COLUMNS: ClassVar[list[str]]

    @abstractmethod
    def to_csv_row(self) -> dict[str, Any]:
        """Return a flat dict of the fields to include in CSV output."""
        ...

    @classmethod
    def to_csv(cls, records: list[Self]) -> str:
        """Format a list of records as a CSV string."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=cls.CSV_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        for record in records:
            row = record.to_csv_row()
            writer.writerow(
                {col: row.get(col, "") for col in cls.CSV_COLUMNS},
            )
        return output.getvalue().strip()
