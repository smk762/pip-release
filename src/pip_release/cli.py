"""Command line for polling, review, and publish."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

from pip_release.config import (
    Config,
    ConfigError,
    Destination,
    load_config,
    load_env_file,
    resolve_config_path,
)
from pip_release.http import HttpClient, HttpError
from pip_release.models import APPROVED, Draft
from pip_release.platforms import Publisher, load_publishers
from pip_release.pypi import ProfileUnavailable, discover_projects
from pip_release.store import Store
from pip_release.textutil import plain_to_html
from pip_release.workflow import (
    PollEvent,
    ReviewError,
    approve,
    confirm,
    edit_draft,
    notify_review,
    poll,
    publish_draft,
    reject,
)

log = logging.getLogger("pip_release")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.command == "init":
            return cmd_init(args.example, args.force)
        if args.command == "healthcheck":
            return cmd_healthcheck()
        load_env_file(Path(args.env))
        config = load_config(resolve_config_path(args.config))
        if args.store:
            config.store_path = Path(args.store)
        if args.command == "discover":
            return cmd_discover(config)
        if args.command == "ui":
            return cmd_ui(config, args.host, args.port)
        store = Store(config.store_path)
        try:
            return _dispatch(args, config, store)
        finally:
            store.close()
    except (ConfigError, ReviewError, ProfileUnavailable) as exc:
        print(exc, file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


def _dispatch(args: argparse.Namespace, config: Config, store: Store) -> int:
    publishers = _selected(config)
    by_id = {item.id: item for item in load_publishers()}
    http = HttpClient()
    if args.command == "platforms":
        return cmd_platforms(config, by_id, os.environ)
    if args.command == "poll":
        return cmd_poll(config, store, http, publishers)
    if args.command == "watch":
        return cmd_watch(config, store, http, publishers)
    if args.command == "drafts":
        return cmd_drafts(store, args.status)
    if args.command == "show":
        return cmd_show(store, args.id)
    if args.command == "edit":
        return cmd_edit(store, by_id, args.id)
    if args.command == "approve":
        return cmd_approve(store, by_id, _ids(args, store), args.note)
    if args.command == "reject":
        return cmd_reject(store, _ids(args, store), args.note)
    if args.command == "publish":
        return cmd_publish(config, store, by_id, http, _ids(args, store), args.dry_run)
    if args.command == "confirm":
        return cmd_confirm(store, args.id)
    raise ReviewError(f"Unknown command {args.command}")


def cmd_ui(config: Config, host: str, port: int) -> int:
    from pip_release.ui.app import assert_ui_bind, create_app

    try:
        assert_ui_bind(host, os.environ)
    except PermissionError as exc:
        raise ConfigError(str(exc)) from exc
    import uvicorn

    print(f"Review UI at http://{host}:{port}/")
    uvicorn.run(create_app(config, os.environ), host=host, port=port, log_level="info")
    return 0


def cmd_init(example: str | None, force: bool) -> int:
    source = Path("examples/dragonhound.yaml" if example == "dragonhound" else "config.example.yaml")
    if not source.is_file():
        raise ConfigError(f"Missing {source}. Run init from the repository root.")
    _copy(source, Path("config.yaml"), force)
    env_example = Path(".env.example")
    if env_example.is_file():
        _copy(env_example, Path(".env"), force)
    print(f"Wrote config.yaml from {source}")
    return 0


def cmd_discover(config: Config) -> int:
    if not config.users:
        raise ConfigError("Set pypi.user before running discover.")
    http = HttpClient()
    failed = False
    for user in config.users:
        print(f"# {user}")
        try:
            for name in discover_projects(http, user):
                print(f"  - {name}")
        except (ProfileUnavailable, HttpError) as exc:
            print(f"  # {exc}", file=sys.stderr)
            failed = True
    if failed:
        print("List projects explicitly under pypi.projects.", file=sys.stderr)
        return 1
    return 0


def cmd_platforms(
    config: Config, publishers: Mapping[str, Publisher], env: Mapping[str, str]
) -> int:
    if not config.destinations:
        print("No destinations in the config.")
        return 0
    for name, destination in config.destinations.items():
        publisher = publishers.get(name)
        if publisher is None:
            print(f"{name:<12} unknown platform")
            continue
        state = "enabled" if destination.enabled else "disabled"
        who = destination.username or destination.name or ""
        missing = publisher.missing_secrets(env) if destination.enabled else []
        extra = f"  missing {', '.join(missing)}" if missing else ""
        account = f"  {who}" if who else ""
        print(f"{publisher.label:<16} {state:<10}{account}{extra}")
    return 0


def cmd_poll(config: Config, store: Store, http: HttpClient, publishers: list[Publisher]) -> int:
    events = poll(config, store, http, publishers)
    new_ids: list[int] = []
    errors = 0
    for event in events:
        print(_format_event(event))
        new_ids.extend(event.draft_ids)
        if event.kind == "error":
            errors += 1
    drafts = [draft for draft_id in new_ids if (draft := store.get(draft_id))]
    review = (os.environ.get("PIP_RELEASE_UI_URL") or "").strip()
    if drafts and review:
        print(f"Review {review}")
    if drafts:
        try:
            notify_review(http, os.environ, drafts)
        except (HttpError, OSError, ValueError) as exc:
            print(f"Review notification failed: {exc}", file=sys.stderr)
    _heartbeat(config)
    return 1 if errors else 0


def cmd_watch(config: Config, store: Store, http: HttpClient, publishers: list[Publisher]) -> int:
    while True:
        try:
            cmd_poll(config, store, http, publishers)
        except (ConfigError, ReviewError, HttpError, OSError, ValueError) as exc:
            log.error("%s", exc)
            _heartbeat(config)
        time.sleep(config.interval_seconds)


def cmd_drafts(store: Store, status: str | None) -> int:
    drafts = store.list_drafts(status=status)
    if not drafts:
        print("No drafts.")
        return 0
    print(f"{'ID':<6}{'PROJECT':<20}{'VERSION':<16}{'PLATFORM':<12}{'STATUS':<14}EDITED")
    for draft in drafts:
        edited = "yes" if draft.edited else "no"
        print(
            f"{draft.id:<6}{draft.project:<20}{draft.version:<16}"
            f"{draft.platform:<12}{draft.status:<14}{edited}"
        )
    return 0


def cmd_show(store: Store, draft_id: int) -> int:
    draft = _one(store, draft_id)
    _print_draft(draft)
    return 0


def cmd_edit(store: Store, publishers: Mapping[str, Publisher], draft_id: int) -> int:
    draft = _one(store, draft_id)
    publisher = _publisher(publishers, draft.platform)
    original = f"title: {draft.title}\n\n{draft.body}\n"
    path = _temp_path(draft_id)
    path.write_text(original, encoding="utf-8")
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
    completed = subprocess.run([editor, str(path)], check=False)
    if completed.returncode != 0:
        raise ReviewError(f"Editor exited {completed.returncode}. The draft was not changed.")
    title, body = parse_edit(path.read_text(encoding="utf-8"), draft.title)
    edit_draft(store, publisher, draft_id, title, body)
    print(f"Updated draft {draft_id}. It is pending approval.")
    return 0


def cmd_approve(
    store: Store,
    publishers: Mapping[str, Publisher],
    ids: list[int],
    note: str | None,
) -> int:
    for draft_id in ids:
        draft = _one(store, draft_id)
        approve(store, _publisher(publishers, draft.platform), draft_id, note)
        print(f"Approved {draft_id}.")
    return 0


def cmd_reject(store: Store, ids: list[int], note: str | None) -> int:
    for draft_id in ids:
        reject(store, draft_id, note)
        print(f"Rejected {draft_id}.")
    return 0


def cmd_publish(
    config: Config,
    store: Store,
    publishers: Mapping[str, Publisher],
    http: HttpClient,
    ids: list[int],
    dry_run: bool,
) -> int:
    failed = False
    for draft_id in ids:
        draft = _one(store, draft_id)
        publisher = _publisher(publishers, draft.platform)
        if dry_run:
            print(f"# {draft.platform} #{draft.id}")
            if draft.title:
                print(f"title: {draft.title}")
            print(draft.body)
            print()
            continue
        try:
            result = publish_draft(store, publisher, draft, os.environ, http)
        except (ReviewError, OSError, ValueError, HttpError) as exc:
            print(f"Draft {draft_id} failed: {exc}", file=sys.stderr)
            failed = True
            continue
        print(result.detail)
        if result.handed_off:
            print(_handoff(store.get(draft_id) or draft, config.destinations.get(draft.platform)))
    return 1 if failed else 0


def cmd_confirm(store: Store, draft_id: int) -> int:
    confirm(store, draft_id)
    print(f"Marked {draft_id} published.")
    return 0


def cmd_healthcheck() -> int:
    raw = os.environ.get("PIP_RELEASE_HEARTBEAT")
    if not raw:
        print("PIP_RELEASE_HEARTBEAT is not set", file=sys.stderr)
        return 1
    path = Path(raw)
    if not path.is_file():
        print("No heartbeat yet", file=sys.stderr)
        return 1
    stamp, interval = path.read_text(encoding="utf-8").split()
    age = time.time() - float(stamp)
    if age > float(interval) * 2 + 30:
        print(f"Heartbeat is {age:.0f}s old", file=sys.stderr)
        return 1
    return 0


def parse_edit(text: str, previous_title: str) -> tuple[str, str]:
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if lines and lines[0].startswith("title:"):
        title = lines[0].split(":", 1)[1].strip()
        rest = lines[1:]
        if rest and rest[0] == "":
            rest = rest[1:]
        return title, "\n".join(rest).strip()
    return previous_title, normalized.strip()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pip-release",
        description="Draft PyPI release announcements and hold them for approval.",
    )
    parser.add_argument("--config", help="Path to YAML or JSON config. Default: config.yaml")
    parser.add_argument("--env", default=".env", help="Env file for secrets. Existing variables win.")
    parser.add_argument("--store", help="Override the SQLite path")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Copy the example config and .env into place")
    init.add_argument("--example", choices=("dragonhound",), help="Use the dragonhound fixture")
    init.add_argument("--force", action="store_true", help="Replace an existing config.yaml")

    sub.add_parser("discover", help="Print projects from a PyPI user profile")
    sub.add_parser("poll", help="Check PyPI once")
    sub.add_parser("watch", help="Poll on the configured interval")
    sub.add_parser("platforms", help="Show destinations and missing secrets")
    sub.add_parser("healthcheck", help="Exit 0 when the watcher heartbeat is fresh")
    ui = sub.add_parser("ui", help="Open the review UI")
    ui.add_argument("--host", default="127.0.0.1")
    ui.add_argument("--port", type=int, default=8787)

    drafts = sub.add_parser("drafts", help="List drafts")
    drafts.add_argument("--status", choices=("pending", "approved", "rejected", "published", "failed", "handed_off", "publishing"))

    show = sub.add_parser("show", help="Print one draft")
    show.add_argument("id", type=int)

    edit = sub.add_parser("edit", help="Edit a draft in $EDITOR")
    edit.add_argument("id", type=int)

    for name, help_text in (
        ("approve", "Approve drafts"),
        ("reject", "Reject drafts"),
    ):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("ids", nargs="*", type=int)
        command.add_argument("--release", help="project==version")
        command.add_argument("--note")

    publish = sub.add_parser("publish", help="Publish approved drafts")
    publish.add_argument("ids", nargs="*", type=int)
    publish.add_argument("--release", help="project==version")
    publish.add_argument("--approved", action="store_true", help="Every approved draft")
    publish.add_argument("--dry-run", action="store_true", help="Print the post and do not send it")

    confirm_cmd = sub.add_parser("confirm", help="Mark a Patreon handoff as published")
    confirm_cmd.add_argument("id", type=int)
    return parser


def _selected(config: Config) -> list[Publisher]:
    known = {item.id: item for item in load_publishers()}
    selected: list[Publisher] = []
    for name, destination in config.destinations.items():
        if name not in known:
            raise ConfigError(
                f"Unknown platform {name!r}. Installed: {', '.join(sorted(known))}"
            )
        if destination.enabled:
            selected.append(known[name])
    return selected


def _ids(args: argparse.Namespace, store: Store) -> list[int]:
    ids = list(getattr(args, "ids", []) or [])
    if getattr(args, "id", None):
        ids.append(args.id)
    if getattr(args, "approved", False):
        ids.extend(draft.id for draft in store.list_drafts(status=APPROVED))
    release = getattr(args, "release", None)
    if release:
        if "==" not in release:
            raise ReviewError("--release must look like project==version")
        project, version = release.split("==", 1)
        ids.extend(draft.id for draft in store.list_drafts(project=project, version=version))
    deduped = list(dict.fromkeys(ids))
    if not deduped:
        raise ReviewError("Name a draft id, --release, or --approved.")
    return deduped


def _one(store: Store, draft_id: int) -> Draft:
    draft = store.get(draft_id)
    if draft is None:
        raise ReviewError(f"No draft {draft_id}")
    return draft


def _publisher(publishers: Mapping[str, Publisher], platform: str) -> Publisher:
    try:
        return publishers[platform]
    except KeyError as exc:
        raise ReviewError(f"No publisher named {platform}") from exc


def _format_event(event: PollEvent) -> str:
    if event.kind == "baseline":
        return f"baselined {event.project} ({event.detail}); no drafts"
    if event.kind == "draft":
        return f"drafted {event.project} {event.version}: {event.detail}"
    if event.kind == "skip":
        return f"skipped {event.project} {event.version}: {event.detail}"
    return f"error {event.project}: {event.detail}"


def _print_draft(draft: Draft) -> None:
    print(f"#{draft.id}  {draft.project} {draft.version}  {draft.platform}  {draft.status}")
    if draft.title:
        print(f"title: {draft.title}")
    print()
    print(draft.body)
    if draft.error:
        print(f"\nerror: {draft.error}")
    if draft.note:
        print(f"\nnote: {draft.note}")


def _handoff(draft: Draft, destination: Destination | None) -> str:
    where = (destination.url if destination and destination.url else "https://www.patreon.com")
    title = draft.title or f"{draft.project} {draft.version}"
    return (
        f"Paste this into {where}\n\n"
        f"Title:\n{title}\n\n"
        f"{plain_to_html(draft.body)}\n"
    )


def _heartbeat(config: Config) -> None:
    raw = os.environ.get("PIP_RELEASE_HEARTBEAT")
    if not raw:
        return
    path = Path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{time.time():.0f} {config.interval_seconds}\n", encoding="utf-8")


def _copy(source: Path, dest: Path, force: bool) -> None:
    if dest.exists() and not force:
        return
    shutil.copyfile(source, dest)


def _temp_path(draft_id: int) -> Path:
    directory = Path(os.environ.get("TMPDIR") or "/tmp")
    return directory / f"pip-release-{draft_id}.txt"
