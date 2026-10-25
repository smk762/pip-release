"""Read project releases from the PyPI JSON API and profile HTML."""

from __future__ import annotations

import re
from urllib.parse import quote

from pip_release.http import Http, HttpError, read_json
from pip_release.models import Release, VersionRef

PYPI = "https://pypi.org"
_NAME = re.compile(
    r'class="(?:package|project)-snippet__name"[^>]*>\s*([^<]+?)\s*<'
)
_HREF = re.compile(r'href="(?:https://pypi\.org)?/project/([^"/]+)/?"')


class ProfileUnavailable(Exception):
    """The user page was a client challenge, or it listed no projects."""


def project_json_url(name: str, version: str | None = None) -> str:
    safe = quote(name, safe="")
    if version is None:
        return f"{PYPI}/pypi/{safe}/json"
    return f"{PYPI}/pypi/{safe}/{quote(version, safe='')}/json"


def release_page(name: str, version: str) -> str:
    return f"{PYPI}/project/{quote(name, safe='')}/{quote(version, safe='')}/"


def profile_url(username: str) -> str:
    return f"{PYPI}/user/{quote(username, safe='')}/"


def list_versions(http: Http, name: str) -> list[VersionRef]:
    data = read_json(http, project_json_url(name))
    releases = data.get("releases")
    refs: list[VersionRef] = []
    if isinstance(releases, dict) and releases:
        for version, files in releases.items():
            if not isinstance(files, list) or not files:
                continue
            yanked = all(bool(item.get("yanked")) for item in files if isinstance(item, dict))
            times = [
                str(item.get("upload_time_iso_8601") or "")
                for item in files
                if isinstance(item, dict)
            ]
            refs.append(
                VersionRef(
                    version=str(version),
                    yanked=yanked,
                    upload_time=max(times) if times else "",
                )
            )
        return refs
    info = data.get("info") or {}
    version = info.get("version")
    if not version:
        return []
    return [
        VersionRef(
            version=str(version),
            yanked=bool(info.get("yanked")),
            upload_time="",
        )
    ]


def fetch_release(http: Http, name: str, version: str) -> Release:
    try:
        data = read_json(http, project_json_url(name, version))
    except HttpError:
        data = read_json(http, project_json_url(name))
    info = data.get("info") or {}
    urls = info.get("project_urls") or {}
    if not isinstance(urls, dict):
        urls = {}
    project = str(info.get("name") or name)
    found = str(info.get("version") or version)
    return Release(
        project=project,
        version=found if found == version else version,
        summary=str(info.get("summary") or "").strip(),
        url=release_page(project, version),
        author=(str(info["author"]).strip() if info.get("author") else None),
        project_urls={str(key): str(value) for key, value in urls.items() if value},
        yanked=bool(info.get("yanked")),
    )


def parse_profile_projects(html: str) -> list[str]:
    if "Client Challenge" in html or "_fs-ch-" in html:
        raise ProfileUnavailable(
            "PyPI returned a client challenge instead of the profile. "
            "List projects explicitly in the config."
        )
    names = [match.group(1).strip() for match in _NAME.finditer(html)]
    if not names:
        names = [match.group(1).strip() for match in _HREF.finditer(html)]
    deduped: list[str] = []
    seen: set[str] = set()
    for name in names:
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        deduped.append(name)
    if not deduped:
        raise ProfileUnavailable("The profile page listed no projects.")
    return deduped


def discover_projects(http: Http, username: str) -> list[str]:
    status, body = http.request("GET", profile_url(username), headers={"Accept": "text/html"})
    if status != 200:
        raise ProfileUnavailable(f"Profile for {username} returned HTTP {status}.")
    return parse_profile_projects(body.decode("utf-8", "replace"))
