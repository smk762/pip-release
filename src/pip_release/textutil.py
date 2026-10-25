"""Plain-text fitting for platform limits."""

from __future__ import annotations

import html
import re

_URL = re.compile(r"https?://[^\s]+")
_HEADING = re.compile(r"^##\s+", re.MULTILINE)


def weighted_length(text: str) -> int:
    """X counts each URL as 23 characters, which is the t.co length."""

    total = 0
    pos = 0
    for match in _URL.finditer(text):
        total += match.start() - pos
        total += 23
        pos = match.end()
    total += len(text) - pos
    return total


def clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    if limit < 4:
        return ""
    return text[: limit - 3].rstrip() + "..."


def clip_lines(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    if limit < 4:
        return ""
    cut = text[: limit - 3]
    newline = cut.rfind("\n")
    if newline > limit // 2:
        cut = cut[:newline]
    return cut.rstrip() + "\n..."


def fit_body(head: str, notes: str, link: str, limit: int) -> str:
    """Join a headline, optional notes, and a link without dropping the link."""

    head = " ".join(head.split())
    notes = notes.strip()
    link = link.strip()
    base = "\n\n".join(part for part in (head, link) if part)
    if len(base) > limit:
        room = limit - (len(link) + 2 if link else 0)
        head = clip(head, max(room, 0))
        return "\n\n".join(part for part in (head, link) if part)[:limit]
    if not notes:
        return base
    room = limit - len(base) - 2
    if room < 8:
        return base
    trimmed = clip_lines(notes, room)
    body = "\n\n".join(part for part in (head, trimmed, link) if part)
    if len(body) <= limit:
        return body
    return base


def fit_weighted(head: str, link: str, limit: int = 280) -> str:
    head = " ".join(head.split())
    link = link.strip()
    sep = "\n\n"

    def fits(text: str) -> bool:
        return weighted_length(text) <= limit

    if not head:
        return link
    body = head + sep + link
    if fits(body):
        return body
    while head and not fits(head + sep + link):
        head = head[:-1].rstrip()
    if head:
        space = head.rfind(" ")
        if space > 20:
            shorter = head[:space].rstrip()
            if shorter and fits(shorter + sep + link):
                head = shorter
        return head + sep + link
    return link


def html_text(text: str) -> str:
    return html.escape(text, quote=False)


def plain_to_html(text: str) -> str:
    paragraphs = [part.strip() for part in text.strip().split("\n\n") if part.strip()]
    return "\n".join(
        "<p>" + html_text(part).replace("\n", "<br>\n") + "</p>" for part in paragraphs
    )


def extract_changelog(markdown: str, version: str) -> str:
    """Return the Keep a Changelog section for ``version``, without the heading."""

    heading = re.compile(
        rf"^##\s+\[?{re.escape(version)}\]?.*$",
        re.MULTILINE,
    )
    match = heading.search(markdown)
    if match is None:
        return ""
    rest = markdown[match.end() :]
    nxt = _HEADING.search(rest)
    section = rest[: nxt.start()] if nxt else rest
    return section.strip()
