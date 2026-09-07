#!/usr/bin/env -S uv run
# /// script
# dependencies = ["nox"]
# ///

from __future__ import annotations

import os

import nox

# Use uv for environment creation and package installation
nox.options.default_venv_backend = "uv"
nox.options.sessions = ["lint", "tests"]


@nox.session
def tests(session):
    session.install(".")

    # Install test tooling
    session.install("pytest", "coverage", "pytest-asyncio")

    # Run tests under coverage
    session.run("coverage", "run", "-m", "pytest", "tests")

    # Coverage report (terminal)
    session.run(
        "coverage",
        "report",
        "-m",
        "--fail-under",
        "90",
    )


@nox.session
def lint(session):
    # Install workspace packages (so type checking resolves imports)
    session.install(".")

    # manually install pydantic (this is OK, remember the web app)
    session.install("pydantic")

    # Lint + format + typing tools
    session.install("ruff", "ty")

    # Format check (fails if reformatting needed)
    session.run("ruff", "format", "--check", ".")

    # Lint
    session.run("ruff", "check", ".")

    # Type checking
    # session.run("ty", "check", "src")


@nox.session(venv_backend="none")
def build_image(session: nox.Session) -> None:
    """Build the documentation Docker image and save it as a tarball.

    Usage:  nox -s build_docs_image -- <version>
    Produces: dist/docs-image-<version>.tar
    """
    if not session.posargs:
        session.error("Specify a version, e.g.: nox -s build_image -- 1.2.3")

    version = session.posargs[0]
    local_tag = f"dockerhub.ebi.ac.uk/gwas/gwas-mcp:{version}"

    # IMPORTANT
    # ancient K8S clusters only support legacy media types,
    # so we disable BuildKit's OCI media types to ensure compatibility
    os.environ["BUILDKIT_OCI_MEDIA_TYPES"] = "0"
    session.run(
        "docker",
        "build",
        "--platform",
        "linux/amd64,linux/arm64",
        "--provenance=false",
        "-f",
        "deployment/Dockerfile",
        "-t",
        local_tag,
        ".",
        "--push",
        external=True,
    )


if __name__ == "__main__":
    nox.main()
