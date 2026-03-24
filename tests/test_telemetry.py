"""Tests for the telemetry module."""

from __future__ import annotations

import os
import socket

import pytest


def _free_port() -> int:
    """Return an unused TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(autouse=True)
def _isolate_telemetry(monkeypatch):
    """Reset module-level state so each test starts clean."""
    monkeypatch.setenv("GWASCATALOG_METRICS_PORT", str(_free_port()))

    # Reload so that _METRICS_PORT picks up the new env var.
    import importlib

    import gwascatalog.mcp.telemetry as mod

    importlib.reload(mod)
    yield


def test_init_creates_instruments():
    from gwascatalog.mcp import telemetry
    from gwascatalog.mcp.telemetry import init_telemetry

    init_telemetry()

    assert telemetry.tool_calls is not None
    assert telemetry.tool_results is not None
    assert telemetry.resource_accesses is not None
    assert telemetry.tool_duration is not None


def test_startup_check_metric_visible():
    import urllib.request

    from gwascatalog.mcp import telemetry

    telemetry.init_telemetry()
    port = int(os.environ["GWASCATALOG_METRICS_PORT"])

    body = urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics").read().decode()

    assert "gwascatalog_tool_calls_total" in body
    assert "_startup_check" in body


def test_record_tool_call():
    import urllib.request

    from gwascatalog.mcp import telemetry

    telemetry.init_telemetry()
    port = int(os.environ["GWASCATALOG_METRICS_PORT"])

    telemetry.record_tool_call("test_tool", result_count=3, duration_s=0.42)
    telemetry.record_tool_call("test_tool", result_count=0, duration_s=0.1, error=True)

    body = urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics").read().decode()

    assert 'tool="test_tool"' in body
    assert "gwascatalog_tool_results_total" in body
    assert "gwascatalog_tool_duration" in body


def test_record_resource_access():
    import urllib.request

    from gwascatalog.mcp import telemetry

    telemetry.init_telemetry()
    port = int(os.environ["GWASCATALOG_METRICS_PORT"])

    telemetry.record_resource_access("cohorts")

    body = urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics").read().decode()

    assert 'resource="cohorts"' in body
    assert "gwascatalog_resource_accesses_total" in body


def test_record_before_init_is_noop():
    """Calling record helpers before init_telemetry should not raise."""
    from gwascatalog.mcp import telemetry

    # Instruments are None before init
    telemetry.record_tool_call("x", result_count=0, duration_s=0.0)
    telemetry.record_resource_access("y")
