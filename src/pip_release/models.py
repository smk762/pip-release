"""Shared records for releases and the review queue."""

from __future__ import annotations

from dataclasses import dataclass

PENDING = "pending"
APPROVED = "approved"
REJECTED = "rejected"
PUBLISHED = "published"
FAILED = "failed"
HANDED_OFF = "handed_off"
PUBLISHING = "publishing"

STATUSES = (PENDING, APPROVED, REJECTED, PUBLISHED, FAILED, HANDED_OFF, PUBLISHING)
DRAFT_FIELDS = {"title", "body", "edited", "note", "external_id", "error"}


@dataclass(frozen=True)
class VersionRef:
    version: str
    yanked: bool
    upload_time: str


@dataclass(frozen=True)
class Release:
    project: str
    version: str
    summary: str
    url: str
    author: str | None
    project_urls: dict[str, str]
    yanked: bool
    notes: str = ""


@dataclass(frozen=True)
class Rendered:
    title: str
    body: str


@dataclass(frozen=True)
class Draft:
    id: int
    project: str
    version: str
    platform: str
    title: str
    body: str
    link: str
    status: str
    edited: bool
    created_at: str
    updated_at: str
    note: str | None
    external_id: str | None
    error: str | None


@dataclass(frozen=True)
class PublishResult:
    external_id: str | None
    detail: str
    handed_off: bool = False
