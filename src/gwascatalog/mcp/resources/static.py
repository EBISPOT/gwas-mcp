"""Static reference data bundled with the package."""

from __future__ import annotations

import csv
from importlib import resources as importlib_resources
from io import StringIO
from typing import IO

type ColumnarData = dict[str, list[str]]


def _csv_to_columnar(file: IO[str]) -> ColumnarData:
    """Parse CSV into columnar format (column names as keys, values as lists)."""
    reader = csv.DictReader(file)
    columns: dict[str, list[str]] = {col: [] for col in reader.fieldnames or []}
    for row in reader:
        for col in columns:
            columns[col].append(row[col])
    return columns


def _read_data_file(filename: str) -> ColumnarData:
    """Read a CSV file from the bundled data directory and return columnar data."""
    data = StringIO(
        importlib_resources.files("gwascatalog.mcp.data")
        .joinpath(filename)
        .read_text("utf-8")
    )
    return _csv_to_columnar(data)


def read_ancestry_labels() -> ColumnarData:
    """Return ancestry label categories as columnar data."""
    return _read_data_file("ancestry_labels.csv")


def read_variant_consequences() -> ColumnarData:
    """Return Ensembl variant consequence types as columnar data."""
    return _read_data_file("variant_consequences.csv")
