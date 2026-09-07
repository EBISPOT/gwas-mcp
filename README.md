# GWAS Catalog MCP

A Model Context Protocol (MCP) server that lets AI agents and agentic IDEs
query the [GWAS Catalog](https://www.ebi.ac.uk/gwas/) in plain language —
searching traits, studies, and variant–trait associations from published
genome-wide association studies.

You don't need to install anything. A hosted server is live at:

```
https://ebi.ac.uk/gwas/mcp
```

## Connect

### Claude Code

```bash
claude mcp add --transport http gwas-mcp https://ebi.ac.uk/gwas/mcp
```

Add `--scope user` to make it available in all your projects.

### Codex

Add this to `~/.codex/config.toml`:

```toml
[mcp_servers.gwas-mcp]
url = "https://ebi.ac.uk/gwas/mcp"
```

Any MCP client that supports remote (streamable HTTP) servers can connect using
the same URL.

## What you can ask

The server gives your agent three tools:

| Tool | What it finds |
|------|---------------|
| Traits | EFO traits (diseases, phenotypes) by name, gene, or publication |
| Studies | GWAS studies by trait, ancestry, gene, or accession |
| Associations | Variant–trait associations with statistics (p-value, odds ratio, …) |

It also exposes reference data (ancestry labels, cohort IDs, variant
consequences) that agents use to interpret results.

You don't call these directly — just ask your agent questions like:

- "What EFO trait covers type 2 diabetes?"
- "Find GWAS studies of type 2 diabetes in East Asian cohorts."
- "What variants are associated with LDL cholesterol near the *APOE* gene?"
- "Show the strongest associations for study accession GCST000001."

## Run it yourself

Most people should use the server hosted above.

The best way to test and develop the server locally is to run [MCP Inspector](https://github.com/modelcontextprotocol/inspector) in STDIO mode.

### Kubernetes health checks

The Helm deployment checks a fresh MCP initialisation handshake on the local
HTTP endpoint. Readiness fails after one unsuccessful check; liveness restarts
the container after three consecutive failures. Both run every 30 seconds,
with a 5-second handshake deadline and a 10-second process timeout. Startup
allows approximately 60 seconds, using a startup probe on Kubernetes 1.20+
and initial delays on older clusters.

These probes do not query the REST API. They detect local MCP initialisation
failures; external monitoring is still needed for ingress and public connectivity.

The development endpoint is `https://wwwdev.ebi.ac.uk/gwas/mcp`. Both development
Helm paths are `/gwas/mcp`; an older deployed path containing `/api` requires a
Helm release update using the current values.

## License

Apache-2.0
