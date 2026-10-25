"""Server-rendered review queue for drafts."""

from __future__ import annotations

import hmac
import re
import secrets
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import quote, urlsplit

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from pip_release.config import Config, Destination
from pip_release.http import Http, HttpClient, HttpError
from pip_release.models import APPROVED, FAILED, HANDED_OFF, PENDING, PUBLISHING, STATUSES, Draft
from pip_release.platforms import Publisher, load_publishers
from pip_release.store import Store
from pip_release.textutil import plain_to_html
from pip_release.workflow import ReviewError, approve, confirm, edit_draft, publish_draft, reject

_ROOT = Path(__file__).resolve().parent
_OPEN = {PENDING, APPROVED, FAILED, HANDED_OFF, PUBLISHING}
_FILTERS = (
    ("open", "Open"),
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("failed", "Failed"),
    ("handed_off", "Patreon"),
    ("published", "Published"),
    ("all", "All"),
)
_STATUS_LABEL = {
    "pending": "Pending",
    "approved": "Approved",
    "rejected": "Rejected",
    "published": "Published",
    "failed": "Failed",
    "handed_off": "Ready to paste",
    "publishing": "Publishing",
}
_HANDLE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
_PROFILE = {
    "twitter": "https://x.com/{handle}",
    "telegram": "https://t.me/{handle}",
    "patreon": "https://www.patreon.com/c/{handle}",
}


def account_links(config: Config, publishers: Mapping[str, Publisher]) -> dict[str, list[dict[str, str]]]:
    """Public pages for the tracked PyPI identity and enabled destinations."""

    profiles = [
        {"label": user, "href": href}
        for user in config.users
        if (href := _pypi_url("user", user))
    ]
    if not profiles:
        profiles = [
            {"label": project, "href": href}
            for project in config.projects
            if (href := _pypi_url("project", project))
        ]
    destinations: list[dict[str, str]] = []
    for platform, destination in config.destinations.items():
        if not destination.enabled:
            continue
        href = _destination_url(platform, destination)
        if href is None:
            continue
        publisher = publishers.get(platform)
        label = publisher.label if publisher else platform
        handle = _handle(destination.username or destination.name)
        if handle:
            label = f"{label} · {handle}"
        destinations.append({"label": label, "href": href})
    return {"profiles": profiles, "destinations": destinations}


def _pypi_url(kind: str, name: str) -> str | None:
    handle = _handle(name)
    if handle is None:
        return None
    return f"https://pypi.org/{kind}/{quote(handle, safe='')}/"


def _destination_url(platform: str, destination: Destination) -> str | None:
    if destination.url:
        safe = _public_url(destination.url)
        if safe:
            return safe
    handle = _handle(destination.username or destination.name)
    pattern = _PROFILE.get(platform)
    if handle and pattern:
        return pattern.format(handle=quote(handle, safe=""))
    return None


def _handle(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip().lstrip("@")
    if _HANDLE.fullmatch(text):
        return text
    return None


def _public_url(url: str) -> str | None:
    text = url.strip()
    if any(char in text for char in " \t\r\n\"'<>"):
        return None
    parts = urlsplit(text)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return None
    if parts.username or parts.password:
        return None
    return text


def assert_ui_bind(host: str, env: Mapping[str, str]) -> None:
    if host in {"127.0.0.1", "::1", "localhost"}:
        return
    if (env.get("PIP_RELEASE_UI_TOKEN") or "").strip():
        return
    raise PermissionError(
        f"Refusing to listen on {host} without PIP_RELEASE_UI_TOKEN. "
        "The review UI can publish posts."
    )


def create_app(
    config: Config,
    env: Mapping[str, str] | None = None,
    http: Http | None = None,
) -> Starlette:
    settings = dict(env or {})
    secret = (settings.get("PIP_RELEASE_UI_SECRET") or "").strip() or secrets.token_hex(32)
    templates = Jinja2Templates(directory=str(_ROOT / "templates"))
    state = {
        "config": config,
        "env": settings,
        "token": (settings.get("PIP_RELEASE_UI_TOKEN") or "").strip(),
        "http": http,
        "publishers": {item.id: item for item in load_publishers()},
        "templates": templates,
    }

    async def login_form(request: Request) -> Response:
        if not state["token"] or request.session.get("reviewer"):
            return RedirectResponse("/", status_code=303)
        return _render(request, "login.html", error="")

    async def login_submit(request: Request) -> Response:
        form = await request.form()
        if not _csrf_ok(request, form.get("csrf")):
            return _expired()
        given = str(form.get("token") or "")
        if not hmac.compare_digest(given, state["token"]):
            return _render(request, "login.html", error="That token does not match.", status_code=401)
        request.session["reviewer"] = True
        return RedirectResponse("/", status_code=303)

    async def queue(request: Request) -> Response:
        denied = _guard(request, state["token"])
        if denied is not None:
            return denied
        status = request.query_params.get("status") or "open"
        if status not in {item[0] for item in _FILTERS}:
            status = "open"
        with _store(config) as store:
            drafts = _select(store, status)
            groups = _groups(drafts)
        return _render(
            request,
            "queue.html",
            status=status,
            filters=[{"id": key, "label": label} for key, label in _FILTERS],
            groups=groups,
            status_label=_STATUS_LABEL,
        )

    async def draft_page(request: Request) -> Response:
        denied = _guard(request, state["token"])
        if denied is not None:
            return denied
        draft_id = int(request.path_params["draft_id"])
        with _store(config) as store:
            draft = store.get(draft_id)
            if draft is None:
                return _render(request, "missing.html", draft_id=draft_id, status_code=404)
            publisher = state["publishers"].get(draft.platform)
            page = _draft_context(config, draft, publisher)
        return _render(request, "draft.html", **page)

    async def save(request: Request) -> Response:
        return await _act(request, state, "save")

    async def approve_one(request: Request) -> Response:
        return await _act(request, state, "approve")

    async def reject_one(request: Request) -> Response:
        return await _act(request, state, "reject")

    async def publish_one(request: Request) -> Response:
        return await _act(request, state, "publish")

    async def confirm_one(request: Request) -> Response:
        return await _act(request, state, "confirm")

    async def approve_release(request: Request) -> Response:
        denied = _guard(request, state["token"])
        if denied is not None:
            return denied
        form = await request.form()
        if not _csrf_ok(request, form.get("csrf")):
            return _expired()
        project = str(form.get("project") or "")
        version = str(form.get("version") or "")
        try:
            with _store(config) as store:
                pending = [
                    draft
                    for draft in store.list_drafts(project=project, version=version)
                    if draft.status == PENDING
                ]
                for draft in pending:
                    publisher = _publisher(state["publishers"], draft.platform)
                    approve(store, publisher, draft.id, None)
        except (ReviewError, ValueError) as exc:
            _flash(request, "bad", str(exc))
            return RedirectResponse(f"/?status=open", status_code=303)
        count = len(pending)
        noun = "draft" if count == 1 else "drafts"
        _flash(request, "ok", f"Approved {count} {noun} for {project} {version}.")
        return RedirectResponse("/?status=approved", status_code=303)

    routes = [
        Route("/login", login_form, methods=["GET"]),
        Route("/login", login_submit, methods=["POST"]),
        Route("/", queue, methods=["GET"]),
        Route("/drafts/{draft_id:int}", draft_page, methods=["GET"]),
        Route("/drafts/{draft_id:int}/save", save, methods=["POST"]),
        Route("/drafts/{draft_id:int}/approve", approve_one, methods=["POST"]),
        Route("/drafts/{draft_id:int}/reject", reject_one, methods=["POST"]),
        Route("/drafts/{draft_id:int}/publish", publish_one, methods=["POST"]),
        Route("/drafts/{draft_id:int}/confirm", confirm_one, methods=["POST"]),
        Route("/releases/approve", approve_release, methods=["POST"]),
        Mount("/static", app=StaticFiles(directory=str(_ROOT / "static")), name="static"),
    ]
    app = Starlette(routes=routes)
    app.state.templates = templates
    app.state.accounts = account_links(config, state["publishers"])
    app.add_middleware(
        SessionMiddleware,
        secret_key=secret,
        session_cookie="pip_release_review",
        same_site="lax",
        https_only=False,
        max_age=14 * 24 * 60 * 60,
    )
    return app


async def _act(request: Request, state: dict, action: str) -> Response:
    denied = _guard(request, state["token"])
    if denied is not None:
        return denied
    form = await request.form()
    if not _csrf_ok(request, form.get("csrf")):
        return _expired()
    draft_id = int(request.path_params["draft_id"])
    config: Config = state["config"]
    try:
        with _store(config) as store:
            draft = store.get(draft_id)
            if draft is None:
                raise ReviewError(f"No draft {draft_id}")
            publisher = _publisher(state["publishers"], draft.platform)
            message = _perform(store, publisher, draft, form, action, state, config)
    except (ReviewError, ValueError, HttpError, OSError) as exc:
        _flash(request, "bad", str(exc))
        return RedirectResponse(f"/drafts/{draft_id}", status_code=303)
    _flash(request, "ok", message)
    return RedirectResponse(f"/drafts/{draft_id}", status_code=303)


def _perform(store, publisher: Publisher, draft: Draft, form, action: str, state: dict, config: Config) -> str:
    note = str(form.get("note") or "").strip() or None
    if action == "reject":
        reject(store, draft.id, note)
        return f"Rejected {draft.platform} for {draft.project} {draft.version}."
    if action == "confirm":
        confirm(store, draft.id)
        return f"Marked {draft.project} {draft.version} published on Patreon."
    if action == "publish":
        client = state["http"] or HttpClient()
        result = publish_draft(store, publisher, draft, state["env"], client)
        if result.handed_off:
            return f"{draft.project} {draft.version} is ready to paste into Patreon."
        return result.detail
    title = str(form.get("title") if form.get("title") is not None else draft.title)
    body = str(form.get("body") if form.get("body") is not None else draft.body)
    if title != draft.title or body != draft.body:
        draft = edit_draft(store, publisher, draft.id, title, body)
    if action == "save":
        return "Saved. This draft is pending approval."
    approve(store, publisher, draft.id, note)
    return f"Approved {draft.platform} for {draft.project} {draft.version}."


def _draft_context(config: Config, draft: Draft, publisher: Publisher | None) -> dict:
    limit = getattr(publisher, "limit", 10000) if publisher else 10000
    destination = config.destinations.get(draft.platform)
    handoff = None
    if draft.status == HANDED_OFF and draft.platform == "patreon":
        where = destination.url if destination and destination.url else "https://www.patreon.com"
        handoff = {"url": where, "title": draft.title, "html": plain_to_html(draft.body)}
    return {
        "draft": draft,
        "label": publisher.label if publisher else draft.platform,
        "limit": limit,
        "weighted": draft.platform == "twitter",
        "show_title": draft.platform != "twitter",
        "status_label": _STATUS_LABEL.get(draft.status, draft.status),
        "can_edit": draft.status in {PENDING, APPROVED, FAILED},
        "can_approve": draft.status == PENDING,
        "can_publish": draft.status in {APPROVED, FAILED, PUBLISHING},
        "can_reject": draft.status not in {"rejected", "published"},
        "can_confirm": draft.status == HANDED_OFF,
        "handoff": handoff,
    }


def _select(store: Store, status: str) -> list[Draft]:
    if status == "all":
        return store.list_drafts()
    if status == "open":
        return [draft for draft in store.list_drafts() if draft.status in _OPEN]
    if status not in STATUSES:
        return [draft for draft in store.list_drafts() if draft.status in _OPEN]
    return store.list_drafts(status=status)


def _groups(drafts: list[Draft]) -> list[dict]:
    groups: list[dict] = []
    index: dict[tuple[str, str], dict] = {}
    for draft in drafts:
        key = (draft.project, draft.version)
        group = index.get(key)
        if group is None:
            group = {
                "project": draft.project,
                "version": draft.version,
                "link": draft.link,
                "drafts": [],
                "pending": 0,
            }
            index[key] = group
            groups.append(group)
        group["drafts"].append(draft)
        if draft.status == PENDING:
            group["pending"] += 1
    return groups


def _publisher(publishers: Mapping[str, Publisher], platform: str) -> Publisher:
    try:
        return publishers[platform]
    except KeyError as exc:
        raise ReviewError(f"No publisher named {platform}") from exc


class _store:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.store: Store | None = None

    def __enter__(self) -> Store:
        self.store = Store(self.config.store_path)
        return self.store

    def __exit__(self, *exc: object) -> None:
        if self.store is not None:
            self.store.close()


def _guard(request: Request, token: str) -> Response | None:
    if token and not request.session.get("reviewer"):
        return RedirectResponse("/login", status_code=303)
    return None


def _csrf(request: Request) -> str:
    token = request.session.get("csrf")
    if not isinstance(token, str) or not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def _csrf_ok(request: Request, given: object) -> bool:
    expected = request.session.get("csrf")
    if not isinstance(expected, str) or not isinstance(given, str):
        return False
    return hmac.compare_digest(expected, given)


def _flash(request: Request, kind: str, text: str) -> None:
    request.session["flash"] = {"kind": kind, "text": text}


def _render(request: Request, name: str, status_code: int = 200, **context: object) -> HTMLResponse:
    templates: Jinja2Templates = request.app.state.templates
    context["flash"] = request.session.pop("flash", None)
    context["csrf"] = _csrf(request)
    context.setdefault("filters", None)
    context.setdefault("status", "")
    context.setdefault("accounts", getattr(request.app.state, "accounts", None))
    return templates.TemplateResponse(request, name, context, status_code=status_code)


def _expired() -> HTMLResponse:
    return HTMLResponse("This form expired. Reload the page and try again.", status_code=400)
