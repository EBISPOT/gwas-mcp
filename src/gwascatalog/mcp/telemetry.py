"""OpenTelemetry metrics for the GWAS Catalog MCP server.

Call :func:`init_telemetry` once at process startup (before any tool
calls) to wire up the Prometheus exporter and create instruments.
"""

from __future__ import annotations

import logging
import os

from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server

_METRICS_PORT = int(os.getenv("GWASCATALOG_METRICS_PORT", "9464"))
logger = logging.getLogger(__name__)

_provider: MeterProvider | None = None

# Populated by init_telemetry(); safe to reference (but no-ops) before then.
tool_calls = None
tool_results = None
resource_accesses = None
tool_duration = None


def init_telemetry() -> None:
    """Create the OTel MeterProvider, instruments, and ``/metrics`` endpoint.

    Idempotent — subsequent calls are no-ops.  A synthetic ``_startup_check``
    counter event is recorded so that at least one ``gwascatalog_*`` metric
    is immediately visible on ``/metrics``.
    """
    global _provider, tool_calls, tool_results  # noqa: PLW0603
    global resource_accesses, tool_duration  # noqa: PLW0603

    if _provider is not None:
        return

    resource = Resource.create({"service.name": "gwascatalog-mcp"})
    reader = PrometheusMetricReader()
    _provider = MeterProvider(resource=resource, metric_readers=[reader])

    meter = _provider.get_meter("gwascatalog.mcp")

    tool_calls = meter.create_counter(
        name="gwascatalog.tool.calls",
        description="Total MCP tool invocations",
        unit="1",
    )
    tool_results = meter.create_counter(
        name="gwascatalog.tool.results",
        description="MCP tool results partitioned by outcome",
        unit="1",
    )
    resource_accesses = meter.create_counter(
        name="gwascatalog.resource.accesses",
        description="Total MCP resource accesses",
        unit="1",
    )
    tool_duration = meter.create_histogram(
        name="gwascatalog.tool.duration",
        description="Tool call duration",
        unit="s",
    )

    start_http_server(port=_METRICS_PORT, addr="0.0.0.0")

    # Record a synthetic event so custom metrics are visible immediately.
    tool_calls.add(1, {"tool": "_startup_check", "status": "ok"})
    logger.info("Telemetry initialised, metrics at :%d/metrics", _METRICS_PORT)


def record_tool_call(
    tool_name: str,
    *,
    result_count: int,
    duration_s: float,
    error: bool = False,
) -> None:
    """Record metrics for a single tool invocation."""
    if tool_calls is None:
        return
    status = "error" if error else "ok"
    tool_calls.add(1, {"tool": tool_name, "status": status})
    tool_duration.record(duration_s, {"tool": tool_name})
    if not error:
        has_results = "true" if result_count > 0 else "false"
        tool_results.add(1, {"tool": tool_name, "has_results": has_results})


def record_resource_access(resource_name: str) -> None:
    """Record a resource read / list access."""
    if resource_accesses is None:
        return
    resource_accesses.add(1, {"resource": resource_name})
