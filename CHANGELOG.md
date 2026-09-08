# Changelog

## Unreleased

- Point the development MCP deployment at the `gwas-rest-api-dev` service.
- Build AMD64 `dev-<commit SHA>` images after successful checks on pushes to
  `dev`, and print the command for manual deployment.
- Promote the matching dev image to release tags without rebuilding; fail if
  the dev image is missing or an existing release points to a different image.

## 1.0.2 - 2026-09-07

- Add GitLab CI checks and AMD64 image publishing for stable release tags,
  with `latest` tracking the highest published stable version.
- Upgrade the MCP Python SDK to 2.1.1 while preserving stateless HTTP, existing
  tools and resources, stdio support and telemetry.
- Add Kubernetes probes that check fresh MCP initialisation, remove unready
  containers from traffic and restart after three consecutive liveness failures.
- Allow approximately 60 seconds for startup, with compatibility for older
  Kubernetes clusters.
- Document the development endpoint as `https://wwwdev.ebi.ac.uk/gwas/mcp`.

## 1.0.1 - 2026-07-03

- Fix broken REST API V2 queries (camel case and broken sort)

## 1.0.0 - 2026-07-01

- Initial release of the GWAS Catalog MCP server.
- Adds tools for querying studies, traits and associations.
- Adds MCP resources for API docs, schemas, indexes and cohort guidance.
- Includes telemetry, HTTP deployment support and Helm configuration.
