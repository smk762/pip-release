"""Poll PyPI and move drafts through review."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field, replace

from pip_release.config import Config, normalize_name
from pip_release.http import Http, HttpError, check_url, send_json
from pip_release.models import (
    APPROVED,
    FAILED,
    HANDED_OFF,
    PENDING,
    PUBLISHED,
    PUBLISHING,
    Draft,
    PublishResult,
)
from pip_release.notes import fetch_notes
from pip_release.platforms import Publisher
from pip_release.pypi import fetch_release, list_versions
from pip_release.store import Store

log = logging.getLogger(__name__)


class ReviewError(Exception):
    pass


@dataclass
class PollEvent:
    kind: str
    project: str
    version: str | None = None
    detail: str = ""
    draft_ids: list[int] = field(default_factory=list)


def tracked_projects(config: Config) -> list[str]:
    ignored = {normalize_name(name) for name in config.ignore}
    return [name for name in config.projects if normalize_name(name) not in ignored]


def poll(
    config: Config,
    store: Store,
    http: Http,
    publishers: list[Publisher],
) -> list[PollEvent]:
    projects = tracked_projects(config)
    if not projects:
        raise ReviewError(
            "No projects to watch. Add pypi.projects. "
            "PyPI does not publish a per-user release feed."
        )
    events: list[PollEvent] = []
    if not publishers:
        for project in projects:
            if not store.is_baselined(project):
                events.extend(_baseline_only(store, http, project))
        events.append(
            PollEvent(
                "error",
                projects[0],
                detail="No destinations are enabled, so new releases were left unseen",
            )
        )
        return events
    for project in projects:
        try:
            versions = list_versions(http, project)
        except (HttpError, OSError, ValueError) as exc:
            events.append(PollEvent("error", project, detail=str(exc)))
            continue
        if not store.is_baselined(project):
            store.baseline(project, [item.version for item in versions])
            latest = versions[-1].version if versions else None
            events.append(
                PollEvent(
                    "baseline",
                    project,
                    latest,
                    detail=_version_count(len(versions)),
                )
            )
            continue
        fresh = [item for item in versions if not store.seen(project, item.version)]
        fresh.sort(key=lambda item: item.upload_time)
        for item in fresh:
            if item.yanked:
                store.mark_seen(project, item.version)
                events.append(PollEvent("skip", project, item.version, detail="yanked"))
                continue
            try:
                events.append(_draft_release(store, http, publishers, project, item.version))
            except (OSError, ValueError) as exc:
                events.append(PollEvent("error", project, item.version, detail=str(exc)))
    return events


def _baseline_only(store: Store, http: Http, project: str) -> list[PollEvent]:
    if store.is_baselined(project):
        return []
    try:
        versions = list_versions(http, project)
    except (HttpError, OSError, ValueError) as exc:
        return [PollEvent("error", project, detail=str(exc))]
    store.baseline(project, [item.version for item in versions])
    return [
        PollEvent(
            "baseline",
            project,
            versions[-1].version if versions else None,
            detail=_version_count(len(versions)),
        )
    ]


def _draft_release(
    store: Store,
    http: Http,
    publishers: list[Publisher],
    project: str,
    version: str,
) -> PollEvent:
    try:
        release = fetch_release(http, project, version)
    except (HttpError, OSError, ValueError) as exc:
        return PollEvent("error", project, version, detail=str(exc))
    if release.yanked:
        store.mark_seen(project, version)
        return PollEvent("skip", project, version, detail="yanked")
    try:
        notes = fetch_notes(http, release.project_urls, release.version)
    except (HttpError, OSError, ValueError):
        log.warning("Release notes for %s %s were skipped", project, version, exc_info=True)
        notes = ""
    release = replace(release, notes=notes)
    ids: list[int] = []
    labels: list[str] = []
    for publisher in publishers:
        rendered = publisher.render(release)
        publisher.validate(rendered.title, rendered.body)
        draft_id, created = store.add_draft(
            project=project,
            version=version,
            platform=publisher.id,
            title=rendered.title,
            body=rendered.body,
            link=release.url,
        )
        if created:
            ids.append(draft_id)
            labels.append(f"{publisher.id} #{draft_id}")
    store.mark_seen(project, version)
    if not ids:
        return PollEvent("skip", project, version, detail="drafts already existed")
    return PollEvent("draft", project, version, detail=", ".join(labels), draft_ids=ids)


def notify_review(http: Http, env: Mapping[str, str], drafts: list[Draft]) -> None:
    url = (env.get("PIP_RELEASE_REVIEW_WEBHOOK") or "").strip()
    if not url or not drafts:
        return
    check_url(url)
    payload = {
        "event": "drafts.created",
        "drafts": [
            {
                "id": draft.id,
                "project": draft.project,
                "version": draft.version,
                "platform": draft.platform,
                "title": draft.title,
                "body": draft.body,
            }
            for draft in drafts
        ],
    }
    review_url = (env.get("PIP_RELEASE_UI_URL") or "").strip()
    if review_url:
        payload["review_url"] = review_url
    status, _body = send_json(http, url, payload)
    if status not in (200, 201, 202, 204):
        raise HttpError("POST", url, status)


def approve(store: Store, publisher: Publisher, draft_id: int, note: str | None) -> Draft:
    draft = _require_draft(store, draft_id)
    publisher.validate(draft.title, draft.body)
    updated = store.transition(
        draft_id, (PENDING,), APPROVED, note=note, error=None
    )
    if updated is None:
        raise ReviewError(f"Draft {draft_id} is {draft.status} and cannot be approved")
    return updated


def reject(store: Store, draft_id: int, note: str | None) -> Draft:
    draft = _require_draft(store, draft_id)
    updated = store.transition(
        draft_id,
        (PENDING, APPROVED, FAILED, HANDED_OFF, PUBLISHING),
        "rejected",
        note=note,
    )
    if updated is None:
        raise ReviewError(f"Draft {draft_id} is {draft.status} and cannot be rejected")
    return updated


def edit_draft(
    store: Store, publisher: Publisher, draft_id: int, title: str, body: str
) -> Draft:
    draft = _require_draft(store, draft_id)
    publisher.validate(title, body)
    updated = store.update_text(draft_id, title, body, (PENDING, APPROVED, FAILED))
    if updated is None:
        raise ReviewError(f"Draft {draft_id} is {draft.status} and cannot be edited")
    return updated


def publish_draft(
    store: Store,
    publisher: Publisher,
    draft: Draft,
    env: Mapping[str, str],
    http: Http,
    *,
    dry_run: bool = False,
) -> PublishResult:
    if draft.status not in (APPROVED, FAILED, PUBLISHING):
        raise ReviewError(
            f"Draft {draft.id} is {draft.status}. Approve it before publishing."
        )
    if dry_run:
        return PublishResult(external_id=None, detail=draft.body, handed_off=publisher.id == "patreon")
    locked = store.transition(draft.id, (APPROVED, FAILED, PUBLISHING), PUBLISHING, error=None)
    if locked is None:
        raise ReviewError(f"Draft {draft.id} changed before it could be published")
    try:
        result = publisher.publish(locked, env, http)
    except Exception as exc:
        store.transition(draft.id, (PUBLISHING,), FAILED, error=str(exc)[:500])
        raise
    status = HANDED_OFF if result.handed_off else PUBLISHED
    store.transition(
        draft.id,
        (PUBLISHING,),
        status,
        external_id=result.external_id,
        error=None,
        note=result.detail if result.handed_off else locked.note,
    )
    return result


def confirm(store: Store, draft_id: int) -> Draft:
    draft = _require_draft(store, draft_id)
    updated = store.transition(draft_id, (HANDED_OFF,), PUBLISHED)
    if updated is None:
        raise ReviewError(
            f"Draft {draft_id} is {draft.status}. Confirm is for a Patreon handoff."
        )
    return updated


def _version_count(count: int) -> str:
    noun = "version" if count == 1 else "versions"
    return f"{count} {noun} already on PyPI"


def _require_draft(store: Store, draft_id: int) -> Draft:
    draft = store.get(draft_id)
    if draft is None:
        raise ReviewError(f"No draft {draft_id}")
    return draft
