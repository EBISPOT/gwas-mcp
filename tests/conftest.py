"""Shared test fixtures."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_client():
    """Mock GwasCatalogClient with AsyncMock."""
    return AsyncMock()


@pytest.fixture
def mock_ctx(mock_client):
    """Mock MCP Context with client in lifespan context."""
    ctx = MagicMock()
    ctx.request_context.lifespan_context = {"client": mock_client}
    return ctx
