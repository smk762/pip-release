# Open-source release announcement bots and CI

Research date: 25 October 2026. Scope is open-source GitHub Actions, self-hosted bots, and the few hosted products that showed up while looking for the comparison target: notice a release, draft platform-specific posts, hold them for a human to edit and approve, then publish. Platforms checked: Twitter/X, Mastodon, Bluesky, Discord, Telegram, Slack, generic webhooks, and Patreon. Sources are repository READMEs, GitHub repository metadata, GitHub Marketplace pages, GitLab docs, and PyPI docs. Vendor marketing pages are labeled as such.

No single open-source project found here implements that full comparison target. The maintained open-source actions post immediately from caller-supplied text. Human review shows up in adjacent tools (GitHub draft releases, pull-request tweet files, one project-specific LLM queue, and a Patreon browser filler), not inside the social posting actions.

## Which GitHub Actions or bots post a GitHub or GitLab release to Twitter/X, Mastodon, Bluesky, Discord, Telegram, Slack, or a webhook?

### Takeaway

Maintained open-source posters are per-platform or Apprise-based, and they post when a workflow calls them, usually on GitHub `release: published`. Release Drafter and `action-gh-release` only create the GitHub release. GitLab ships native Discord and Telegram integrations. Patreon has no release-to-post action; one project says the official API cannot create posts.

### Cited Findings

Twitter/X:

- `ethomson/send-tweet-action` sends a caller-supplied `status` string using consumer key, consumer secret, access token, and access-token secret. The README example triggers on `push`, not on a release. Latest release is v1.0.0 (2019-12-31). Last push 2023-03-04. MIT. 83 stars, 11 open issues. — [Repository metadata and README](https://github.com/ethomson/send-tweet-action)
- Marketplace page for `snow-actions/tweet` says to create a Twitter app and “Generate Twitter API v1.1 tokens. (Not Twitter API v2).” The sample posts `Released ${{ github.event.release.name }}` plus the release URL. — [Tweet action marketplace page](https://github.com/marketplace/actions/tweet-action)
- `snow-actions/tweet` last push 2023-04-21, MIT, 56 stars, 3 open issues, description “Tweet to Twitter via GitHub Actions.” — [Repository metadata](https://github.com/snow-actions/tweet)
- `nearform-actions/github-action-notify-twitter` is described as a GitHub action that can send a custom message to a Twitter account. Last push 2026-10-16. License field is null. 14 stars, 6 open issues. — [Repository metadata](https://github.com/nearform-actions/github-action-notify-twitter)
- On `ethomson/send-tweet-action` issue #28 (open, created 2023-04-25, updated 2025-05-06), commenters said they moved to `nearform-actions/github-action-notify-twitter` because it could use v2 endpoints. One commenter on 2024-07-26 reported HTTP 403 from that action; another on 2024-08-06 said it worked. On 2025-05-06 a commenter wrote that send-tweet-action “no longer works since the previous API is no longer supported.” — [Issue #28](https://github.com/ethomson/send-tweet-action/issues/28)
- A Singlewire product notice says X announced deprecation of v1 API endpoints effective 30 April 2025, and that Singlewire’s Twitter connector would stop. This is a vendor notice about Singlewire’s product, not a test of the GitHub Actions above. — [Singlewire deprecation notice](https://singlewire.my.site.com/s/article/Deprecation-Notice-Outbound-System-Twitter)
- `twitter-together/action` publishes tweets from `*.tweet` files added under `tweets/` when those files are pushed to the default branch. Pull requests get a length check and a preview check. It is not wired to a release event. Last push 2024-10-16. MIT. 716 stars, 34 open issues. — [README via search](https://github.com/twitter-together/action); [repository metadata](https://api.github.com/repos/twitter-together/action)
- A consuming workflow for `sizls/broadcast-action` at pin v0.11.9 lists platforms `bluesky,mastodon,discord,linkedin,twitter,facebook` and runs on `release: types: [published]`. It forwards `TWITTER_BEARER_TOKEN`. The same file says Instagram was removed in CLI v0.2.1. This is a downstream workflow comment, not the upstream README. — [directive broadcast.yml](https://github.com/directive-run/directive/blob/45ea65a9ec08455929400685dc1226e1a88a009c/.github/workflows/broadcast.yml)

Mastodon:

- `cbrgm/mastodon-github-action` posts a caller-supplied `message` to a Mastodon instance. Required inputs are `url` and `access-token`; `message` is required unless `media-paths` is set. Optional: `visibility`, `sensitive`, `spoiler-text`, `language`, `scheduled-at`, media. It can also run as a container (`ghcr.io/cbrgm/mastodon-github-action`). Apache-2.0. Last push 2026-10-22. 39 stars, 1 open issue. The README does not mention GitHub releases. — [README](https://github.com/cbrgm/mastodon-github-action); [repository metadata](https://api.github.com/repos/cbrgm/mastodon-github-action)
- `cbrgm/gopodder` calls that action on `release: published` with a message built from repository name, release name, and release URL, pinned to v2.2.0. — [gopodder notify.yml](https://github.com/cbrgm/gopodder/blob/main/.github/workflows/notify.yml)

Bluesky:

- Marketplace page for `myConsciousness/bluesky-post` documents `myConsciousness/bluesky-post@v6`. Inputs include `text`, `identifier`, `password` (app password recommended), optional `service`, and media, video, reply, and quote. It posts to Bluesky from whatever event the workflow uses; the quick start is `on: [push]`. — [Send Bluesky Post marketplace page](https://github.com/marketplace/actions/send-bluesky-post)
- Repository metadata: BSD-3-Clause, last push 2026-08-16, 46 stars, 0 open issues. A fetched copy of the main README still shows `@v5` examples, while the marketplace page and a July 2026 changelog bump describe v6. — [Repository metadata](https://api.github.com/repos/myConsciousness/bluesky-post); [README still showing v5](https://github.com/myConsciousness/bluesky-post/blob/main/README.md); [v5-to-v6 bump notes](https://github.com/hectorespert/som-energia-hass/pull/61)
- WeakAuras posts the same generated text with `myConsciousness/bluesky-post@v5` on `release: published` and `workflow_dispatch`. — [WeakAuras release_notifications.yml](https://github.com/WeakAuras/WeakAuras2/blob/ccfbf553/.github/workflows/release_notifications.yml)

Discord:

- `sarisia/actions-status-discord` description is “Post GitHub Actions status to Discord as an beautiful embed.” MIT. Last push 2026-05-08. 284 stars, 11 open issues. — [Repository metadata](https://api.github.com/repos/sarisia/actions-status-discord)
- A third-party guide shows that action on `release: published`, passing webhook, title, description from `github.event.release.body`, URL, and color. That is the guide’s example, not the action README. — [Promotion Agent GitHub automation](https://ava-agent.github.io/promotion-agent/guide/github-automation.html)
- Marketplace page for `SethCohen/github-releases-to-discord` says it sends a Discord embed of a GitHub release description on `release: published`, with cleanup of the release body (carriage returns, HTML comments, mentions, optional removal of PR and issue links, heading reduction, embed length trimming). — [Github Releases To Discord](https://github.com/marketplace/actions/github-releases-to-discord)
- WeakAuras uses `tsickert/discord-webhook@v7.0.0` to send an embed whose description is a generated changelog. — [WeakAuras release_notifications.yml](https://github.com/WeakAuras/WeakAuras2/blob/ccfbf553/.github/workflows/release_notifications.yml)
- GitLab’s Discord Notifications integration posts selected GitLab events to a Discord webhook (`https://discord.com/api/webhooks/...`). The fetched page says to select event checkboxes and does not list the event names. Webhook URL validation is noted as introduced in GitLab 18.0. — [GitLab Discord notifications](https://docs.gitlab.com/user/project/integrations/discord_notifications/)

Telegram:

- Marketplace page for `tyagdit/release-telegram-action` says it cleans up GitHub-generated release notes and sends `github.event.release.body` to a Telegram channel. Example trigger is `release: types: published`. It says it only works on Linux runners and that cleanup is specific to notes from `.github/release.yml`. — [Release Telegram Action](https://github.com/marketplace/actions/release-telegram-action)
- `cbrgm/gopodder` calls `cbrgm/telegram-github-action` at commit pin labeled v1.4.0 on `release: published`, with a message of release name, tag, actor, repository, and HTML URL. — [gopodder notify.yml](https://github.com/cbrgm/gopodder/blob/main/.github/workflows/notify.yml)
- `sinspired/multi-release-notify` sends to Telegram via an Apprise URL `tgram://bot_token/chat_id`, and the quick start triggers on `release: published`. It also lists Slack, email, Bark, ntfy, and DingTalk, plus any Apprise URL. — [README](https://github.com/sinspired/multi-release-notify)
- GitLab’s Telegram integration sends selected GitLab events to a bot token and channel identifier. The fetched page does not list event names. Hostname override for a local Bot API server is noted as introduced in GitLab 17.1. — [GitLab Telegram](https://docs.gitlab.com/user/project/integrations/telegram/)

Slack and generic webhooks:

- `multi-release-notify` has a `slack_url` input (`slack://xoxb-token/#general`) and a generic `urls` input. Its generic example includes `discord://webhook_id/webhook_token`. — [README](https://github.com/sinspired/multi-release-notify)
- `nikhilbadyal/release-tracker` notifies through Apprise and documents Discord, Slack, Telegram, email, Pushover, and Microsoft Teams URL schemes. It says Apprise supports 80+ services. — [release-tracker README excerpt](https://github.com/nikhilbadyal/release-tracker)
- Project workflows post a release string with `curl` to Discord and Slack incoming webhooks on `release: published`, with no shared action. One of them states X is omitted and should be posted by hand. — [InnerWarden announce-release.yml](https://github.com/InnerWarden/innerwarden/blob/main/.github/workflows/announce-release.yml); [great_cto announce.yml](https://github.com/avelikiy/great_cto/blob/main/.github/workflows/announce.yml)

GitHub release notes only, not social posts:

- `release-drafter/release-drafter` “Drafts your next release notes as pull requests are merged into master.” It updates a GitHub draft release. ISC. Last push 2026-10-24. 3947 stars, 41 open issues. — [README](https://github.com/release-drafter/release-drafter/); [repository metadata](https://api.github.com/repos/release-drafter/release-drafter)
- `softprops/action-gh-release` creates GitHub releases. MIT. Last push 2026-10-24. 5782 stars, 123 open issues. Inputs include `body`, `body_path`, `draft` (default false), and `generate_release_notes`. No social-network inputs appear in the documented input table. — [README input table](https://github.com/softprops/action-gh-release/); [repository metadata](https://api.github.com/repos/softprops/action-gh-release)

GitLab and multi-forge watchers:

- `release-tracker` documents a GitHub watcher (GitHub REST API), a GitLab watcher (GitLab API, `base_url` default `https://gitlab.com/api/v4`), and a PyPI watcher (package name, no authentication). Notifications go out through Apprise. — [release-tracker README excerpt](https://github.com/nikhilbadyal/release-tracker)

Patreon:

- No GitHub Action was found that publishes a software release as a Patreon post.
- `Shynixn/PatreonPostApi` states: “The official Patreon API does not provide POST actions for creating or publishing posts,” and that Selenium-style automation is typically blocked by Cloudflare. Its workaround is a Chrome extension running in a logged-in browser session. — [PatreonPostApi README](https://github.com/Shynixn/PatreonPostApi)
- `IqbalZarar-Khan/DISBot` listens to Patreon webhooks and posts into Discord, including `posts:publish`. That is Patreon-to-Discord, not a software release to Patreon. — [DISBot README](https://github.com/IqbalZarar-Khan/DISBot)

Hosted products that match the comparison shape, not identified as open source:

- SocialHandoff’s site says a GitHub Action or signed webhook sends a published release, an agent drafts per-network posts, and a person approves in an inbox before publish. Named networks on those pages: X, Bluesky, LinkedIn, Mastodon. No source repository or license was found. — [Release announcements](https://socialhandoff.com/use-cases/release-announcements/); [GitHub releases help](https://socialhandoff.com/help/github-releases/); [Mastodon approval page](https://socialhandoff.com/integrations/github-actions/mastodon/)
- Ship 2 Post’s site says a GitHub App detects a release, tag, or merge, drafts channel-native copy, and holds it in a review queue. No source repository was found, and the page does not name Discord, Telegram, or Patreon. — [Ship 2 Post](https://s2p.dev/auto-post-github-releases-to-social-media)
- A third-party directory describes NewReleases as a service that tracks GitHub, GitLab, PyPI, and other registries and notifies by email, Slack, Telegram, Discord, and custom webhooks, among other chat tools. The directory page does not call it open source and does not mention X, Mastodon, Bluesky, Patreon, templates beyond filtering, or an approval step. — [NewReleases directory listing](https://www.webfolio.to/tools/newreleases)

### Inferences

- The reusable open-source layer is “post this string,” not “turn this release into a social announcement.” Release awareness lives in the workflow trigger (`on: release`) or in a poller (`release-tracker`, PyPI RSS bots).
- Adding Discord or Slack is a webhook. Adding Telegram is a bot token plus chat id, or an Apprise `tgram://` URL. Adding Mastodon or Bluesky means a separate maintained action; the Apprise examples in these READMEs do not list them. Adding X means dealing with API-version and billing breakage. Adding Patreon means there is no official create-post API, according to PatreonPostApi.
- A downstream workflow can fan one release event out to several of these actions. WeakAuras, gopodder, and the directive broadcast workflow are examples. That composition is not itself a productized bot.

### Gaps

- Upstream README, license, and last commit were not fetched for `sizls/broadcast-action`, `SethCohen/github-releases-to-discord`, `tyagdit/release-telegram-action`, `tsickert/discord-webhook`, `cbrgm/telegram-github-action`, or `nearform-actions/github-action-notify-twitter` (metadata only). Whether the October 2026 nearform push still successfully posts to X was not verified.
- GitLab’s Discord and Telegram docs say to select events, but the fetched pages do not name “release” as a checkbox. Slack, Mastodon, Bluesky, and X were not confirmed as native GitLab release integrations.
- No Marketplace page was found for a dedicated Slack release action. Slack coverage here is Apprise URLs and hand-written webhook steps.
- SocialHandoff, Ship 2 Post, and NewReleases were not confirmed open source. Their feature claims are vendor or directory copy.
- Current X API price and which write endpoints still exist in October 2026 were not taken from an X developer page.

## Do any generate the text with templates or an LLM, or do they only forward the release title and body?

### Takeaway

The open-source actions either post text the workflow already wrote, or format the existing release title and body. Template engines exist for GitHub release notes and for Apprise messages. LLM drafting showed up in vendor products and in one project’s own workflow, not in the Marketplace actions whose READMEs were read.

### Cited Findings

- `cbrgm/mastodon-github-action` posts the `message` input unchanged. There is no release-body or template input in the README. — [README](https://github.com/cbrgm/mastodon-github-action)
- `myConsciousness/bluesky-post` posts the `text` input. It extracts mentions, links, and tags into Bluesky facets. The marketplace page does not describe summarizing a release. — [Marketplace page](https://github.com/marketplace/actions/send-bluesky-post)
- `snow-actions/tweet` and `ethomson/send-tweet-action` post a `status` string supplied by the workflow. Examples interpolate `github.event.release.name` and the release URL. — [Tweet action marketplace page](https://github.com/marketplace/actions/tweet-action); [send-tweet-action README](https://github.com/ethomson/send-tweet-action)
- `SethCohen/github-releases-to-discord` forwards the release description after cleanup and optional link stripping. That is formatting, not generation of new copy. — [Marketplace page](https://github.com/marketplace/actions/github-releases-to-discord)
- `tyagdit/release-telegram-action` sends `github.event.release.body` after cleanup aimed at GitHub-generated notes. — [Marketplace page](https://github.com/marketplace/actions/release-telegram-action)
- `multi-release-notify` auto-generates a title such as `owner/repo updated to v1.2.0` and release notes from commit subjects between the previous tag and HEAD, with per-channel formatting (email HTML, Telegram HTML, Slack markdown). Callers can override `title` and `message`, or supply repository-local template files such as `telegram_template`. The README does not mention an LLM. — [README](https://github.com/sinspired/multi-release-notify)
- Release Drafter fills a GitHub release body from merged pull requests using `template`, `category-template`, `change-template`, `name-template`, and `tag-template`. That text is the GitHub release notes, not a social post. — [README](https://github.com/release-drafter/release-drafter/)
- `action-gh-release` can set `body`, load `body_path`, or set `generate_release_notes` so GitHub generates the name and body. Again, that is the GitHub release, not a social post. — [README](https://github.com/softprops/action-gh-release/)
- WeakAuras runs `./generate_changelog.sh` and `.github/scripts/generate_twitter_post.py`, then posts that text to Discord, Twitter, Mastodon, and Bluesky. The workflow file shows a local script, not an LLM API. — [release_notifications.yml](https://github.com/WeakAuras/WeakAuras2/blob/ccfbf553/.github/workflows/release_notifications.yml)
- `alex-jb/orallexa-marketing-agent` `.github/workflows/release-announce.yml` runs `marketing_agent generate` with `ANTHROPIC_API_KEY`, `--platforms x bluesky mastodon`, `--mode hybrid`, and `--variants 3`, using the release body and up to five changelog bullets. — [release-announce.yml](https://github.com/alex-jb/orallexa-marketing-agent/blob/main/.github/workflows/release-announce.yml)
- SocialHandoff’s site says an agent reads the release body and drafts a thread for X and Bluesky, a single LinkedIn post, and a Mastodon post sized to 500 characters, using “brand memory.” This is a vendor description. — [Release announcements](https://socialhandoff.com/use-cases/release-announcements/)
- Ship 2 Post’s site says it “drafts channel-native copy in your brand voice.” Vendor description; the page does not say which model. — [Ship 2 Post](https://s2p.dev/auto-post-github-releases-to-social-media)
- `pypi-notifier` sends a Discord notification when a polled RSS feed has a new version. The project page does not describe rewriting the release text. — [PyPI project page](https://pypi.org/project/pypi-notifier/)
- `xnuinside/pypi_tools_bot` notifies Telegram when a tracked package has a new PyPI release. The README describes the alert, not generated announcement copy. — [README](https://github.com/xnuinside/pypi_tools_bot)
- DISBot’s site says Discord messages support custom templates with placeholders. Those templates announce Patreon posts, not software releases. — [DISBot site](https://disbot.site/)

### Inferences

- Platform-specific length and formatting, where it exists, is mechanical: Bluesky facets, Discord embed trimming, Telegram HTML, Mastodon `scheduled-at` and visibility. None of the action READMEs read here ask an LLM to rewrite a changelog into a short post per network.
- The orallexa workflow is the only public source found that both reads a GitHub release and calls an LLM. It is that project’s marketing agent, with platforms hardcoded to X, Bluesky, and Mastodon in the workflow, not a Marketplace action.

### Gaps

- `release-tracker`’s retrieved README excerpt shows Apprise `format: text|markdown|html` and does not mention templates beyond that or an LLM. The full README was not opened, so a template feature could exist further down the file.
- Prompt text, model name, and output shape for orallexa’s `marketing_agent generate` were not read. Only the workflow invocation was.
- SocialHandoff and Ship 2 Post do not document model, temperature, or the exact prompt in the pages fetched.

## Is there a human approval or edit step before publish, or do they post immediately when a tag or release is created?

### Takeaway

The social and chat actions post immediately when the job runs. Their READMEs do not include a draft, edit, or approve input. Approval exists beside them: GitHub draft releases, pull-request review for twitter-together, a git folder queue in one LLM workflow, GitHub environment reviewers as a general Actions feature, and a Patreon browser extension that can wait for a human to click Post.

### Cited Findings

- Mastodon action inputs are credentials, message, visibility, sensitivity, language, `scheduled-at`, and media. `scheduled-at` must be at least 5 minutes in the future. There is no dry-run or approval input. — [README](https://github.com/cbrgm/mastodon-github-action)
- Bluesky marketplace inputs are the post content, credentials, and media or reply fields. The quick start posts on the workflow trigger. No approval input is listed. — [Marketplace page](https://github.com/marketplace/actions/send-bluesky-post)
- Tweet, Discord release, and Telegram release examples all use `on: release: types: [published]` and then send. None of those Marketplace pages describe holding the message for edit. — [Tweet action](https://github.com/marketplace/actions/tweet-action); [Github Releases To Discord](https://github.com/marketplace/actions/github-releases-to-discord); [Release Telegram Action](https://github.com/marketplace/actions/release-telegram-action)
- `multi-release-notify` says “If a `*_url` exists, it is sent automatically.” The quick start is `release: published`. No approval input is in the input tables. — [README](https://github.com/sinspired/multi-release-notify)
- Release Drafter keeps a draft GitHub release “ready to publish when you’re ready.” Action input `publish` immediately publishes that GitHub release. Action input `dry-run` (default false) performs no writes and logs what it would have done. The README also notes some users set `publish: true` so a prerelease goes out “without the need for human intervention.” This gate is for the GitHub release, not a social post. — [README](https://github.com/release-drafter/release-drafter/)
- `action-gh-release` `draft` defaults to false. “When reusing an existing draft release, set this to true to keep it draft; omit it to publish after upload.” — [README](https://github.com/softprops/action-gh-release/)
- twitter-together’s approval step is GitHub pull-request review. On pull request it validates length and posts a preview check. On push to the default branch it publishes each new `*.tweet` file. The tweet body is the file contents, written by a person before merge. — [README](https://github.com/twitter-together/action)
- orallexa’s release workflow commits drafts to `queue/pending/` and tells a maintainer to `git mv` the file to `queue/approved/` and push. A separate `publish.yml` is described as what sends approved files. The workflow opens a GitHub issue with those instructions. — [release-announce.yml](https://github.com/alex-jb/orallexa-marketing-agent/blob/main/.github/workflows/release-announce.yml)
- GitHub documents environment required reviewers: a person or team must approve a workflow job that targets that environment before the job continues. This is a platform feature, not an input of the posting actions. A 2021 article shows using it to approve publishing a GitHub release and npm packages, not social posts. — [GitHub environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments); [Aaron Powell, 2021](https://www.aaron-powell.com/posts/2021-01-11-using-environments-for-approval-workflows-with-github/)
- SocialHandoff’s site says the action “does not publish on its own,” the draft appears in an inbox, and a reviewer can edit inline, approve, or reject. Vendor claim. — [GitHub releases help](https://socialhandoff.com/help/github-releases/); [Release announcements](https://socialhandoff.com/use-cases/release-announcements/)
- Ship 2 Post’s site says copy is held in a review queue and “Approve once and it publishes.” Vendor claim. — [Ship 2 Post](https://s2p.dev/auto-post-github-releases-to-social-media)
- PatreonPostApi’s Chrome extension has **Auto-submit** (fills the form and clicks Post) and **Background fetch** (fills the form and waits). The README says to leave both disabled so the user reviews the filled post and clicks Post. It also warns Patreon website changes can break auto-submit. — [README](https://github.com/Shynixn/PatreonPostApi)
- `pypi-notifier` sends when a newer version is detected. The project page does not describe a confirmation step. On first launch it sends nothing until a later update. — [PyPI project page](https://pypi.org/project/pypi-notifier/)
- A directive workflow comment says GitHub releases created with `GITHUB_TOKEN` do not fire downstream `release: [published]` workflows, so an announce workflow can stay dormant unless dispatched another way. That is a trigger caveat, not an approval feature. — [directive broadcast.yml](https://github.com/directive-run/directive/blob/45ea65a9ec08455929400685dc1226e1a88a009c/.github/workflows/broadcast.yml)

### Inferences

- The comparison target’s “hold, edit, then publish” step is absent from the Marketplace posting actions. The closest open-source assemblies are: (1) Release Drafter or `draft: true` so a human publishes the GitHub release, after which immediate posters fire, and (2) orallexa’s pending/approved git queue, which does allow editing the generated posts before publish, for X, Bluesky, and Mastodon only.
- Putting a posting job in a GitHub environment with required reviewers would pause the job before it posts, but the reviewer would approve the workflow run, not edit the post body in an inbox. That behavior is GitHub’s, and none of the action READMEs document it.
- Mastodon `scheduled-at` delays publication. It does not open the text for editing.

### Gaps

- Whether `sizls/broadcast-action` has a dry-run or approval flag was not checked in its own README.
- orallexa’s `publish.yml` was not fetched, so the exact publish trigger after approval is only what the release workflow comment says.
- No source was found for an open-source inbox UI that edits one release into Twitter, Discord, Telegram, and Patreon drafts.

## Are any of them source-agnostic enough to take a PyPI release (RSS or webhook) rather than only a GitHub release event?

### Takeaway

A few pollers start from PyPI. The social GitHub Actions do not. PyPI’s documented public mechanism in the feeds doc is RSS, not a webhook. The posting actions will send any string a workflow passes them, so a PyPI poller could call them, but that glue was not found as a finished OSS release announcer for X, Mastodon, Bluesky, and Patreon.

### Cited Findings

- PyPI documents three RSS feeds: newest packages `https://pypi.org/rss/packages.xml`, latest updates `https://pypi.org/rss/updates.xml`, and per-project releases `https://pypi.org/rss/project/<project_name>/releases.xml`. The per-project feed includes package name, description, version, and a link to the release page. The feeds page does not describe an outbound webhook. — [PyPI RSS feeds](https://docs.pypi.org/api/feeds/)
- `pypi-notifier` 0.1.1 polls configured PyPI RSS URLs on a cron, stores state in SQLite, and posts to a Discord webhook when a new version appears. Docker and library use are documented. Supported notification clients listed: Discord only. — [PyPI project page](https://pypi.org/project/pypi-notifier/)
- `xnuinside/pypi_tools_bot` is a self-hosted Telegram bot. `/track package_name` notifies on new PyPI releases; `/track:nodev` skips dev releases. A public bot is linked at `https://t.me/pypi_tools_bot`. The README also covers download stats, search, and release lists, not social cross-posting. — [README](https://github.com/xnuinside/pypi_tools_bot)
- `release-tracker` has a PyPI watcher that takes a package name and needs no authentication, plus GitHub and GitLab watchers, and sends through one Apprise URL. Documented Apprise targets in that excerpt include Discord, Slack, and Telegram. — [README excerpt](https://github.com/nikhilbadyal/release-tracker)
- The NewReleases directory listing says the service tracks PyPI as well as GitHub and GitLab and can notify Discord, Telegram, Slack, and custom webhooks. Not established as open source. — [Directory listing](https://www.webfolio.to/tools/newreleases)
- `cbrgm/mastodon-github-action` can run from a container outside GitHub Actions, taking a message on the command line. It does not fetch PyPI. — [README](https://github.com/cbrgm/mastodon-github-action)
- `multi-release-notify`’s release quick start checks out the git repo with `fetch-depth: 0` and generates notes from previous tag to HEAD. Inputs `version`, `release_url`, `release_notes`, `title`, and `message` can be set explicitly. The README examples are GitHub Actions workflows. — [README](https://github.com/sinspired/multi-release-notify)
- Bluesky, Twitter, Discord webhook, and Telegram actions documented above take a string. Nothing in those READMEs subscribes to PyPI.

### Inferences

- Source-agnostic notification exists for “a PyPI version appeared” to Discord, Telegram, or Slack, via `release-tracker` plus Apprise, `pypi-notifier`, or `pypi_tools_bot`. Those are alerts, not platform-specific announcement drafts.
- A PyPI-triggered X, Mastodon, or Bluesky post would be custom glue: poll `releases.xml` or call the PyPI JSON API, then invoke `mastodon-github-action` or `bluesky-post` with a composed string. That composition was not found as a published action.
- Because the feeds doc does not mention webhooks, an OSS design that “receives a PyPI webhook” is ahead of what that page documents. RSS polling is the mechanism these tools actually use.

### Gaps

- Whether PyPI added outbound project webhooks after the feeds doc was written was not checked against any other PyPI page.
- License, last commit, and whether `pypi-notifier` or `pypi_tools_bot` are still maintained were not fetched. Only the PyPI page (v0.1.1) and the bot README were seen.
- `release-tracker` last commit, license, and whether it posts the PyPI release description or only the version were not in the retrieved excerpt.
- No tool in these sources drafts a PyPI release into Patreon.

## What licenses and maintenance signals show up, including dead Twitter APIs?

### Takeaway

Mastodon, Bluesky, Discord status, Release Drafter, and `action-gh-release` were pushed in 2026. The widely copied v1.1 tweet actions were last pushed in 2023, and an open issue says the old Twitter API path no longer works after the April 2025 v1 deprecation. `nearform` was pushed on 16 October 2026, but its license is unset and user reports about it working stop in 2024 and conflict.

### Cited Findings

| Project | License | Last push | Stars | Open issues | Notes |
| --- | --- | --- | --- | --- | --- |
| `cbrgm/mastodon-github-action` | Apache-2.0 | 2026-10-22 | 39 | 1 | Active. Posts a given message. — [metadata](https://api.github.com/repos/cbrgm/mastodon-github-action) |
| `myConsciousness/bluesky-post` | BSD-3-Clause | 2026-08-16 | 46 | 0 | Marketplace documents v6; main README copy still shows v5. — [metadata](https://api.github.com/repos/myConsciousness/bluesky-post), [marketplace](https://github.com/marketplace/actions/send-bluesky-post) |
| `sarisia/actions-status-discord` | MIT | 2026-05-08 | 284 | 11 | CI status embeds, also used for release embeds. — [metadata](https://api.github.com/repos/sarisia/actions-status-discord) |
| `release-drafter/release-drafter` | ISC | 2026-10-24 | 3947 | 41 | GitHub draft notes, not social. — [metadata](https://api.github.com/repos/release-drafter/release-drafter) |
| `softprops/action-gh-release` | MIT | 2026-10-24 | 5782 | 123 | GitHub releases. — [metadata](https://api.github.com/repos/softprops/action-gh-release) |
| `nearform-actions/github-action-notify-twitter` | null in the API | 2026-10-16 | 14 | 6 | Commenters treated it as the v2 replacement. — [metadata](https://api.github.com/repos/nearform-actions/github-action-notify-twitter), [issue discussion](https://github.com/ethomson/send-tweet-action/issues/28) |
| `twitter-together/action` | MIT | 2024-10-16 | 716 | 34 | PR-reviewed tweet files. Four-secret OAuth setup in the README. No issue was opened in this research to confirm it still posts. — [metadata](https://api.github.com/repos/twitter-together/action) |
| `snow-actions/tweet` | MIT | 2023-04-21 | 56 | 3 | Marketplace still says API v1.1, not v2. — [metadata](https://api.github.com/repos/snow-actions/tweet), [marketplace](https://github.com/marketplace/actions/tweet-action) |
| `ethomson/send-tweet-action` | MIT | 2023-03-04 | 83 | 11 | Only release v1.0.0 on 2019-12-31. Issue #28 still open. — [metadata](https://github.com/ethomson/send-tweet-action), [issue #28](https://github.com/ethomson/send-tweet-action/issues/28) |
| `sinspired/multi-release-notify` | MIT (README badge) | not fetched | not fetched | not fetched | Apprise fan-out. — [README](https://github.com/sinspired/multi-release-notify) |

- Issue #28 on send-tweet-action is the clearest maintenance signal for the old Twitter API: opened April 2023 requesting v2, still open, and a May 2025 comment says the action no longer works because the previous API is unsupported. The maintainer’s last push to that repo was March 2023, before the April 2025 v1 endpoint date in the Singlewire notice. — [Issue #28](https://github.com/ethomson/send-tweet-action/issues/28); [Singlewire notice](https://singlewire.my.site.com/s/article/Deprecation-Notice-Outbound-System-Twitter)
- InnerWarden’s release workflow comment says X is intentionally omitted because “its OAuth dance is not worth a CI secret.” That is one project’s choice, not an API outage report. — [announce-release.yml](https://github.com/InnerWarden/innerwarden/blob/main/.github/workflows/announce-release.yml)
- The directive workflow’s twitter adapter is configured with a bearer token, which is the v2 style, at broadcast-action v0.11.9. Whether that adapter succeeds against the current X API was not tested. — [broadcast.yml](https://github.com/directive-run/directive/blob/45ea65a9ec08455929400685dc1226e1a88a009c/.github/workflows/broadcast.yml)

### Inferences

- For a new announcer, Mastodon (`cbrgm`, Apache-2.0, pushed this month) and Bluesky (`myConsciousness`, BSD-3-Clause, v6 in 2026) are the living social actions. Discord and Telegram are better covered by webhooks, Apprise, or small release-specific actions whose maintenance was only partly checked.
- Copying a 2020–2023 “tweet the release” Marketplace example is likely to hit the v1.1 cutoff. The sources do not show a popular, licensed, obviously healthy X action with a 2026 success report.
- High open-issue counts on Release Drafter (41) and `action-gh-release` (123) sit next to pushes on 24 October 2026, so those counts are not by themselves a sign of abandonment.

### Gaps

- Last release tag, as distinct from last push, was not fetched except for send-tweet-action v1.0.0 and the bluesky v6 / mastodon v2 pins seen in other repos.
- Licenses and commit dates are missing for `release-tracker`, `pypi-notifier`, `pypi_tools_bot`, `SethCohen/github-releases-to-discord`, `tyagdit/release-telegram-action`, `cbrgm/telegram-github-action`, `tsickert/discord-webhook`, `sizls/broadcast-action`, `Shynixn/PatreonPostApi`, DISBot, and orallexa-marketing-agent.
- No October 2026 issue thread was found that retests twitter-together or snow-actions/tweet after the April 2025 v1 deprecation. Absence of that search hit is not proof they still work.
- X’s current paid-tier requirements were not quoted from X’s own pricing page.
