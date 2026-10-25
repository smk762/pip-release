# pip-release

pip-release watches PyPI projects, drafts an announcement for each new version, and waits for a person to edit and approve it before anything is published.

Public identities live in YAML or JSON. Tokens and webhook URLs live in `.env`. The first poll records versions that are already on PyPI and does not draft them. Later versions become one draft per enabled platform.

Twitter, Discord, and Telegram publish through their APIs. Patreon's public API does not create posts, so an approved Patreon draft is printed for the creator's editor. After it is posted there, `pip-release confirm` marks it published.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip-release init --example dragonhound
```

`init` copies `examples/dragonhound.yaml` to `config.yaml` and `.env.example` to `.env`. That fixture tracks [dragonhound_dev](https://pypi.org/user/dragonhound_dev/) and names [dragonhound3](https://x.com/dragonhound3) and [AtlasRealms](https://www.patreon.com/c/AtlasRealms). Discord and Telegram are present and disabled until a channel exists. For any other maintainer, run `pip-release init` and edit `config.yaml`.

PyPI documents per-project RSS, not a feed of one user's projects, and the profile page often answers with a client challenge. `pip-release discover` prints project names when the profile is readable. Otherwise keep the explicit `pypi.projects` list.

## Review

Open the queue in a browser:

```bash
pip-release ui
```

That listens on `http://127.0.0.1:8787/`. Drafts are grouped by release. You can edit the text, approve or reject it, and publish from the same page. Saving an edit puts the draft back to pending. Patreon still cannot be created through its API: Publish shows the title and HTML to paste, and “I published this on Patreon” records that you did.

Set `PIP_RELEASE_UI_TOKEN` when the UI is reachable beyond your own machine. Docker’s review service listens inside the container on all interfaces and publishes only `127.0.0.1:8787` on the host, so it requires that token. `PIP_RELEASE_UI_URL` is included in the optional review webhook and printed after `poll` when new drafts appear.

The same actions are available from the shell:

```bash
pip-release poll          # baseline, or draft what is new
pip-release drafts
pip-release show 1
pip-release edit 1        # $EDITOR; the draft returns to pending
pip-release approve 1
pip-release publish 1
pip-release publish --approved --dry-run
```

`pip-release watch` repeats `poll` on `poll.interval_seconds` (at least 60, default 1800). A new draft can also be posted as JSON to `PIP_RELEASE_REVIEW_WEBHOOK`.

Exit status is 1 when a project could not be read. Drafts that fail to publish stay `failed` and can be published again.

## Platforms

| Id | Needs in `.env` | Publish |
| --- | --- | --- |
| `twitter` | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | `POST https://api.x.com/2/tweets` with OAuth 1.0a. Posts are capped at 280 weighted characters, and a URL counts as 23. A post that includes a link is billed at the URL rate on the X developer console. |
| `discord` | `DISCORD_WEBHOOK_URL` | Incoming webhook. The edited text is the message, up to 2000 characters. |
| `telegram` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | `sendMessage` as HTML. The bot must be allowed to post in the channel. |
| `patreon` | none | Prints title and HTML. `pip-release confirm <id>` records that the creator published it. |

`pip-release platforms` prints which destinations are enabled and which secret names are still empty. It does not print secret values.

Set `enabled: false` to keep a platform in the file without drafting for it. A platform omitted from `destinations` is not used. Unknown ids are an error.

## Add a platform

Implement the `Publisher` methods (`render`, `validate`, `missing_secrets`, `publish`) and register an entry point in group `pip_release.platforms`. Then add a `destinations.<id>` block. Built-in publishers live in `src/pip_release/platforms/__init__.py`.

Likely next publishers, in the order they are useful for a Python release: Mastodon, Bluesky, LinkedIn, Slack, Matrix, and an email or RSS handoff. Lemmy, Nostr, and Threads are further out. Mastodon and Bluesky already have maintained release actions elsewhere; this queue still has to own the PyPI poll and the approval step.

## Docker

Copy a config into place first (`pip-release init --example dragonhound` or `cp config.example.yaml config.yaml`), then:

```bash
docker compose up -d --build
docker compose run --rm watcher drafts
```

The review service is on `http://127.0.0.1:8787/` after `PIP_RELEASE_UI_TOKEN` is set in `.env`. The watcher runs as uid 10001 with a read-only root filesystem. Config is mounted read-only. The queue is the `pip-release-data` volume. Secrets come from `.env`.

## Tests

```bash
pytest
```
