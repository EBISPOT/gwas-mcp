"""Release images are built from protected tags on main."""

from __future__ import annotations

import subprocess

import pytest

from scripts import publish_image as release

COMMIT = "a" * 40


@pytest.mark.parametrize(
    ("published", "tags", "expected"),
    [
        (set(), [], "1.0.2"),
        ({"1.0.1"}, ["v1.0.1"], "1.0.2"),
        ({"1.0.2"}, ["v1.0.2"], "1.0.2"),
        ({"1.9.0", "1.10.0"}, ["v1.9.0", "v1.10.0"], "1.10.0"),
        ({"1.0.2"}, ["v2.0.0", "v3.0.0-rc.1", f"dev-{COMMIT}"], "1.0.2"),
    ],
)
def test_publish_release(monkeypatch, tmp_path, published, tags, expected):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.2"\n')
    images = {version: f"sha256:{version}" for version in published}
    calls = []

    def run(*args):
        calls.append(args)
        if args == ("git", "rev-parse", "HEAD"):
            return COMMIT
        if args == ("git", "tag", "--list"):
            return "\n".join(tags)
        if args[:2] == ("docker", "push"):
            images[args[2].split(":")[-1]] = "sha256:1.0.2"
        if args[:4] == ("docker", "buildx", "imagetools", "create"):
            images[args[-2].split(":")[-1]] = args[-1].split("@")[1]
        return ""

    monkeypatch.setattr(release, "run", run)
    monkeypatch.setattr(
        release.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0),
    )
    monkeypatch.setattr(release, "exists", lambda version: version in images)
    monkeypatch.setattr(release, "digest", images.__getitem__)
    release.publish("v1.0.2")
    built = "1.0.2" not in published
    assert any(call[:3] == ("docker", "buildx", "build") for call in calls) is built
    assert (("docker", "push", f"{release.IMAGE}:1.0.2") in calls) is built
    assert images["latest"] == images[expected]


@pytest.mark.parametrize("already_built", [False, True])
def test_dev_build_is_immutable(monkeypatch, capsys, already_built):
    calls = []

    def run(*args):
        calls.append(args)
        return COMMIT

    monkeypatch.setattr(release, "run", run)
    monkeypatch.setattr(release, "exists", lambda version: already_built)
    release.publish_dev(COMMIT)
    assert (
        any(call[:3] == ("docker", "buildx", "build") for call in calls)
        != already_built
    )
    assert all("imagetools" not in call for call in calls)
    if not already_built:
        build = next(call for call in calls if "build" in call)
        assert build[build.index("--platform") + 1] == "linux/amd64"
        assert ("docker", "push", f"{release.IMAGE}:dev-{COMMIT}") in calls
    output = capsys.readouterr().out
    assert f"--set-string image.tag=dev-{COMMIT}" in output
    assert "helm upgrade" in output


@pytest.mark.parametrize("commit", ["abc", "b" * 40, "../invalid"])
def test_dev_requires_checkout_sha(monkeypatch, commit):
    monkeypatch.setattr(release, "run", lambda *args: COMMIT)
    with pytest.raises(ValueError, match="full SHA"):
        release.publish_dev(commit)


def test_release_requires_main_ancestor(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.2"\n')
    calls = []

    def run(*args):
        calls.append(args)
        return COMMIT

    monkeypatch.setattr(release, "run", run)
    monkeypatch.setattr(
        release.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1),
    )
    with pytest.raises(RuntimeError, match="reachable from main"):
        release.publish("v1.0.2")
    assert ("git", "fetch", "origin", "main", "--tags") in calls


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
    "output",
    [
        "sha256:" + "a" * 64,
        "Name: dockerhub.ebi.ac.uk/gwas/gwas-mcp:1.0.2\n"
        "MediaType: application/vnd.docker.distribution.manifest.v2+json\n"
        "Digest:    sha256:" + "b" * 64,
    ],
)
def test_digest_parses_buildx_output(monkeypatch, output):
    monkeypatch.setattr(release, "run", lambda *args: output)
    assert release.digest("1.0.2") == output.split("Digest:")[-1].strip()


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


def test_latest_verification_failure(monkeypatch):
    monkeypatch.setattr(release, "run", lambda *args: "")
    monkeypatch.setattr(release, "digest", lambda version: "sha256:wrong")
    with pytest.raises(RuntimeError, match="source image digest"):
        release.alias("sha256:expected", "latest")
