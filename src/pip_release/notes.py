"""Best-effort release notes from a GitHub release or a changelog file."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from urllib.parse import quote

from pip_release.http import Http
from pip_release.textutil import clip_lines, extract_changelog

_REPO = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:/|$)"
)
_BLOB = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/blob/([^/]+)/(.+)$"
)
_NOTE_LIMIT = 6000


def find_repo(urls: Mapping[str, str]) -> tuple[str, str] | None:
    preferred = ("Repository", "Source", "Source Code", "Homepage", "Changelog")
    ordered = [urls[key] for key in preferred if key in urls]
    ordered.extend(urls.values())
    for raw in ordered:
        match = _REPO.match(raw.strip())
        if match:
            return match.group(1), match.group(2)
    return None


def changelog_raw_url(urls: Mapping[str, str], owner: str, repo: str) -> str | None:
    for key in ("Changelog", "Changes", "History"):
        raw = (urls.get(key) or "").strip()
        match = _BLOB.match(raw)
        if match and match.group(1) == owner and match.group(2) == repo:
            ref, path = match.group(3), match.group(4)
            return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    return None


def fetch_notes(http: Http, urls: Mapping[str, str], version: str) -> str:
    repo = find_repo(urls)
    if repo is None:
        return ""
    owner, name = repo
    for tag in (version, f"v{version}"):
        url = (
            f"https://api.github.com/repos/{owner}/{name}/releases/tags/"
            f"{quote(tag, safe='')}"
        )
        status, body = http.request(
            "GET",
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        if status != 200:
            continue
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            continue
        text = str(payload.get("body") or "").strip()
        if text:
            return clip_lines(text, _NOTE_LIMIT)
    raw = changelog_raw_url(urls, owner, name)
    if raw is None:
        return ""
    status, body = http.request("GET", raw, headers={"Accept": "text/plain"})
    if status != 200 or len(body) > 1_000_000:
        return ""
    section = extract_changelog(body.decode("utf-8", "replace"), version)
    return clip_lines(section, _NOTE_LIMIT) if section else ""
