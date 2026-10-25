import json
from datetime import datetime, timedelta, timezone

import pytest

from pip_release.config import Destination, load_config
from pip_release.models import APPROVED, HANDED_OFF, PENDING, PUBLISHED, Draft
from pip_release.platforms import (
    DiscordPublisher,
    PatreonPublisher,
    TwitterPublisher,
    load_publishers,
)
from pip_release.store import Store
from pip_release.workflow import (
    ReviewError,
    approve,
    desktop_notice,
    poll,
    publish_draft,
    reject,
    reminder_due,
)


class FakeHttp:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []

    def request(self, method, url, body=None, headers=None):
        self.calls.append((method, url, body, headers or {}))
        key = (method, url.split("?", 1)[0])
        if key in self.payloads:
            status, payload = self.payloads[key]
            if isinstance(payload, bytes):
                return status, payload
            return status, json.dumps(payload).encode()
        return 404, b"{}"


def project_json(*versions, yanked=()):
    releases = {}
    for index, version in enumerate(versions):
        releases[version] = [
            {
                "yanked": version in yanked,
                "upload_time_iso_8601": f"2026-01-{index + 1:02d}T00:00:00Z",
            }
        ]
    latest = versions[-1]
    return {
        "info": {
            "name": "argus-atlas",
            "version": latest,
            "summary": "Bake tiles",
            "author": "smk762",
            "yanked": False,
            "project_urls": {"Homepage": "https://example.com/atlas"},
        },
        "releases": releases,
    }


def routes(*versions, yanked=()):
    body = project_json(*versions, yanked=yanked)
    found = {
        ("GET", "https://pypi.org/pypi/argus-atlas/json"): (200, body),
    }
    for version in versions:
        found[("GET", f"https://pypi.org/pypi/argus-atlas/{version}/json")] = (200, body)
    return found


def config(tmp_path, enabled=("twitter", "patreon")):
    destinations = {}
    for name in ("twitter", "discord", "telegram", "patreon"):
        item = {"enabled": name in enabled}
        if name == "twitter":
            item["username"] = "dragonhound3"
        if name == "patreon":
            item["name"] = "AtlasRealms"
            item["url"] = "https://www.patreon.com/c/AtlasRealms"
        destinations[name] = item
    path = tmp_path / "config.yaml"
    path.write_text(
        "pypi:\n  user: dragonhound_dev\n  projects: [argus-atlas]\n"
        "destinations:\n"
        + "\n".join(
            f"  {name}:\n    enabled: {'true' if item['enabled'] else 'false'}"
            + (f"\n    username: {item['username']}" if "username" in item else "")
            + (f"\n    name: {item['name']}" if "name" in item else "")
            + (f"\n    url: {item['url']}" if "url" in item else "")
            for name, item in destinations.items()
        ),
        encoding="utf-8",
    )
    loaded = load_config(path)
    loaded.store_path = tmp_path / "state.sqlite"
    return loaded


def publishers():
    by_id = {item.id: item for item in load_publishers()}
    return [by_id["twitter"], by_id["patreon"]]


def test_builtin_platforms_are_the_four_starters():
    assert [item.id for item in load_publishers()] == [
        "twitter",
        "discord",
        "telegram",
        "patreon",
    ]


def test_first_poll_baselines_and_the_next_poll_drafts(tmp_path):
    cfg = config(tmp_path)
    store = Store(cfg.store_path)
    http = FakeHttp(routes("0.1.0"))
    first = poll(cfg, store, http, publishers())
    assert [event.kind for event in first] == ["baseline"]
    assert store.list_drafts() == []

    http.payloads = routes("0.1.0", "0.2.0")
    second = poll(cfg, store, http, publishers())
    assert [event.kind for event in second] == ["draft"]
    drafts = store.list_drafts()
    assert [(draft.platform, draft.status) for draft in drafts] == [
        ("twitter", "pending"),
        ("patreon", "pending"),
    ]
    assert drafts[0].body.endswith("https://pypi.org/project/argus-atlas/0.2.0/")
    assert "Bake tiles" in drafts[0].body

    third = poll(cfg, store, http, publishers())
    assert third == []
    store.close()


def test_yanked_versions_are_not_drafted(tmp_path):
    cfg = config(tmp_path)
    store = Store(cfg.store_path)
    http = FakeHttp(routes("0.1.0"))
    poll(cfg, store, http, publishers())
    http.payloads = routes("0.1.0", "0.2.0", yanked={"0.2.0"})
    events = poll(cfg, store, http, publishers())
    assert [(event.kind, event.detail) for event in events] == [("skip", "yanked")]
    assert store.list_drafts() == []
    store.close()


def test_publish_requires_approval_and_patreon_is_a_handoff(tmp_path):
    cfg = config(tmp_path)
    store = Store(cfg.store_path)
    http = FakeHttp(routes("0.1.0"))
    poll(cfg, store, http, publishers())
    http.payloads = routes("0.1.0", "0.2.0")
    poll(cfg, store, http, publishers())
    patreon = next(draft for draft in store.list_drafts() if draft.platform == "patreon")
    twitter = next(draft for draft in store.list_drafts() if draft.platform == "twitter")
    with pytest.raises(ReviewError, match="Approve"):
        publish_draft(store, PatreonPublisher(), patreon, {}, http)
    approve(store, PatreonPublisher(), patreon.id, None)
    result = publish_draft(store, PatreonPublisher(), store.get(patreon.id), {}, http)
    assert result.handed_off is True
    assert store.get(patreon.id).status == HANDED_OFF
    assert http.calls[-1][0] == "GET"

    approve(store, TwitterPublisher(), twitter.id, None)
    http.payloads[("POST", "https://api.x.com/2/tweets")] = (
        201,
        {"data": {"id": "99"}},
    )
    env = {
        "X_API_KEY": "k",
        "X_API_SECRET": "s",
        "X_ACCESS_TOKEN": "t",
        "X_ACCESS_TOKEN_SECRET": "ts",
    }
    posted = publish_draft(store, TwitterPublisher(), store.get(twitter.id), env, http)
    assert posted.external_id == "99"
    assert store.get(twitter.id).status == PUBLISHED
    method, url, _body, headers = http.calls[-1]
    assert method == "POST"
    assert url == "https://api.x.com/2/tweets"
    assert headers["Authorization"].startswith("OAuth ")
    store.close()


def test_rejected_draft_is_not_pending(tmp_path):
    cfg = config(tmp_path)
    store = Store(cfg.store_path)
    http = FakeHttp(routes("1"))
    poll(cfg, store, http, publishers())
    http.payloads = routes("1", "2")
    poll(cfg, store, http, publishers())
    draft = store.list_drafts()[0]
    reject(store, draft.id, "not this one")
    assert store.get(draft.id).status != PENDING
    with pytest.raises(ReviewError):
        approve(store, TwitterPublisher(), draft.id, None)
    store.close()


def test_discord_webhook_must_be_discord():
    publisher = DiscordPublisher()
    draft = store_draft_like()
    with pytest.raises(ValueError, match="Discord"):
        publisher.publish(draft, {"DISCORD_WEBHOOK_URL": "https://example.com/hook"}, FakeHttp({}))


def store_draft_like():
    from pip_release.models import Draft

    return Draft(
        id=1,
        project="demo",
        version="1",
        platform="discord",
        title="demo 1",
        body="hello",
        link="https://pypi.org/project/demo/1/",
        status=APPROVED,
        edited=False,
        created_at="",
        updated_at="",
        note=None,
        external_id=None,
        error=None,
    )


def test_destination_round_trip_unused():
    assert Destination(enabled=False).enabled is False


def test_desktop_notice_groups_a_release_and_includes_the_review_url():
    first = store_draft_like()
    second = Draft(
        id=2,
        project="demo",
        version="1",
        platform="twitter",
        title="",
        body="tweet",
        link=first.link,
        status=PENDING,
        edited=False,
        created_at="",
        updated_at="",
        note=None,
        external_id=None,
        error=None,
    )
    notice = desktop_notice([first, second], "http://127.0.0.1:8787/")
    assert notice is not None
    summary, body = notice
    assert summary == "2 PyPI drafts waiting"
    assert body == "demo 1\nhttp://127.0.0.1:8787/"
    assert desktop_notice([], "") is None
    still = desktop_notice([first], "http://127.0.0.1:8787/", still_waiting=True)
    assert still is not None
    assert still[0] == "PyPI draft still waiting"


def test_reminder_is_due_after_24_hours():
    now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
    assert reminder_due(None, now) is True
    assert reminder_due("not-a-date", now) is True
    recent = (now - timedelta(hours=23, minutes=59)).isoformat()
    assert reminder_due(recent, now) is False
    due = (now - timedelta(hours=24)).isoformat()
    assert reminder_due(due, now) is True
