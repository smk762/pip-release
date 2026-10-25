# PyPI release announcement tools

Research date: 25 October 2026. Facts below are limited to pages and repository metadata retrieved that day. Pricing, features, and dates that were not on those pages are left in Gaps.

Candidate fields used throughout: what it watches, delivery, whether it drafts social copy, whether a human approves before a public send, license or price, and maintenance evidence.

## What are the established PyPI release feeds and watchers?

### Takeaway

PyPI itself only publishes RSS: one feed per project, plus two site-wide feeds. The live hosted watchers found on 25 October 2026 are libraries.io (follow a package, email and an on-site newsfeed), NewReleases.io (track named packages or an imported dependency file; chat, email, and webhooks), and Anitya at release-monitoring.org (one upstream project at a time, including a PyPI backend, with Fedora Messaging events). Dependabot and Renovate watch PyPI versions of dependencies already declared in a repository and open pull requests. Self-hosted package notifiers send a raw version alert. Nothing in the official feed list is a per-user or per-organization release feed.

### Cited Findings

#### PyPI RSS (official)

- PyPI documents exactly three RSS feeds. Newest packages: `https://pypi.org/rss/packages.xml` (newly created projects: name, description, project-page link). Latest updates: `https://pypi.org/rss/updates.xml` (newly created releases across projects: name, description, version, release-page link). Project releases: `https://pypi.org/rss/project/<project_name>/releases.xml` (same fields, one project). — [RSS Feeds, PyPI Docs](https://docs.pypi.org/api/feeds/); same text in Warehouse at [docs/user/api/feeds.md](https://github.com/pypi/warehouse/blob/main/docs/user/api/feeds.md)
- For periodically checking for new packages or updates, PyPI's API introduction says to use the RSS feeds. It also says no new integrations should use the XML-RPC APIs because they are planned for deprecation, and existing consumers should migrate to the JSON, RSS, or Index APIs. `https://docs.pypi.org/api/xml-rpc/` returned HTTP 404 on this pass. — [Introduction, PyPI Docs](https://docs.pypi.org/api/)
- The JSON API is per project. Its docs mark the `releases` key as deprecated and tell projects to use the Index API for that information where possible. — [JSON API, PyPI Docs](https://docs.pypi.org/api/json/)
- A Python Discourse thread asks for email when packages the person maintains are released. A reply points at the per-project RSS feed and an RSS-to-email service. The same thread distinguishes Warehouse email on project or release removal from email on new releases; the reply says the removal work does not cover notification on new releases. — [Relieve notifications about new PyPI releases](https://discuss.python.org/t/relieve-notifications-about-new-pypi-releases/60944)
- Record: watches one named project, or the entire index (newest projects / all new releases). Delivers RSS only. Does not draft social posts. No approval step, because nothing is sent except the feed. Price: no fee is stated on the feeds page. License of Warehouse was not retrieved. Maintained: the feeds page is the current PyPI docs, and the same page is on the Warehouse `main` branch. A last-commit date for that file was not retrieved.

#### libraries.io

- The libraries.io login page says that following a package puts new releases in an on-site newsfeed, and that libraries.io can email you about new versions of your dependencies. — [Login to Libraries.io](https://libraries.io/login)
- The API is free for registered users. Requests need an `api_key`, are limited to 60 requests per minute, and the docs say larger-scale access is available from Tidelift. Platform list includes `Pypi` (`https://pypi.org/`). Project lookup is `GET https://libraries.io/api/:platform/:name`. — [libraries.io API](https://libraries.io/api)
- The same API page's user endpoints take a GitHub login, not a PyPI username: `GET https://libraries.io/api/github/:login` ("user or organization"), `GET https://libraries.io/api/github/:login/repositories`, and `GET https://libraries.io/api/github/:login/projects` ("packages referencing the given user's repositories"). The headings present on the fetched API page run through platforms, project, repository, and those GitHub user routes. They do not include a subscriptions section. — [libraries.io API](https://libraries.io/api)
- A Python wrapper's README says `Subscribe.subscribe("pypi", "pandas")` produces an email on each new pandas version, and that one libraries.io subscription option (excluding prereleases) is toggled on the website rather than in the wrapper. That README was not cross-checked against the live API headings above. — [pybraries/pybraries](https://github.com/pybraries/pybraries)
- A 2018 Stack Overflow answer describes per-package Atom feeds at `https://libraries.io/pypi/{PACKAGENAME}/versions.atom` and a subscribe button, and reports an 11-day lag for one project as of August 2018. That URL and that reliability claim were not re-tested on 25 October 2026. — [How can I subscribe to updates of a package on PyPI?](https://stackoverflow.com/questions/17395151/how-can-i-subscribe-to-updates-of-a-package-on-pypi)
- Repository `librariesio/libraries.io`: not archived, license AGPL-3.0, `pushed_at` 2026-10-23T23:30:22Z, created 2014-09-30. — [GitHub API](https://api.github.com/repos/librariesio/libraries.io)
- Record: watches one package you follow (login-page wording: packages you depend on). A GitHub user's or organization's repositories can be listed, and packages that reference those repositories can be listed; that is not a PyPI username. Delivers email and an on-site newsfeed per the login page. No social-post drafting and no public-post approval step were described. Price: API access described as free for registered users; Tidelift for larger-scale data access; no other price was on the pages read. Looks maintained: default-branch push on 23 October 2026.

#### NewReleases.io

- The PyPI provider page lists package releases among providers and lists delivery to email, Slack, Telegram, Discord, Google Chat, Microsoft Teams, Mattermost, Rocket.Chat, Matrix, and webhooks. Email can be hourly, daily, weekly, or instant. Projects can be imported from a `requirements.txt` and from "a file with links to projects." Version filtering is by regular expression, pre-release flag, and updated state. The listed integrations do not include Twitter/X or Patreon. — [NewReleases.io PyPI page](https://pypi.newreleases.io/)
- The Slack page says notifications go out no longer than 30 minutes after a tracked project is updated, that pre-releases, updates, and regular expressions can be filtered, and that the app posts only about new releases of projects configured for Slack plus integration on/off messages. — [NewReleases.io Slack](https://newreleases.io/slack)
- The pricing page says "No credit card required!", a heading "Free", and "However, we do appreciate donations." It does not list project caps or paid tiers. — [NewReleases.io pricing](https://newreleases.io/pricing)
- A third-party comparison claims a free tier of 25 projects and paid plans from $5/month with chat integrations only on paid plans. That contradicts the vendor pages above, which list Slack, Telegram, and Discord on the product page and do not publish those prices. The third-party numbers are not used as facts. — [gitwatchman.com comparison](https://www.gitwatchman.com/blog/best-github-release-trackers), contradicted by [pricing](https://newreleases.io/pricing) and [PyPI provider page](https://pypi.newreleases.io/)
- Record: watches named projects, including PyPI packages, plus imports such as `requirements.txt` or a link file. Delivers the channels listed above. No drafting of social copy and no human approval before send were described; messages are release notifications. Price on the vendor pricing page: free, donations appreciated; numeric limits not stated there. Maintenance: the site responded on this pass. No public source repository or release date was found, so there is no commit date.

#### Anitya (release-monitoring.org)

- Anitya is "a cross-distribution upstream release monitoring project," homepage `https://release-monitoring.org`. Repository `fedora-infra/anitya`: not archived, license GPL-2.0, `pushed_at` 2026-10-23T23:43:11Z, created 2013-11-29. — [GitHub API](https://api.github.com/repos/fedora-infra/anitya)
- The user guide lists a PyPI backend "for projects hosted on pypi.python.org." Projects are registered individually. Duplicate names are allowed only across ecosystems, so two PyPI projects cannot share one Anitya name. A Flag button sends a project to an admin, which is moderation of bad metadata, not approval of an announcement. — [Anitya user guide](https://anitya.readthedocs.io/en/latest/user-guide.html)
- Integration is Fedora Messaging. Topics include `anitya.project.version.update.v2` when a new release is found (stable vs not stable). The older `anitya.project.version.update` topic is documented as deprecated. — [Integrating with Anitya](https://anitya.readthedocs.io/en/latest/integrating-with-anitya.html)
- The HTTP API can look up a monitored project with `GET /api/by_ecosystem/pypi/<name>` (example uses `pypi/six` on `release-monitoring.org`). — [Anitya API](https://anitya.readthedocs.io/en/stable/api.html)
- Email is not described in those two official chapters. A blog and a 2018 Stack Overflow answer say Fedora Notifications can email or otherwise notify from Anitya rules such as a named upstream project. Those UIs were not opened in this pass. — [GeekSocket](https://geeksocket.in/posts/release-monitoring-notifications/); [Stack Overflow](https://stackoverflow.com/questions/17395151/how-can-i-subscribe-to-updates-of-a-package-on-pypi)
- Record: watches one registered upstream project; PyPI is one backend. Delivers Fedora Messaging events. Email is described only by secondary guides. No social drafting. No announcement-approval step. Price: none found. License of the software: GPL-2.0. Looks maintained: push on 23 October 2026.

#### Dependabot (GitHub)

- GitHub documents Dependabot version updates for outdated dependencies. Enabling them is a `dependabot.yml` in the repository. When a dependency is outdated, Dependabot opens a pull request; the docs tell the maintainer to check tests, review the changelog and release notes in the pull request, and merge. Security updates are separate pull requests for known vulnerabilities. Version updates have a default cooldown of 3 days after a release; security updates do not. — [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates)
- Python is the `pip` ecosystem value, including pipenv and Poetry manifests. — [Supported ecosystems](https://docs.github.com/en/code-security/dependabot/ecosystems-supported-by-dependabot/supported-ecosystems-and-repositories)
- Record: watches dependency manifests in a Git repository, not a PyPI user and not an arbitrary package list chosen for announcement. Delivers GitHub pull requests. Does not draft social posts. A human merges the pull request before the dependency change lands; that is code review, not approval of a public announcement. Price: not stated on the pages read (it is part of GitHub). Maintenance: described in GitHub's current code-security docs; no doc-updated date was on those pages.

#### Renovate (Mend)

- Renovate extracts dependencies from repository files, looks up the latest version, and the Python docs say it checks PyPI by default. If the PyPI metadata includes a GitHub URL and a changelog or GitHub releases, Renovate embeds release notes in the generated pull request. Docs page examined corresponds to Mend Renovate 44.181.5. — [Python package manager support](https://docs.renovatebot.com/python/); pip requirements manager uses the `pypi` datasource — [pip Requirements](https://docs.renovatebot.com/modules/manager/pip_requirements/)
- The `pypi` datasource uses PEP 440, tries the JSON API then the Simple API, and reads release timestamps from `upload_time` or PEP 700 `upload-time`. — [Pypi datasource](https://docs.renovatebot.com/modules/datasource/pypi/)
- Repository `renovatebot/renovate`: "Cross-platform Dependency Automation by Mend.io," not archived, license AGPL-3.0, `pushed_at` 2026-10-25T06:16:22Z. Homepage `https://mend.io/renovate`. — [GitHub API](https://api.github.com/repos/renovatebot/renovate)
- Record: watches packages already declared in a repo. Delivers pull requests, optionally with upstream release notes inside the pull request. Does not draft social posts. A human can review the pull request before merge. Software license AGPL-3.0. Hosted Mend price was not retrieved. Looks maintained: push on 25 October 2026.

#### cenkalti/pypi-notifier (historical hosted app)

- README: watches `requirements.txt` files and emails when a requirement is updated. An hourly task sends the mail. Homepage listed as `http://www.pypi-notifier.org`. MIT. — [cenkalti/pypi-notifier](https://github.com/cenkalti/pypi-notifier)
- GitHub API: `archived: true`, MIT, `pushed_at` 2025-07-15T15:27:00Z, created 2013-07-13. The payload has no archive timestamp. — [GitHub API](https://api.github.com/repos/cenkalti/pypi-notifier)
- A fetch of the marketing homepage in search results returned only the title "PyPI Notifier," with no feature text. Whether the hosted service still sends mail was not tested.
- Record: dependency files in GitHub repos, email, no social draft, no approval step described (the hourly job sends mail). MIT. Archived, so treated as historical even though the last push is in 2025.

#### pypi-notifier 0.1.1 (jlw_4049)

- PyPI package `pypi-notifier` 0.1.1, MIT, author jlw_4049. Uploaded 2024-12-14. It polls a dict of package name to project RSS URL, stores state in SQLite, and posts to a Discord webhook when a newer version appears. The first run sends nothing. Docker and a cron schedule are documented. Supported notification clients in the description: Discord only. — [pypi.org/project/pypi-notifier](https://pypi.org/project/pypi-notifier/)
- No GitHub repository for this package was identified. A Gitea profile for the author was found, and the search snippet did not list this project among its repos. — [gitea.jessielw.com/jlw_4049](https://gitea.jessielw.com/jlw_4049)
- Record: an explicit list of project RSS feeds. Discord webhook. No social drafting and no approval step. MIT. Last publication found: 14 December 2024. No 2025 or 2026 release was found.

#### Sheriff-Sap/PYPINotifier

- README: desktop app. Packages come from `config.ini`. It shows name, latest version, and release date, raises a desktop notification, and can open the PyPI page. — [Sheriff-Sap/PYPINotifier](https://github.com/Sheriff-Sap/PYPINotifier)
- GitHub API: MIT, not archived, created 2023-02-22, `pushed_at` 2023-02-22T20:55:38Z, `updated_at` 2023-02-25. One star. — [GitHub API](https://api.github.com/repos/Sheriff-Sap/PYPINotifier)
- Record: a config-file package list. Desktop notification. No social drafting, no approval step, no chat delivery. MIT. Last push February 2023. Historical.

#### nikhilbadyal/release-tracker

- README: monitors GitHub, GitLab, PyPI, APKMirror, APKPure, and F-Droid. PyPI config is a package name (`repo: "requests"`). Notifications go through Apprise. The README names Discord, Slack, Telegram, email, Pushover, and Microsoft Teams, and says Apprise supports 80+ services. It also downloads wheels and sdists when `upload_assets` is set. MIT. Created 2025-05-03. — [nikhilbadyal/release-tracker](https://github.com/nikhilbadyal/release-tracker)
- GitHub API: not archived, MIT, `pushed_at` 2026-10-23T13:25:44Z. — [GitHub API](https://api.github.com/repos/nikhilbadyal/release-tracker)
- The README does not describe social-post drafting, a human approval step, Twitter/X, or Patreon. The full Apprise catalog was not opened, so support for those two networks is not claimed.
- Record: one configured package name per PyPI watcher entry. Apprise notifications. No draft and no approval described. MIT. Looks maintained: push on 23 October 2026.

#### herald-post (generic feed publisher, new in October 2026)

- PyPI project `herald-post`, summary "Post one announcement to every channel you choose, after showing exactly what each one will get." Versions 0.1.0 (upload 2026-10-10T13:55:37) and 0.2.0 (upload 2026-10-10T17:19:19). Classifiers include "License :: OSI Approved :: Apache Software License" and "Development Status :: 3 - Alpha." The JSON `license` field is null. Project URLs point at `https://github.com/sigrix-io/herald`. — [pypi.org/pypi/herald-post/json](https://pypi.org/pypi/herald-post/json)
- Channels in the project description: Bluesky, Mastodon, Discord, Slack, Telegram, LinkedIn, and stdout. Twitter/X and Patreon are not in that table. It says it is a command, a GitHub Action, a Python library, an MCP server, and a plugin interface.
- `herald watch FEED --to CHANNEL` posts each new item of an RSS or Atom feed. The documented example is a GitHub `releases.atom` URL. Template placeholders are `{title}`, `{link}`, and `{feed}`. The first run for a feed and channel records current items and posts none. Later runs post new items, oldest first, with no preview step. `herald preview` shows exact per-channel text and returns a draft id; `herald post` accepts only that draft id. The description says a post sends only a draft a preview made. Those are two different paths: watch publishes from the feed template; preview/post publishes text the operator already supplied.
- A PyPI project feed is an RSS feed, so `herald watch` can be pointed at `https://pypi.org/rss/project/<name>/releases.xml`. The docs do not mention PyPI by name.
- Record: any one HTTPS RSS or Atom feed the operator names, or a hand-written announcement. Watch path delivers immediately to the channels above using a template. Preview path shows the exact text and posts only that draft. It does not generate prose. Apache classifier, alpha, both releases on 10 October 2026. Later commits were not checked.

#### OpenAdaptAI/openadapt-crier (social drafts, GitHub source)

- README: watches GitHub repositories for commits, releases, and merged pull requests (`CRIER_REPOS`). An LLM scores interest and writes platform-specific drafts. Drafts go to a Telegram bot with Approve, Edit, and Reject, plus per-platform toggles for Twitter, Discord, and LinkedIn. Approved posts go out through openadapt-herald to Discord, Twitter/X, and LinkedIn. Telegram is the review channel in this description, not a public announcement channel. Patreon is not mentioned. PyPI is not mentioned. — [OpenAdaptAI/openadapt-crier](https://github.com/OpenAdaptAI/openadapt-crier)
- GitHub API: MIT, not archived, created 2026-03-01, `pushed_at` 2026-10-14T09:28:08Z, 0 stars. — [GitHub API](https://api.github.com/repos/OpenAdaptAI/openadapt-crier)
- Record: GitHub repos, not PyPI. Drafts social copy. Human approves, edits, or rejects in Telegram before Discord, Twitter/X, and LinkedIn. MIT. Push on 14 October 2026. Included because it is the closest approve-then-publish design found, and it does not watch PyPI.

#### ntfy (the nearest match for "nitfy")

- No product named nitfy was found. ntfy.sh is a generic push service: subscribe to a topic in the phone or desktop app, publish with HTTP POST. The getting-started page does not mention PyPI, RSS, or package registries. — [ntfy docs](https://docs.ntfy.sh/)
- A separate Python project, dschep/ntfy, is "a utility for sending push notifications," GPLv3 on its PyPI page, with optional backends that include Telegram, Slack, and Matrix. GitHub release v2.7.1 was published 2025-10-27. It is a local notifier you invoke, not a PyPI watcher. — [pypi.org/project/ntfy](https://pypi.org/project/ntfy/); [v2.7.1](https://github.com/dschep/ntfy/releases/tag/v2.7.1)
- Record for ntfy.sh: watches nothing; it delivers a message something else sends. License and price were not on the getting-started page. The docs page loaded, so the service is documented as current; a release date was not retrieved.

#### Anaconda.org / conda (adjacent, not PyPI)

- Conda documents a channel clone RSS feed that lists syncs and package add/remove events for a rolling two weeks. The documented example is conda-forge at the channel RSS URL, with item titles like `linux-64:add:<file>.tar.bz2`. The docs page used is conda 25.5.x. The example's sample dates are in 2019. — [conda channels](https://docs.conda.io/projects/conda/en/25.5.x/user-guide/concepts/channels.html)
- Anaconda channel notices are written by a channel owner or administrator (`anaconda-client` 1.15.0 or later). They are created as drafts and become visible in `conda install` / `conda update` only after `anaconda channel notice publish`. They are not email, chat, or social posts, and the docs describe conda channels, not PyPI projects. — [Channel notices](https://www.anaconda.com/docs/anaconda-org/admin-guide/notices)
- No Anaconda.org feature that emails or posts when a PyPI project is released was found.

#### Listing aid that does not notify

- `pypi-toolkit` 0.2.0's PyPI description says `pypi-toolkit package list <username>` lists packages for a PyPI user, and it can audit metadata. Notification is not in the feature list. Upload date and repository activity were not retrieved. — [pypi.org/project/pypi-toolkit](https://pypi.org/project/pypi-toolkit/)

#### Vendor marketing page, not independently verified

- A postrss.com article, with "Updated: 2026-10-15" in the search snippet, says to add `https://pypi.org/rss/project/your-package/releases.xml` to their auto-poster and names Mastodon, Bluesky, Discord, Matrix, Telegram, team chat, and LinkedIn. It describes automatic posting and a message built from the feed title and/or description, plus keyword filters. The snippet's channel table does not include Twitter/X or Patreon, and it does not describe an approval step. The article body was not fetched, and pricing was not in the snippet. Treat this as an unverified vendor claim. — [postrss.com article snippet](https://postrss.com/pypi-release-rss-feed-auto-post/)

### Inferences

- The established pattern is "tell me a dependency moved" or "here is one project's feed," not "announce this maintainer's new release."
- A global updates feed plus a separately obtained package list could be filtered down to one person, but that filter is not part of any product documented here.
- Crier and herald show that approve-then-publish and multi-channel posting exist in 2026, aimed at GitHub events or at a single RSS URL the operator pastes in.

### Gaps

- No GitHub App or Actions Marketplace item dedicated to announcing a PyPI user's releases was identified. The marketplace was not browsed page by page. actionsflow appears only as a February 2024 discussion asking whether it can watch one project's RSS; that does not establish the feature. — [actionsflow discussion #48](https://github.com/actionsflow/actionsflow/discussions/48)
- Live behavior of XML-RPC `user_packages` was not tested. Current PyPI docs say not to start new XML-RPC integrations. Older third-party notes describe `user_packages(username)` returning role and package name. — [lukaszb/pypi](https://github.com/lukaszb/pypi); [memotut writeup](https://www.memotut.com/en/bfe434ebea3d624d6eab/)
- PyPI Organizations: the feeds page does not list an organization feed. Whether the organization UI exposes releases another way was not checked.
- NewReleases.io source repository, last change date, and any project cap beyond the pricing page's "Free."
- Whether libraries.io still sends reliable release email in 2026, and whether `versions.atom` still exists. The 2018 lag report is stale evidence.
- ntfy.sh license and price; Apprise's full service list; herald commits after 10 October 2026; pypi-toolkit's upload date; postrss.com as a working product.
- Patreon posting was not found on any of the product pages read.

## Which of them can follow every project owned by a PyPI username, not just one package?

### Takeaway

None of the watchers documented here take a PyPI username and follow every project that account owns. Official RSS is per project or site-wide. libraries.io can list packages tied to a GitHub user or organization. NewReleases.io, Anitya, release-tracker, and the pypi-notifier packages take an explicit package list or one project. Dependabot and Renovate follow dependencies declared in a repo.

### Cited Findings

- The PyPI feeds page lists newest packages, latest updates, and `https://pypi.org/rss/project/<project_name>/releases.xml`. It does not list a user URL. — [RSS Feeds](https://docs.pypi.org/api/feeds/)
- libraries.io user and user-package calls are `GET /api/github/:login` and `GET /api/github/:login/projects`, described as packages referencing that user's repositories. The sample payload's `host_type` is GitHub. — [libraries.io API](https://libraries.io/api)
- NewReleases.io imports a `requirements.txt` or a file of project links, and tracks projects the user adds. The PyPI page does not mention a PyPI username. — [pypi.newreleases.io](https://pypi.newreleases.io/)
- Anitya projects are added one at a time, with the PyPI backend named on the project. — [Anitya user guide](https://anitya.readthedocs.io/en/latest/user-guide.html)
- `pypi-notifier` 0.1.1 is configured with a dict of package RSS URLs. cenkalti/pypi-notifier reads `requirements.txt`. Sheriff-Sap/PYPINotifier reads `config.ini`. release-tracker lists package names under `repos:`. — [pypi-notifier 0.1.1](https://pypi.org/project/pypi-notifier/); [cenkalti/pypi-notifier](https://github.com/cenkalti/pypi-notifier); [Sheriff-Sap/PYPINotifier](https://github.com/Sheriff-Sap/PYPINotifier); [release-tracker](https://github.com/nikhilbadyal/release-tracker)
- Dependabot and Renovate read manifests in a repository (`pip` / `pypi` datasource). — [Dependabot ecosystems](https://docs.github.com/en/code-security/dependabot/ecosystems-supported-by-dependabot/supported-ecosystems-and-repositories); [Renovate Python](https://docs.renovatebot.com/python/)
- `pypi-toolkit package list your-username` is described as listing a user's packages. It is an audit and listing CLI, and the description does not include watching or notifying. — [pypi-toolkit](https://pypi.org/project/pypi-toolkit/)
- Discourse: a maintainer who wanted email for "the packages I'm maintainer of" was pointed at per-package RSS, not a user feed. — [Discourse thread](https://discuss.python.org/t/relieve-notifications-about-new-pypi-releases/60944)

### Inferences

- "Every project a PyPI user owns" is an unsolved product gap. The closest substitutes are a hand-maintained package list, a `requirements.txt` of dependencies (a different set from projects one maintains), or libraries.io's list of packages whose repositories sit under a GitHub login.
- Ownership and maintenance are different roles. Even the older XML-RPC notes return a role alongside the package name. A tool that only stored "owner" would miss maintainer-only projects, and the reverse. No current notifier documented here makes that distinction because none take the username.

### Gaps

- Whether the public PyPI user profile HTML enumerates that user's projects was not fetched, so it is not claimed as an API.
- Whether `user_packages` still answers in October 2026 was not tested.
- No source was found for a PyPI organization release subscription.

## Do any of them draft social copy, or do they only send a raw version alert?

### Takeaway

The PyPI watchers send a raw release alert: feed entry, email, chat message, webhook, desktop notification, Fedora Messaging event, or a dependency pull request. herald can turn one RSS item into a template post (`{title}`, `{link}`, `{feed}`) and can require a human to preview text, but it does not write announcement prose and its watch mode posts without that preview. Crier drafts prose and waits for Telegram approval, and it watches GitHub rather than PyPI. No documented tool drafts a post and then publishes to Twitter/X, Discord, Telegram, and Patreon.

### Cited Findings

- PyPI project RSS items are package name, description, release version, and a link to the release page. — [RSS Feeds](https://docs.pypi.org/api/feeds/)
- libraries.io login page: email and a newsfeed "when there's a new release." No social channels are mentioned there. — [libraries.io login](https://libraries.io/login)
- NewReleases.io Slack page: messages about new releases of configured projects. Delivery list on the PyPI page is email, Slack, Telegram, Discord, Google Chat, Teams, Mattermost, Rocket.Chat, Matrix, and webhooks. — [Slack](https://newreleases.io/slack); [PyPI page](https://pypi.newreleases.io/)
- Anitya emits `anitya.project.version.update.v2` with a stable/not-stable distinction. The integration chapter does not describe composed social text. — [Integrating with Anitya](https://anitya.readthedocs.io/en/latest/integrating-with-anitya.html)
- Dependabot pull requests include changelog and release notes for the maintainer to review. Renovate can embed upstream release notes in the pull request when GitHub metadata is present. Both are pull-request bodies, not social posts. — [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates); [Renovate Python](https://docs.renovatebot.com/python/)
- jlw `pypi-notifier` sends a Discord webhook on a new version. release-tracker sends an Apprise notification. cenkalti emails. Sheriff-Sap raises a desktop notification. None of those READMEs describe generated social copy or an approval queue. — [pypi-notifier](https://pypi.org/project/pypi-notifier/); [release-tracker](https://github.com/nikhilbadyal/release-tracker); [cenkalti/pypi-notifier](https://github.com/cenkalti/pypi-notifier); [PYPINotifier](https://github.com/Sheriff-Sap/PYPINotifier)
- herald `watch` fills `{title}`, `{link}`, and `{feed}` and posts. `preview` then `post` shows exact channel text and posts only that draft. Channels listed: Bluesky, Mastodon, Discord, Slack, Telegram, LinkedIn, stdout. A plugin interface is mentioned. Twitter/X and Patreon are absent from the channel table. — [herald-post on PyPI](https://pypi.org/project/herald-post/)
- Crier: LLM drafts, Telegram Approve/Edit/Reject, then Discord, Twitter/X, and LinkedIn. Source events are GitHub commits, releases, and merged pull requests. — [openadapt-crier](https://github.com/OpenAdaptAI/openadapt-crier)
- Anaconda channel notices have an explicit draft state and a publish command. The audience is conda users in the terminal, and the subject is a conda channel, not a PyPI release. — [Channel notices](https://www.anaconda.com/docs/anaconda-org/admin-guide/notices)
- The postrss.com snippet describes automatic posts built from the feed title and/or description. It was not fetched in full and is not treated as a confirmed product.

### Inferences

- "Human approves before anything public is sent" shows up in three adjacent places, each missing part of the target job: herald's preview path (operator-supplied text, or a separate auto-posting watch path), Crier (GitHub only; public targets Discord, X, and LinkedIn; Telegram is the inbox), and Anaconda notices (conda CLI, admin draft/publish).
- Room for more platforms later is explicit only for herald, which says it has a plugin interface. That claim is about herald's own channels, not about a PyPI-user watcher.
- A raw alert that includes the project description is still a release notice. None of the PyPI watchers were documented as writing a maintainer-style announcement (what changed, call to action, per-network edits).

### Gaps

- No page found that posts a PyPI release to Patreon, or that queues one draft for X, Discord, Telegram, and Patreon together.
- Apprise's service list was not opened, so release-tracker might be able to reach more networks than the README names. That would still be a raw notification, based on the README.
- Whether herald's plugin interface has existing Twitter/X or Patreon plugins was not checked beyond the channel table on the PyPI description.

## Which are abandoned, and which are actively maintained in 2025–2026?

### Takeaway

Actively changing in 2025–2026, by a repository push or a PyPI upload in that window: libraries.io (push 23 October 2026), Anitya (push 23 October 2026), Renovate (push 25 October 2026), release-tracker (push 23 October 2026; repo created May 2025), herald-post (uploads 10 October 2026), and openadapt-crier (push 14 October 2026, GitHub-only). PyPI's own RSS docs are the current documentation. NewReleases.io's site answered but has no commit date here. dschep/ntfy shipped v2.7.1 on 27 October 2025 and is not a PyPI watcher. Historical or stale: Sheriff-Sap/PYPINotifier (last push 22 February 2023), jlw pypi-notifier (only upload 14 December 2024), and cenkalti/pypi-notifier (archived; last push 15 July 2025).

### Cited Findings

- `librariesio/libraries.io` `pushed_at` 2026-10-23T23:30:22Z, `archived: false`, AGPL-3.0. — [GitHub API](https://api.github.com/repos/librariesio/libraries.io)
- `fedora-infra/anitya` `pushed_at` 2026-10-23T23:43:11Z, `archived: false`, GPL-2.0. — [GitHub API](https://api.github.com/repos/fedora-infra/anitya)
- `renovatebot/renovate` `pushed_at` 2026-10-25T06:16:22Z, `archived: false`, AGPL-3.0. Datasource docs labeled Mend Renovate 44.181.5. — [GitHub API](https://api.github.com/repos/renovatebot/renovate); [Pypi datasource](https://docs.renovatebot.com/modules/datasource/pypi/)
- `nikhilbadyal/release-tracker` created 2025-05-03, `pushed_at` 2026-10-23T13:25:44Z, `archived: false`, MIT. — [GitHub API](https://api.github.com/repos/nikhilbadyal/release-tracker)
- `herald-post` 0.1.0 and 0.2.0 both uploaded 2026-10-10. Alpha classifier. — [pypi.org/pypi/herald-post/json](https://pypi.org/pypi/herald-post/json)
- `OpenAdaptAI/openadapt-crier` created 2026-03-01, `pushed_at` 2026-10-14T09:28:08Z, `archived: false`, MIT. Watches GitHub, not PyPI. — [GitHub API](https://api.github.com/repos/OpenAdaptAI/openadapt-crier)
- dschep/ntfy v2.7.1 published 2025-10-27. Not a registry watcher. — [GitHub release](https://github.com/dschep/ntfy/releases/tag/v2.7.1)
- `cenkalti/pypi-notifier` `archived: true`, `pushed_at` 2025-07-15T15:27:00Z. Archive date itself was not in the API object. — [GitHub API](https://api.github.com/repos/cenkalti/pypi-notifier)
- `pypi-notifier` 0.1.1 upload time 2024-12-14T20:13:23Z. No later version was listed. — [pypi.org/project/pypi-notifier](https://pypi.org/project/pypi-notifier/)
- `Sheriff-Sap/PYPINotifier` `pushed_at` 2023-02-22T20:55:38Z, `archived: false`. — [GitHub API](https://api.github.com/repos/Sheriff-Sap/PYPINotifier)
- Dependabot is documented on GitHub's current code-security docs. A last-updated stamp for those pages was not retrieved. — [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates)
- NewReleases.io pricing and PyPI pages loaded. No repository push date was found. — [pricing](https://newreleases.io/pricing)
- PyPI feeds are the live docs, mirrored on Warehouse `main`. — [docs.pypi.org](https://docs.pypi.org/api/feeds/); [feeds.md](https://github.com/pypi/warehouse/blob/main/docs/user/api/feeds.md)
- Conda channel RSS is documented in the conda 25.5.x manual. Channel notices are documented on Anaconda's current docs and require anaconda-client 1.15.0 or later. Those are conda features. — [channels](https://docs.conda.io/projects/conda/en/25.5.x/user-guide/concepts/channels.html); [notices](https://www.anaconda.com/docs/anaconda-org/admin-guide/notices)

### Inferences

- "Archived" is a stronger abandonment signal than a quiet repo. cenkalti is archived. Sheriff-Sap is not archived and has had no push since February 2023, so it is unmaintained in practice.
- A single upload in December 2024 (jlw pypi-notifier) with no later release and no public commit history found means it should not be described as maintained through 2025–2026. It also should not be described as formally abandoned.
- herald-post and crier are new in 2026 and have very little history. A same-day 0.1.0 and 0.2.0, and an alpha classifier, mean herald is published, not a long-running service.
- Site-is-up is weaker evidence than a commit. NewReleases.io is in that category.

### Gaps

- Archive date for cenkalti/pypi-notifier.
- Commit dates for herald after the 10 October 2026 uploads, for pybraries, for pypi-toolkit, and for ntfy.sh.
- A primary status page or changelog for NewReleases.io and for the hosted libraries.io email worker. Repository pushes do not prove the hosted mailer is healthy.
- Dependabot has no separate version stamp on the docs pages read.
