"""Runtime configuration for GWAS Catalog MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_base_url: str = os.getenv(
        "GWASCATALOG_API_BASE_URL", "https://www.ebi.ac.uk/gwas/rest/api"
    )
    host: str = os.getenv("GWASCATALOG_HOST", "127.0.0.1")
    port: int = int(os.getenv("GWASCATALOG_PORT", "8000"))
    mount_path: str = os.getenv("GWASCATALOG_MOUNT_PATH", "/")
    streamable_http_path: str = os.getenv("GWASCATALOG_STREAMABLE_HTTP_PATH", "/mcp")
    timeout_seconds: float = float(os.getenv("GWASCATALOG_HTTP_TIMEOUT", "30"))
