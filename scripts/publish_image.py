"""Build AMD64 dev images and promote their exact manifests to release tags."""

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


def alias(source_digest: str, tag: str) -> None:
    run(
        "docker",
        "buildx",
        "imagetools",
        "create",
        "--prefer-index=false",
        "--tag",
        f"{IMAGE}:{tag}",
        f"{IMAGE}@{source_digest}",
    )
    if digest(tag) != source_digest:
        raise RuntimeError(f"{tag} does not match the source image digest")


def build(tag: str) -> None:
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
        f"{IMAGE}:{tag}",
        ".",
    )
    run("docker", "push", f"{IMAGE}:{tag}")


def publish_dev(commit: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or commit != run(
        "git", "rev-parse", "HEAD"
    ):
        raise ValueError(
            "Dev image commit must be the full SHA of the current checkout"
        )
    version = f"dev-{commit}"
    if not exists(version):
        build(version)

    print(f"Dev image: {IMAGE}:{version}")
    print(
        "helm upgrade --install gwas-mcp deployment/helm --namespace gwas-dev "
        f"-f deployment/helm/values-dev.yaml --set-string image.tag={version}"
    )


def publish(tag: str, *, promote: bool = False) -> None:
    version_key(tag)
    version = tag.removeprefix("v")
    metadata = tomllib.loads(Path("pyproject.toml").read_text())
    if metadata["project"]["version"] != version:
        raise ValueError(
            "Release tag must match the application version in pyproject.toml"
        )

    run("git", "fetch", "origin", "main", "--tags")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"],
        check=False,
    ).returncode:
        raise RuntimeError("Release tag must point to a commit reachable from main")

    if not exists(version):
        build(version)

    if not promote:
        return

    # CI holds one resource_group across publishing and promotion. Refresh tags
    # inside that lock so pipeline completion order cannot roll latest backward.
    tags = run("git", "tag", "--list").splitlines()
    versions = {tag.removeprefix("v") for tag in tags if VERSION.fullmatch(tag)}
    versions.add(version)
    latest = next(
        candidate
        for candidate in sorted(versions, key=version_key, reverse=True)
        if exists(candidate)
    )
    selected_digest = digest(latest)
    alias(selected_digest, "latest")
    print(f"Published {version}; latest points to {latest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--promote", action="store_true")
    mode.add_argument("--dev", action="store_true")
    args = parser.parse_args()
    if args.dev:
        publish_dev(args.tag)
    else:
        publish(args.tag, promote=args.promote)
