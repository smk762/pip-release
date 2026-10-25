import json

import pytest

from pip_release.config import ConfigError, load_config, load_env_file, normalize_name
from pip_release.pypi import ProfileUnavailable, list_versions, parse_profile_projects
from pip_release.textutil import (
    extract_changelog,
    fit_body,
    fit_weighted,
    weighted_length,
)


def test_normalize_name_treats_separators_as_equal():
    assert normalize_name("Argus_Atlas") == normalize_name("argus-atlas")


def test_yaml_rejects_secret_keys(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        "pypi:\n  projects: [demo]\ndestinations:\n  discord:\n    webhook_url: https://example\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="secret"):
        load_config(path)


def test_json_config_and_interval_floor(tmp_path, monkeypatch):
    monkeypatch.delenv("PIP_RELEASE_STORE", raising=False)
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "pypi": {"user": "ada", "projects": ["Demo", "demo"]},
                "destinations": {"twitter": {"enabled": True, "username": "ada"}},
                "poll": {"interval_seconds": 5},
            }
        ),
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.users == ["ada"]
    assert config.projects == ["Demo"]
    assert config.interval_seconds == 60
    assert config.destinations["twitter"].enabled is True


def test_env_file_does_not_override(tmp_path):
    path = tmp_path / ".env"
    path.write_text('export X_API_KEY="from-file"\n# comment\nEMPTY\n', encoding="utf-8")
    environ = {"X_API_KEY": "already"}
    load_env_file(path, environ)
    assert environ["X_API_KEY"] == "already"


def test_dragonhound_fixture_enables_twitter_and_patreon():
    config = load_config_from_repo()
    assert config.users == ["dragonhound_dev"]
    assert config.projects == [
        "argus-atlas",
        "argus-lens",
        "argus-cortex",
        "argus-quarry",
        "argus-forge",
        "argus-proof",
        "argus-curator",
    ]
    assert config.destinations["twitter"].username == "dragonhound3"
    assert config.destinations["patreon"].url.endswith("AtlasRealms")
    assert config.destinations["discord"].enabled is False
    assert config.destinations["telegram"].enabled is False


def load_config_from_repo():
    from pathlib import Path

    return load_config(Path("examples/dragonhound.yaml"))


def test_profile_parser_reads_snippet_names():
    html = """
    <a class="package-snippet" href="/project/argus-atlas/">
      <span class="package-snippet__name">argus-atlas</span>
    </a>
    <a class="package-snippet" href="/project/argus-atlas/">
      <span class="package-snippet__name">argus-atlas</span>
    </a>
    <span class="project-snippet__name">argus-lens</span>
    """
    assert parse_profile_projects(html) == ["argus-atlas", "argus-lens"]


def test_profile_challenge_is_not_a_project_list():
    with pytest.raises(ProfileUnavailable, match="client challenge"):
        parse_profile_projects("<title>Client Challenge</title>")


def test_changelog_section_stops_at_the_next_heading():
    text = """
## [Unreleased]

## [0.2.0a1] - 2026-10-25

### Added

- chunk baking

## [0.1.0a1] - 2026-10-23

- first
"""
    assert extract_changelog(text, "0.2.0a1") == "### Added\n\n- chunk baking"


def test_weighted_length_counts_a_url_as_23():
    text = "hi https://pypi.org/project/argus-atlas/0.2.0a1/"
    assert weighted_length(text) == len("hi ") + 23


def test_fit_body_keeps_the_link():
    body = fit_body("Hello", "n" * 5000, "https://pypi.org/project/demo/1/", 200)
    assert body.endswith("https://pypi.org/project/demo/1/")
    assert len(body) <= 200


def test_fit_weighted_stays_inside_280():
    body = fit_weighted("demo 1 is out. " + ("word " * 200), "https://pypi.org/p/1", 280)
    assert weighted_length(body) <= 280
    assert body.endswith("https://pypi.org/p/1")


def test_list_versions_skips_empty_and_flags_yanked():
    payload = {
        "info": {"version": "2"},
        "releases": {
            "1": [{"yanked": False, "upload_time_iso_8601": "2026-01-01T00:00:00Z"}],
            "2": [{"yanked": True, "upload_time_iso_8601": "2026-02-01T00:00:00Z"}],
            "3": [],
        },
    }

    class Http:
        def request(self, method, url, body=None, headers=None):
            return 200, json.dumps(payload).encode()

    refs = {item.version: item for item in list_versions(Http(), "demo")}
    assert set(refs) == {"1", "2"}
    assert refs["2"].yanked is True
    assert refs["1"].yanked is False
