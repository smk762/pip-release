import re

import pytest
from starlette.testclient import TestClient

from pip_release.cli import main
from pip_release.config import load_config
from pip_release.store import Store
from pip_release.platforms import load_publishers
from pip_release.ui.app import account_links, assert_ui_bind, create_app


def _config(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        """
pypi:
  user: dragonhound_dev
  projects: [argus-atlas]
destinations:
  twitter:
    enabled: true
    username: dragonhound3
  patreon:
    enabled: true
    name: AtlasRealms
    url: https://www.patreon.com/c/AtlasRealms
""",
        encoding="utf-8",
    )
    config = load_config(path)
    config.store_path = tmp_path / "state.sqlite"
    return config


def _seed(config) -> None:
    store = Store(config.store_path)
    store.add_draft(
        project="argus-atlas",
        version="0.2.0",
        platform="twitter",
        title="",
        body="argus-atlas 0.2.0 is out.\n\nhttps://pypi.org/project/argus-atlas/0.2.0/",
        link="https://pypi.org/project/argus-atlas/0.2.0/",
    )
    store.add_draft(
        project="argus-atlas",
        version="0.2.0",
        platform="patreon",
        title="argus-atlas 0.2.0",
        body="argus-atlas 0.2.0 is out.\n\nhttps://pypi.org/project/argus-atlas/0.2.0/",
        link="https://pypi.org/project/argus-atlas/0.2.0/",
    )
    store.close()


def _app(tmp_path, token: str = ""):
    config = _config(tmp_path)
    _seed(config)
    env = {"PIP_RELEASE_UI_SECRET": "test-secret"}
    if token:
        env["PIP_RELEASE_UI_TOKEN"] = token
    return create_app(config, env), config


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def test_queue_lists_the_release_and_save_edits_the_draft(tmp_path):
    app, config = _app(tmp_path)
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert "argus-atlas" in page.text
    assert "0.2.0" in page.text
    assert "Approve 2 pending" in page.text
    assert 'href="https://pypi.org/user/dragonhound_dev/"' in page.text
    assert 'href="https://x.com/dragonhound3"' in page.text
    assert 'href="https://www.patreon.com/c/AtlasRealms"' in page.text
    draft_page = client.get("/drafts/1")
    assert 'href="https://x.com/dragonhound3"' in draft_page.text

    draft = client.get("/drafts/1")
    assert "Post" in draft.text
    updated = "argus-atlas 0.2.0 is out. Smaller note.\n\nhttps://pypi.org/project/argus-atlas/0.2.0/"
    saved = client.post(
        "/drafts/1/save",
        data={"csrf": _csrf(draft.text), "title": "", "body": updated},
        follow_redirects=True,
    )
    assert saved.status_code == 200
    assert "Saved" in saved.text
    store = Store(config.store_path)
    assert store.get(1).body == updated
    assert store.get(1).status == "pending"
    store.close()


def test_approve_publish_and_confirm_patreon(tmp_path):
    app, config = _app(tmp_path)
    client = TestClient(app)
    draft = client.get("/drafts/2")
    client.post(
        "/drafts/2/approve",
        data={"csrf": _csrf(draft.text), "title": "argus-atlas 0.2.0", "body": store_body()},
        follow_redirects=True,
    )
    publish = client.post(
        "/drafts/2/publish",
        data={"csrf": _csrf(client.get("/drafts/2").text)},
        follow_redirects=True,
    )
    assert "Paste into Patreon" in publish.text
    assert "patreon.com/c/AtlasRealms" in publish.text
    confirmed = client.post(
        "/drafts/2/confirm",
        data={"csrf": _csrf(publish.text)},
        follow_redirects=True,
    )
    assert "published on Patreon" in confirmed.text
    store = Store(config.store_path)
    assert store.get(2).status == "published"
    open_queue = client.get("/?status=open")
    assert "/drafts/2" not in open_queue.text
    store.close()


def test_reject_and_missing_csrf(tmp_path):
    app, _config = _app(tmp_path)
    client = TestClient(app)
    draft = client.get("/drafts/1")
    rejected = client.post(
        "/drafts/1/reject",
        data={"csrf": _csrf(draft.text), "note": "hold"},
        follow_redirects=True,
    )
    assert "Rejected" in rejected.text
    assert "hold" in rejected.text
    stale = client.post("/drafts/1/approve", data={"title": "", "body": "x"})
    assert stale.status_code == 400


def test_token_gates_the_queue(tmp_path):
    app, _config = _app(tmp_path, token="s3cret")
    client = TestClient(app, follow_redirects=False)
    assert client.get("/").headers["location"] == "/login"
    login = client.get("/login")
    bad = client.post("/login", data={"csrf": _csrf(login.text), "token": "nope"})
    assert bad.status_code == 401
    good = client.post(
        "/login",
        data={"csrf": _csrf(bad.text), "token": "s3cret"},
        follow_redirects=False,
    )
    assert good.status_code == 303
    assert client.get("/").status_code == 200


def test_account_links_skip_disabled_channels_and_unsafe_urls(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        """
pypi:
  projects: [argus-atlas]
destinations:
  twitter:
    enabled: true
    username: "@dragonhound3"
  discord:
    enabled: false
    url: https://discord.com/channels/1/2
  telegram:
    enabled: true
    username: atlas_news
    url: "javascript:alert(1)"
  patreon:
    enabled: true
    name: AtlasRealms
    url: https://user:secret@www.patreon.com/c/AtlasRealms
""",
        encoding="utf-8",
    )
    config = load_config(path)
    links = account_links(config, {item.id: item for item in load_publishers()})
    assert links["profiles"] == [
        {"label": "argus-atlas", "href": "https://pypi.org/project/argus-atlas/"}
    ]
    hrefs = [item["href"] for item in links["destinations"]]
    assert hrefs == [
        "https://x.com/dragonhound3",
        "https://t.me/atlas_news",
        "https://www.patreon.com/c/AtlasRealms",
    ]
    assert all("discord" not in href for href in hrefs)
    assert all("secret" not in href for href in hrefs)


def test_public_bind_requires_a_token():
    with pytest.raises(PermissionError, match="PIP_RELEASE_UI_TOKEN"):
        assert_ui_bind("0.0.0.0", {})
    assert_ui_bind("127.0.0.1", {})
    assert_ui_bind("0.0.0.0", {"PIP_RELEASE_UI_TOKEN": "x"})


def test_cli_refuses_a_public_ui_without_a_token(tmp_path, capsys):
    path = tmp_path / "config.yaml"
    path.write_text("pypi:\n  projects: [demo]\ndestinations: {}\n", encoding="utf-8")
    code = main(
        [
            "--config",
            str(path),
            "--env",
            str(tmp_path / "missing.env"),
            "ui",
            "--host",
            "0.0.0.0",
        ]
    )
    assert code == 2
    assert "PIP_RELEASE_UI_TOKEN" in capsys.readouterr().err


def store_body() -> str:
    return "argus-atlas 0.2.0 is out.\n\nhttps://pypi.org/project/argus-atlas/0.2.0/"
