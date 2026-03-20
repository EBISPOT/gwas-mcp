# AGENTS.md

## Project overview

This is a model context protocol (MCP) server for the GWAS Catalog (https://ebi.ac.uk/gwas).
The purpose of this repository is to enable natural language queries of data distributed via
the GWAS Catalog REST API (v2, https://www.ebi.ac.uk/gwas/rest/api/v2/) by providing
 MCP tools, resources, and prompts.

 The project is implemented using Python 3.13, fastmcp v1, and Pydantic v2. uv is used
 for dependency management and nox is used for automation.

 ## Environment setup

 ### Requirements

 * Python 3.13
 * uv installed

### Install dependencies

```
uv sync
```

## Running the project

```
uv run gwas-mcp --transport http
```

## Testing

nox is used to automate tests.

```
uv run nox -s tests
```

## Linting and formatting

nox is used to automate linting and formatting.

```
uv run nox -s lint
```

To fix issues with the linter you might want to run the programs specified in the
noxfile directly (e.g. ruff).

## Project structure

* `gwas-mcp` is a Python namespace package
* It's in the `gwascatalog` namespace (see `pyproject.toml`)

```
.
├── pyproject.toml
├── uv.lock
├── noxfile.py
├── src/
│   └── gwascatalog/
│       └── mcp/
├── docs/
└── tests/
```

## CI expectations

* Run all CI sessions through nox.
* All sessions must pass