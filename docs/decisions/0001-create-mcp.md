# Create a Model Context Protocol server for the GWAS Catalog

Date: 2026-03-13

## Status

Accepted

## Context

We want to make it easier for people to explore the GWAS Catalog using natural language queries. With the recent release of the [v2 REST API](https://www.ebi.ac.uk/gwas/rest/api/v2/docs/reference) now is a good time to do this. Other teams at EMBL-EBI are also deploying MCP servers to enable natural language queries.

Some unofficial GWAS Catalog MCP servers have been created from our OpenAPI schema but we would like to develop and deploy our own. An important part of MCP development is evaluation and benchmarking: making sure that agents are actually using the published tools is critical. Developing our own server will simplify this.

## Decision

We will create a MCP server using a supported MCP SDK in Python. Tools will represent common user research tasks (e.g. searching traits, exploring variant associations, finding studies).

We will create 5 - 8 high-level representing common GWAS exploration workflows. The GWAS Catalog is commonly used to answer questions like:

* what genetic variants are associated with a trait?
* what studies exist for a trait?
* what genes are implicated?

tools which mirror the API but don't expose internal REST  details. MCP and REST are different and should be configured differently.

Top-level REST API resources will be exposed using MCP tool primitives, because the API server does compute to filter and summarise GWAS Catalog data.

## Consequences

### Positive

* Enables natural language exploration of the GWAS Catalog
* Provides an officially supported MCP interface
* Simplifies evaluation of tool use and agent behaviour
* Aligns the GWAS Catalog with other MCP deployments at EMBL-EBI

### Negative

* The bioinformatics team will be responsible for maintaining the MCP server
* Tool schemas may need to evolve as MCP usage patterns become clearer