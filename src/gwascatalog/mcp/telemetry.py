"""OpenTelemetry metrics for the GWAS Catalog MCP server."""

from __future__ import annotations

import os
import time

from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server

_METRICS_PORT = int(os.getenv("GWASCATALOG_METRICS_PORT", "9464"))
_initialized = False


def init_telemetry() -> None:
    """Set up the OTel MeterProvider with a Prometheus exporter.

    Starts a Prometheus-compatible ``/metrics`` HTTP endpoint on
    ``GWASCATALOG_METRICS_PORT`` (default 9464).  Safe to call more than once;
    subsequent calls are no-ops.
    """
    global _initialized  # noqa: PLW0603
    if _initialized:
        return

    resource = Resource.create({"service.name": "gwascatalog-mcp"})
    reader = PrometheusMetricReader()
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    set_meter_provider(provider)
    start_http_server(port=_METRICS_PORT)
    _initialized = True


_meter = get_meter_provider().get_meter("gwascatalog.mcp")

# ---- Counters ----

tool_call_counter = _meter.create_counter(
    name="gwascatalog.tool.calls",
    description="Total MCP tool invocations",
    unit="1",
)

tool_result_counter = _meter.create_counter(
    name="gwascatalog.tool.results",
    description="MCP tool invocations partitioned by whether results were returned",
    unit="1",
)

resource_access_counter = _meter.create_counter(
    name="gwascatalog.resource.accesses",
    description="Total MCP resource accesses",
    unit="1",
)

# ---- Histogram ----

tool_duration_histogram = _meter.create_histogram(
    name="gwascatalog.tool.duration",
    description="Tool call duration in seconds",
    unit="s",
)


# ---- Helpers ----


def record_tool_call(
    tool_name: str,
    *,
    result_count: int,
    duration_s: float,
    error: bool = False,
) -> None:
    """Record metrics for a single tool invocation."""
    status = "error" if error else "ok"
    tool_call_counter.add(1, {"tool": tool_name, "status": status})
    tool_duration_histogram.record(duration_s, {"tool": tool_name})
    if not error:
        has_results = "true" if result_count > 0 else "false"
        tool_result_counter.add(1, {"tool": tool_name, "has_results": has_results})


def record_resource_access(resource_name: str) -> None:
    """Record a resource read / list access."""
    resource_access_counter.add(1, {"resource": resource_name})


class ToolTimer:
    """Simple context-manager to measure elapsed wall-clock time."""

    def __init__(self) -> None:
        self.elapsed: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> ToolTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: object) -> None:
        self.elapsed = time.perf_counter() - self._start
