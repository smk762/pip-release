"""Publishers. A new platform is a class plus an entry point."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from importlib.metadata import entry_points
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pip_release.http import Http, send_json
from pip_release.models import Draft, PublishResult, Release, Rendered
from pip_release.oauth1 import authorization_header
from pip_release.textutil import fit_body, fit_weighted, html_text, weighted_length

log = logging.getLogger(__name__)

_ORDER = ("twitter", "discord", "telegram", "patreon")


class Publisher(ABC):
    id: str
    label: str

    @abstractmethod
    def render(self, release: Release) -> Rendered: ...

    @abstractmethod
    def missing_secrets(self, env: Mapping[str, str]) -> list[str]: ...

    @abstractmethod
    def validate(self, title: str, body: str) -> None: ...

    @abstractmethod
    def publish(
        self, draft: Draft, env: Mapping[str, str], http: Http
    ) -> PublishResult: ...


class LengthError(ValueError):
    pass


def _require(env: Mapping[str, str], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if not (env.get(name) or "").strip()]


def _headline(release: Release) -> str:
    summary = release.summary.strip()
    head = f"{release.project} {release.version} is out."
    if summary:
        head = f"{head} {summary}"
    return head


class TwitterPublisher(Publisher):
    id = "twitter"
    label = "Twitter / X"
    limit = 280

    def render(self, release: Release) -> Rendered:
        head = _headline(release)
        return Rendered(title="", body=fit_weighted(head, release.url, self.limit))

    def missing_secrets(self, env: Mapping[str, str]) -> list[str]:
        return _require(
            env,
            ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"),
        )

    def validate(self, title: str, body: str) -> None:
        if weighted_length(body) > self.limit:
            raise LengthError(f"Twitter posts must be {self.limit} weighted characters or fewer")

    def publish(self, draft: Draft, env: Mapping[str, str], http: Http) -> PublishResult:
        missing = self.missing_secrets(env)
        if missing:
            raise LengthError(f"Missing {', '.join(missing)}")
        self.validate(draft.title, draft.body)
        url = "https://api.x.com/2/tweets"
        header = authorization_header(
            "POST",
            url,
            env["X_API_KEY"],
            env["X_API_SECRET"],
            env["X_ACCESS_TOKEN"],
            env["X_ACCESS_TOKEN_SECRET"],
        )
        status, body = send_json(
            http, url, {"text": draft.body}, headers={"Authorization": header}
        )
        if status not in (200, 201):
            raise LengthError(f"Twitter rejected the post with HTTP {status}")
        try:
            payload = json.loads(body.decode("utf-8"))
            external = str((payload.get("data") or {}).get("id") or "") or None
        except json.JSONDecodeError:
            external = None
        return PublishResult(external_id=external, detail="Posted to Twitter / X")


class DiscordPublisher(Publisher):
    id = "discord"
    label = "Discord"
    limit = 2000

    def render(self, release: Release) -> Rendered:
        head = _headline(release)
        body = fit_body(head, release.notes, release.url, self.limit)
        return Rendered(title=f"{release.project} {release.version}", body=body)

    def missing_secrets(self, env: Mapping[str, str]) -> list[str]:
        return _require(env, ("DISCORD_WEBHOOK_URL",))

    def validate(self, title: str, body: str) -> None:
        if len(body) > self.limit:
            raise LengthError(f"Discord posts must be {self.limit} characters or fewer")

    def publish(self, draft: Draft, env: Mapping[str, str], http: Http) -> PublishResult:
        missing = self.missing_secrets(env)
        if missing:
            raise LengthError("Missing DISCORD_WEBHOOK_URL")
        self.validate(draft.title, draft.body)
        url = _discord_url(env["DISCORD_WEBHOOK_URL"])
        status, body = send_json(http, url, {"content": draft.body})
        if status not in (200, 204):
            raise LengthError(f"Discord rejected the post with HTTP {status}")
        external = None
        if body:
            try:
                external = str(json.loads(body.decode("utf-8")).get("id") or "") or None
            except json.JSONDecodeError:
                external = None
        return PublishResult(external_id=external, detail="Posted to Discord")


class TelegramPublisher(Publisher):
    id = "telegram"
    label = "Telegram"
    limit = 4096

    def render(self, release: Release) -> Rendered:
        head = _headline(release)
        # Escaping can grow the text. Leave room for the common entities.
        body = fit_body(head, release.notes, release.url, 3500)
        return Rendered(title=f"{release.project} {release.version}", body=body)

    def missing_secrets(self, env: Mapping[str, str]) -> list[str]:
        return _require(env, ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"))

    def validate(self, title: str, body: str) -> None:
        if len(html_text(body)) > self.limit:
            raise LengthError(f"Telegram posts must be {self.limit} characters or fewer")

    def publish(self, draft: Draft, env: Mapping[str, str], http: Http) -> PublishResult:
        missing = self.missing_secrets(env)
        if missing:
            raise LengthError(f"Missing {', '.join(missing)}")
        self.validate(draft.title, draft.body)
        token = env["TELEGRAM_BOT_TOKEN"].strip()
        if "/" in token or not token:
            raise LengthError("TELEGRAM_BOT_TOKEN is not usable")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        status, body = send_json(
            http,
            url,
            {
                "chat_id": env["TELEGRAM_CHAT_ID"].strip(),
                "text": html_text(draft.body),
                "parse_mode": "HTML",
            },
        )
        if status != 200:
            raise LengthError(f"Telegram rejected the post with HTTP {status}")
        try:
            payload = json.loads(body.decode("utf-8"))
            result = payload.get("result") or {}
            external = str(result.get("message_id") or "") or None
        except json.JSONDecodeError:
            external = None
        return PublishResult(external_id=external, detail="Posted to Telegram")


class PatreonPublisher(Publisher):
    """Patreon's public API does not create posts. Publish hands the text to a person."""

    id = "patreon"
    label = "Patreon"
    limit = 10000

    def render(self, release: Release) -> Rendered:
        head = _headline(release)
        body = fit_body(head, release.notes, release.url, self.limit)
        return Rendered(title=f"{release.project} {release.version}", body=body)

    def missing_secrets(self, env: Mapping[str, str]) -> list[str]:
        return []

    def validate(self, title: str, body: str) -> None:
        if len(title) > 300:
            raise LengthError("Patreon titles must be 300 characters or fewer")
        if len(body) > self.limit:
            raise LengthError(f"Patreon posts must be {self.limit} characters or fewer")

    def publish(self, draft: Draft, env: Mapping[str, str], http: Http) -> PublishResult:
        self.validate(draft.title, draft.body)
        return PublishResult(
            external_id=None,
            detail=(
                "Paste the post into the Patreon editor. "
                f"After it is published there, run pip-release confirm {draft.id}."
            ),
            handed_off=True,
        )


def builtin_publishers() -> list[Publisher]:
    return [
        TwitterPublisher(),
        DiscordPublisher(),
        TelegramPublisher(),
        PatreonPublisher(),
    ]


def load_publishers() -> list[Publisher]:
    found = {publisher.id: publisher for publisher in builtin_publishers()}
    try:
        extras = entry_points(group="pip_release.platforms")
    except Exception:
        extras = ()
    for item in extras:
        try:
            obj = item.load()
            publisher = obj() if isinstance(obj, type) else obj
        except Exception:
            log.warning("Skipping platform entry point %s", item.name, exc_info=True)
            continue
        found[publisher.id] = publisher
    return sorted(
        found.values(),
        key=lambda publisher: (
            _ORDER.index(publisher.id) if publisher.id in _ORDER else 100,
            publisher.id,
        ),
    )


def _discord_url(raw: str) -> str:
    parsed = urlparse(raw.strip())
    if parsed.scheme != "https" or parsed.hostname not in {"discord.com", "discordapp.com"}:
        raise LengthError("DISCORD_WEBHOOK_URL must be a Discord webhook")
    if not parsed.path.startswith("/api/webhooks/"):
        raise LengthError("DISCORD_WEBHOOK_URL must be a Discord webhook")
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["wait"] = "true"
    return urlunparse(parsed._replace(query=urlencode(query)))
