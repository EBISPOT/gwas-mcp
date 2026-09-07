"""Release selection must not depend on pipeline completion order."""

from __future__ import annotations

import subprocess

import pytest

from scripts import publish_image as release


@pytest.mark.parametrize(
    ("published", "tags", "expected", "build"),
    [
        (set(), [], "1.0.2", True),
        ({"1.0.1"}, ["v1.0.1"], "1.0.2", True),
        ({"1.0.2"}, ["v1.0.2"], "1.0.2", False),
        ({"1.9.0", "1.10.0"}, ["v1.9.0", "v1.10.0"], "1.10.0", True),
        ({"1.0.2"}, ["v2.0.0", "v3.0.0-rc.1"], "1.0.2", False),
    ],
)
def test_publish_and_promote(monkeypatch, tmp_path, published, tags, expected, build):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.2"\n')
    calls = []

    def run(*args):
        calls.append(args)
        if args[:3] == ("git", "tag", "--list"):
            return "\n".join(tags)
        if args[:2] == ("docker", "push"):
            published.add(args[-1].split(":")[-1])
        return ""

    monkeypatch.setattr(release, "run", run)
    monkeypatch.setattr(release, "exists", lambda version: version in published)
    monkeypatch.setattr(release, "digest", lambda version: f"sha256:{expected}")
    release.publish("v1.0.2", promote=True)
    assert any(call[:3] == ("docker", "buildx", "build") for call in calls) == build
    assert (
        "docker",
        "buildx",
        "imagetools",
        "create",
        "--prefer-index=false",
        "--tag",
        f"{release.IMAGE}:latest",
        f"{release.IMAGE}@sha256:{expected}",
    ) in calls
    assert ("git", "fetch", "origin", "--tags") in calls


def test_version_validation(monkeypatch, tmp_path):
    assert release.version_key("v1.10.0") > release.version_key("1.9.0")
    for tag in ("latest", "v1.0.0-rc.1", "01.0.0", "1.0.0+build", "v1.2"):
        with pytest.raises(ValueError, match="stable SemVer"):
            release.version_key(tag)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.1"\n')
    with pytest.raises(ValueError, match="application version"):
        release.publish("v1.0.2")


@pytest.mark.parametrize(
    ("code", "error", "expected"),
    [
        (0, "", True),
        (1, "manifest unknown", False),
        (1, "no such manifest", False),
        (1, "unauthorized", None),
        (1, "connection refused", None),
    ],
)
def test_registry_errors_are_not_missing_images(monkeypatch, code, error, expected):
    monkeypatch.setattr(
        release.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, code, "", error),
    )
    if expected is None:
        with pytest.raises(RuntimeError, match="Could not inspect"):
            release.exists("1.0.2")
    else:
        assert release.exists("1.0.2") is expected


def test_promotion_verification_failure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.2"\n')
    monkeypatch.setattr(release, "run", lambda *args: "v1.0.2")
    monkeypatch.setattr(release, "exists", lambda version: True)
    monkeypatch.setattr(release, "digest", lambda version: version)
    with pytest.raises(RuntimeError, match="release digest"):
        release.publish("v1.0.2", promote=True)
