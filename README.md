# gwas-mcp

Production-oriented MCP server for GWAS Catalog REST API resources.

## Run (stdio)

```bash
python -m gwas_mcp.server --transport stdio
```

## Run (HTTP streamable)

```bash
GWASCATALOG_HOST=0.0.0.0 GWASCATALOG_PORT=8080 python -m gwas_mcp.server --transport http
```
