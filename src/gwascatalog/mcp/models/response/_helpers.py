from __future__ import annotations

from typing import Any


def _format_detail(
    data: dict[str, Any],
    enrichment: dict[str, Any] | None = None,
) -> str:
    """Format a record as structured key: value text."""
    lines: list[str] = []

    def _append_section(section: dict[str, Any]) -> None:
        for key, value in section.items():
            if value is None or value == "" or value == []:
                continue
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        sub = [
                            f"{k}: {v}"
                            for k, v in item.items()
                            if v is not None and v != "" and v != []
                        ]
                        lines.append(f"  - {', '.join(sub)}")
                    else:
                        lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")

    _append_section(data)
    if enrichment:
        lines.append("")
        _append_section(enrichment)

    return "\n".join(lines)
