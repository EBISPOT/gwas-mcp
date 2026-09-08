"""Check a fresh MCP initialization handshake for Kubernetes probes."""

from __future__ import annotations

import asyncio
import sys

import anyio
import httpx2

from gwascatalog.mcp.config import Settings
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def check(url: str, timeout: float = 5) -> None:
    # Enclose transport cleanup too; Kubernetes provides the hard process deadline.
    with anyio.fail_after(timeout):
        async with (
            httpx2.AsyncClient(trust_env=False, timeout=timeout) as http,
            streamable_http_client(url, http_client=http) as streams,
            ClientSession(*streams, read_timeout_seconds=timeout) as session,
        ):
            await session.initialize()


def main() -> None:
    settings = Settings()
    url = f"http://127.0.0.1:{settings.port}{settings.streamable_http_path}"
    try:
        asyncio.run(check(url))
    except Exception as exc:
        print(f"MCP initialization check failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
