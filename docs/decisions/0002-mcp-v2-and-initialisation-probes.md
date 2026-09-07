# Adopt MCP Python SDK v2 and probe MCP initialisation

Date: 2026-09-07

## Status

Accepted

## Context

The GWAS Catalog MCP server used the official MCP Python SDK 1.28.1 and its
bundled FastMCP interface. Moving to SDK 2.1.1 requires changes to server
construction, transport configuration and listing handlers, while preserving
our public MCP contract and stateless HTTP operation.

During a reported incident, MCP client initialisation timed out while an uptime
check listing tools continued to succeed. Restarting the pod restored service.
The existing TCP readiness probe could establish that a port accepted
connections, but could not establish that MCP initialisation worked. Recovery
by restart does not establish the incident's root cause.

The deployment also needs to accommodate older Kubernetes clusters, as noted
in the image build configuration and reflected in the legacy Ingress template.

## Decision

Use the official `mcp[cli]==2.1.1` dependency and migrate to `MCPServer`. Preserve
existing tools, schemas, resource URIs, telemetry, browser fallback and stdio
support. Explicitly set `stateless_http=True`; do not rely on the SDK default.
Reuse the REST client's connection pool through the shared application lifespan
without retaining MCP session state. Release this as application patch 1.0.2;
the SDK's major version does not determine our application's release version.

Use one Python health command for Kubernetes startup, readiness and liveness
probes. Each invocation opens a fresh Streamable HTTP connection to the local
container's configured MCP port and path, explicitly calls
`ClientSession.initialize()`, and closes the connection. Environment proxies
are disabled. SDK v2 discovery is not a substitute for the initialisation
operation that failed in the incident.

The command fails on timeout, protocol error or an invalid initialisation
response. It has a five-second deadline covering the handshake and cleanup;
Kubernetes enforces a ten-second process timeout.

| Probe | Period | Consecutive failures | Consecutive successes |
| --- | --- | --- | --- |
| Startup | 10 seconds | 6 | 1 |
| Readiness | 30 seconds | 1 | 1 |
| Liveness | 30 seconds | 3 | 1 |

A readiness failure removes the pod from service traffic; one successful check
restores readiness. Three consecutive liveness failures trigger a container
restart. Kubernetes 1.20+ uses a startup probe with an approximately 60-second
allowance, ending as soon as it succeeds. Older clusters use 60-second initial
delays for readiness and liveness instead. These are approximate detection
windows; termination and process startup add to recovery time.

The probes do not query the REST API. They assess whether the MCP server can
initialise a connection, since restarting it cannot repair an upstream outage.
Keep external monitoring for the public ingress path.

## Consequences

### Positive

- Retains stateless MCP HTTP operation and the existing public MCP contract.
- Detects local initialisation failures that TCP or tools/list checks can miss.
- Automatically withdraws unhealthy pods from traffic and restarts containers
  after repeated failures, while allowing recovery without a restart.
- Reuses the installed SDK and one probe command without another HTTP endpoint.

### Negative

- Each probe starts a Python process and performs a fresh protocol handshake.
- Local success does not establish public ingress connectivity, REST API
  availability or compatibility with every client.
- Restarting is a recovery mechanism, not a root-cause fix. The reported incident
  has not been reproduced with the original client.
- Older clusters wait the full startup delay even when the server starts quickly.

## References

- [MCP Python SDK v2.1.1 release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.1.1)
- [SDK migration guide](https://py.sdk.modelcontextprotocol.io/migration/)
- [Kubernetes probe documentation](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
