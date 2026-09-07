"""Publish AMD64 releases and promote the highest published stable Git tag."""

from __future__ import annotations

import argparse
import re
import subprocess
import tomllib
from pathlib import Path

IMAGE = "dockerhub.ebi.ac.uk/gwas/gwas-mcp"
VERSION = re.compile(r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def version_key(tag: str) -> tuple[int, ...]:
    match = VERSION.fullmatch(tag)
    if match is None:
        raise ValueError(f"Expected a stable SemVer tag, got {tag!r}")
    return tuple(map(int, match.groups()))


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def digest(version: str) -> str:
    return run(
        "docker",
        "buildx",
        "imagetools",
        "inspect",
        f"{IMAGE}:{version}",
        "--format",
        "{{.Manifest.Digest}}",
    )


def exists(version: str) -> bool:
    result = subprocess.run(
        ["docker", "manifest", "inspect", f"{IMAGE}:{version}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return True
    if (
        "manifest unknown" in result.stderr.lower()
        or "no such manifest" in result.stderr.lower()
    ):
        return False
    raise RuntimeError(f"Could not inspect {IMAGE}:{version}: {result.stderr}")


def publish(tag: str, *, promote: bool = False) -> None:
    version_key(tag)
    version = tag.removeprefix("v")
    metadata = tomllib.loads(Path("pyproject.toml").read_text())
    if metadata["project"]["version"] != version:
        raise ValueError(
            "Release tag must match the application version in pyproject.toml"
        )

    if not exists(version):
        run(
            "docker",
            "buildx",
            "build",
            "--platform",
            "linux/amd64",
            "--provenance=false",
            "--output",
            "type=docker,oci-mediatypes=false",
            "-f",
            "deployment/Dockerfile",
            "-t",
            f"{IMAGE}:{version}",
            ".",
        )
        run("docker", "push", f"{IMAGE}:{version}")

    if not promote:
        return

    # CI holds one resource_group across publishing and promotion. Refresh tags
    # inside that lock so pipeline completion order cannot roll latest backward.
    run("git", "fetch", "origin", "--tags")
    tags = run("git", "tag", "--list").splitlines()
    versions = {tag.removeprefix("v") for tag in tags if VERSION.fullmatch(tag)}
    versions.add(version)
    latest = next(
        candidate
        for candidate in sorted(versions, key=version_key, reverse=True)
        if exists(candidate)
    )
    selected_digest = digest(latest)
    run(
        "docker",
        "buildx",
        "imagetools",
        "create",
        "--prefer-index=false",
        "--tag",
        f"{IMAGE}:latest",
        f"{IMAGE}@{selected_digest}",
    )
    if digest("latest") != selected_digest:
        raise RuntimeError("latest does not match the selected release digest")
    print(f"Published {version}; latest points to {latest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()
    publish(args.tag, promote=args.promote)
