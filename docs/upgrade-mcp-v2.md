# MCP Python SDK v2 upgrade plan

Status: Implemented on `codex/mcp-v2-health-checks`; live rollout pending.

## Implementation notes

- SDK dependency and lockfile target 2.1.1; server construction, transport
  settings, annotations, and listing telemetry use the migrated API.
- `gwascatalog.mcp.health` explicitly calls `ClientSession.initialize()` on a
  fresh local connection. It does not substitute SDK v2 discovery for the
  initialization operation that failed in the reported incident.
- Helm uses the agreed readiness and liveness checks, with a startup probe on
  Kubernetes 1.20+ and 60-second initial delays on older clusters.
- Development values already route `/gwas/mcp`; no outdated `/api/mcp` path was
  found in the repository. The expected public URL is documented as
  `https://wwwdev.ebi.ac.uk/gwas/mcp`. Verify the installed Helm release before
  changing a running deployment.
- Regression checks cover real HTTP and stdio initialization, shared client
  lifetime, tool/resource listing and telemetry, a tool call, failed handshakes
  despite successful tools/list, connection failure, and probe exit status.

The agreed plan below is retained as rollout guidance. No live cluster or image
publication has been performed.

## Confirmed scope

- Upgrade the official `modelcontextprotocol/python-sdk` dependency (`mcp`) to
  version 2.1.1. This is not an application release number or a migration to the
  separate `fastmcp` package.
- Add a Kubernetes health check.
- Restart the MCP container after repeated MCP initialization failures. The
  reported incident involved client initialization timing out while an uptime
  check listing tools succeeded; restarting the pod restored service.

## Health check design

The incident establishes recovery by restart, but does not yet establish the
root cause or whether the failure can be reproduced through the pod-local path.
A constant HTTP 200 response or another tools/list check would not specifically
test the reported failure.

Use a Kubernetes exec liveness probe with the installed Python SDK to
open a fresh Streamable HTTP connection to this container's loopback address
and configured MCP path, complete MCP initialization, and close the connection.
Use a bounded deadline and a nonzero exit status on timeout, protocol error, or
invalid initialization response. Do not call the REST API in this restart check.
Kubernetes restarts the container after consecutive failures reach its threshold.

Agreed timing: every 30 seconds, a 5-second initialization deadline, and three
consecutive failures before restart. Default execution allowance: a 10-second
exec timeout allowing Python startup and cleanup.

Agreed readiness behavior: replace the TCP readiness probe with the same fresh
MCP initialization check. Mark the container unready after one failed check and
ready again after one successful check. Liveness independently waits for three
consecutive failures before restarting the container. Neither check depends on
REST API availability.

Agreed startup behavior: use the same initialization check as a startup probe,
with an approximately 60-second startup allowance. Begin normal readiness and
liveness checks immediately after startup succeeds. During implementation,
choose probe timing and thresholds that account for the execution timeout.

A local probe cannot detect failures exclusive to the public ingress or a
particular client/protocol version. Compare the incident client's initialization
behavior only if evidence becomes available; client-specific reproduction is
out of scope at the user's request. Retain external monitoring for the public path.

### Probe defaults

| Probe | Period | Exec timeout | Failure threshold | Success threshold |
| --- | --- | --- | --- | --- |
| Startup | 10 seconds | 10 seconds | 6 | 1 |
| Readiness | 30 seconds | 10 seconds | 1 | 1 |
| Liveness | 30 seconds | 10 seconds | 3 | 1 |

All probes use the same command and 5-second initialization deadline. These
are approximate detection windows, not guaranteed wall-clock recovery times;
termination grace and process startup add to recovery time. Check startup probe
support in the target cluster before rollout: this repository uses a legacy
Ingress API and explicitly mentions old Kubernetes clusters in the image build.
If unsupported, use initial delays for readiness and liveness to provide the
agreed startup allowance rather than requiring a cluster upgrade.

## Current implementation

- `pyproject.toml` requires `mcp[cli]>=1.26.0`; `uv.lock` resolves 1.28.1.
- The server imports `FastMCP` and `Context` from `mcp.server.fastmcp`.
- HTTP uses a stateless Streamable HTTP application, wrapped with a browser
  fallback; stdio is also supported.
- Listing telemetry registers handlers through the private `_mcp_server` attribute.
- The Helm deployment has a TCP readiness probe and no liveness probe.

## Proposed work

1. Audit the v2 migration guide against server creation, context and lifespan,
   HTTP transport, tool and resource registration, telemetry, and test clients.
2. Update the dependency and lockfile to 2.1.1 and migrate affected SDK calls.
3. Preserve existing tools, resources, HTTP path, stdio support, browser fallback,
   and telemetry unless the interview establishes a different requirement.
4. Add one small executable Python module for the initialization probe, reusing
   the installed SDK and existing Settings for the port and MCP path. Connect
   directly to loopback with environment proxies disabled. Run it using the
   container's installed Python, without uv or a shell wrapper. A separate HTTP
   health endpoint is not needed. Wire all three probes into the Helm template.
5. Verify protocol behaviour and health checks; run the lint and tests nox
   sessions, and render the Helm chart for development and production.

## Migration details and acceptance checks

- Replace the removed FastMCP imports with MCPServer and migrate transport
  settings to application construction and server startup. Keep stateless HTTP.
- Account for the shared HTTP lifespan: create and close the REST client once
  per application lifetime and verify concurrent requests can use it correctly.
- Audit the private listing telemetry hooks and update registration as needed;
  preserve counters and existing tool/resource behavior.
- Preserve tool names, input and output schemas, annotations, resource URIs,
  configured HTTP paths, stdio support, and browser fallback behavior. Update
  SDK model field access and test clients where v2 requires it.
- Set the dependency target to `mcp[cli]==2.1.1` and regenerate `uv.lock`. Keep
  the application release version distinct from the SDK version. Update stale
  SDK descriptions in AGENTS.md as part of implementation.
- Exercise real HTTP initialization with fresh connections repeatedly, including
  the deployed `/gwas/mcp` path. Verify listing and one mocked REST-backed tool
  call, plus stdio initialization. Existing unit tests mock Context and do not
  by themselves establish transport compatibility.
- Add a focused regression check where initialization hangs while tools/list
  can still succeed: the health command must fail within its deadline. Also
  verify successful initialization, connection refusal, and protocol errors.
- Confirm probes do not query the REST API and do not fail solely because that
  upstream is unavailable. Bound connection cleanup so a hung close cannot
  leave the probe running indefinitely.
- Run all CI checks through nox: `uv run nox -s lint tests`, including the
  existing coverage threshold. Render and lint the Helm chart with both values
  files and check probe commands, timing, and target-cluster API support.

## Rollout plan

Validate in development first: successful startup, readiness withdrawal on
initialization failure, restart after three failed liveness checks, and recovery
after restart. Use the existing rolling-update strategy. Deploy the same tested
image to production through the normal release process; retain the previous
image and Helm revision for rollback. Image publication and live deployment
are not part of this planning task.

## Sources

- [SDK v2.1.1 release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.1.1)
- [SDK migration guide](https://py.sdk.modelcontextprotocol.io/migration/)
- [Kubernetes probe documentation](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
