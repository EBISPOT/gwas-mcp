"""Release selection must not depend on pipeline completion order."""

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
def test_publish_and_promote(monkeypatch, tmp_path, published, tags, expected):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.2"\n')
    images = {version: f"sha256:{version}" for version in published}
    images[f"dev-{COMMIT}"] = "sha256:1.0.2"
    calls = []

    def run(*args):
        calls.append(args)
        if args == ("git", "rev-parse", "HEAD"):
            return COMMIT
        if args == ("git", "tag", "--list"):
            return "\n".join(tags)
        if args[:4] == ("docker", "buildx", "imagetools", "create"):
            images[args[-2].split(":")[-1]] = args[-1].split("@")[1]
        return ""

    monkeypatch.setattr(release, "run", run)
    monkeypatch.setattr(release, "exists", lambda version: version in images)
    monkeypatch.setattr(release, "digest", images.__getitem__)
    release.publish("v1.0.2", promote=True)
    assert not any(call[:3] == ("docker", "buildx", "build") for call in calls)
    assert images["1.0.2"] == images[f"dev-{COMMIT}"]
    assert images["latest"] == images[expected]
    assert ("git", "fetch", "origin", "--tags") in calls


@pytest.mark.parametrize("already_built", [False, True])
def test_dev_build_is_immutable_and_never_promotes(monkeypatch, capsys, already_built):
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


@pytest.mark.parametrize("missing", [True, False])
def test_release_refuses_missing_dev_image_or_conflicting_release(
    monkeypatch, tmp_path, missing
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.2"\n')
    calls = []

    def run(*args):
        calls.append(args)
        return COMMIT

    monkeypatch.setattr(release, "run", run)
    monkeypatch.setattr(release, "exists", lambda version: not missing)
    monkeypatch.setattr(release, "digest", lambda version: version)
    with pytest.raises(RuntimeError, match="Missing" if missing else "Refusing"):
        release.publish("v1.0.2", promote=True)
    assert calls == [("git", "rev-parse", "HEAD")]


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


def test_promotion_verification_failure(monkeypatch):
    monkeypatch.setattr(release, "run", lambda *args: "")
    monkeypatch.setattr(release, "digest", lambda version: "sha256:wrong")
    with pytest.raises(RuntimeError, match="source image digest"):
        release.alias("sha256:expected", "latest")
