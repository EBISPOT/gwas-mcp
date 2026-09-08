# GWAS Catalog MCP

This context describes the language used by the GWAS Catalog MCP server when
separating user-facing MCP concepts from GWAS Catalog REST API details.

## Language

**MCP contract**:
The public tool parameter and response language exposed by this server to MCP
clients, including `ToolResponse.query`. It uses stable, user-facing GWAS
Catalog terms and should not expose REST API naming quirks.
_Avoid_: REST request contract, wire format

**REST request contract**:
The HTTP query parameter and path language required by the GWAS Catalog REST API.
It may include API-specific names that differ from the MCP contract.
_Avoid_: MCP contract

**API workaround**:
A local adaptation that preserves the MCP contract while avoiding incorrect
behaviour in the current GWAS Catalog REST API, such as an upstream 500 error.
_Avoid_: MCP rule
