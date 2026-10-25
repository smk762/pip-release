# Platform posters for release announcements

Research date: 25 October 2026. Scope is tools a maintainer could use to announce a software release on Discord, Telegram, X, and Patreon, judged on (a) receiving an external release event, (b) drafting or templating the message, (c) waiting for human approval or edit, and (d) being one channel among several. Adjacent networks are noted only when a cited tool already treats them as a publishing destination.

Direct fetches of `https://docs.x.com/llms.txt`, `https://docs.x.com/x-api/getting-started/pricing`, and `https://developer.x.com/en/docs/x-api` returned HTTP 403. X pricing and posting-capability claims below come from a documentation mirror that reproduces the docs.x.com changelog header, plus third-party pages that cite docs.x.com. Those figures are labeled as such.

## Discord: incoming webhooks, popular release-announce bots, and whether any of them queue a message for moderator approval

### Takeaway

Discord incoming webhooks, including Discord’s GitHub-compatible webhook, post immediately. The documented release-announce paths template a message and send it; none of them hold the announcement for a moderator before it appears in the channel. A separate workflow tool can post an approval prompt to Discord and only then send the real announcement.

### Cited Findings

- Incoming webhooks are HTTP endpoints tied to one channel. A POST to the webhook URL makes the message appear in that channel, with no bot and no persistent connection. Discord’s own examples include CI/CD build results and external app updates. — [Discord webhooks overview](https://docs.discord.com/developers/platform/webhooks)
- Incoming webhook type is “Incoming Webhooks can post messages to channels with a generated token.” Executing a webhook is `POST /webhooks/{webhook.id}/{webhook.token}`. The query parameters are `wait`, `thread_id`, and `with_components`. The body fields are content, username, avatar, embeds, files, components, flags, thread name, tags, and poll. There is no pending, draft, or approval field. `wait` only waits for server confirmation of a send. — [Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Discord documents a GitHub-compatible execute URL, `POST /webhooks/{webhook.id}/{webhook.token}/github`. You add that URL as a GitHub repository webhook. Supported GitHub events include `release`, plus push, issues, pull requests, discussions, and others. Query parameters are only `thread_id` and `wait`. — [Webhook resource](https://docs.discord.com/developers/resources/webhook)
- Help Center: creating a webhook generates a URL you drop into other services. The Integrations page lists webhooks, who added them, and which channel they post to. A server can have at most 50 integrations. — [Intro to Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks); [Server Integrations Page](https://support.discord.com/hc/en-us/articles/360045093012-Server-Integrations-Page)
- After a webhook message exists, the same token can edit or delete it (`PATCH` or `DELETE .../messages/{message.id}`). That is an edit of an already-sent message, not a pre-publish queue. — [Webhook resource](https://docs.discord.com/developers/resources/webhook)
- GitHub Marketplace action “Github Releases To Discord” (`SethCohen/github-releases-to-discord`) sends a Discord embed of the GitHub release description when a release is published. It cleans the changelog, converts mentions and issue links, trims to embed limits, and lets you set color, username, avatar, footer, and content such as `@everyone`. Setup is a Discord webhook URL in the workflow. The listing does not describe a hold for moderator approval. — [GitHub Marketplace](https://github.com/marketplace/actions/github-releases-to-discord)
- n8n’s Discord node operations include Message “Send” and “Send and Wait for Response.” The wait operation sends a message and pauses the workflow until a person confirms or replies. Response types include Approval (approve, or approve and disapprove, with custom button labels), Free Text, and Custom Form. — [n8n Discord node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.discord/)
- IFTTT’s Discord–Patreon connector page says that when something is posted on Patreon, IFTTT can post it to a Discord channel, and names the Discord action “Post a message to a channel.” The page does not describe a draft or approval step. — [IFTTT Discord and Patreon](https://ifttt.com/connect/discord/patreon)
- Ship 2 Post’s marketing site says a GitHub release is drafted and held in a review queue, then published to Discord among other destinations. That queue is claimed to live in Ship 2 Post, not in Discord. This is vendor copy; this research did not find an independent repository or a Discord App Directory listing that confirms it. — [Ship 2 Post integrations](https://s2p.dev/integrations); [Ship 2 Post GitHub releases](https://s2p.dev/auto-post-github-releases-to-social-media)

Judged against the four criteria:

- Discord incoming webhook, including the GitHub-compatible URL: (a) yes for a GitHub `release` webhook, (b) no template of your own on the GitHub-compatible endpoint, Discord renders GitHub’s payload, (c) no, immediate-send, (d) Discord only.
- `SethCohen/github-releases-to-discord`: (a) yes, GitHub `release: published`, (b) yes, embed template and cleanup, (c) no, immediate-send, (d) Discord only.
- n8n Discord “Send”: (a) only if the workflow starts from a webhook or another trigger, (b) yes, the workflow supplies the text, (c) no for the Send operation, immediate-send, (d) yes if other n8n nodes are in the same workflow.
- n8n Discord “Send and Wait for Response” with Approval: the approval prompt itself is sent immediately. It can gate later steps. It is not a Discord moderation queue that hides the announcement until a moderator approves it.

### Inferences

- A maintainer who only needs Discord can point a GitHub release webhook at Discord’s GitHub-compatible URL and get an immediate channel post with no extra bot.
- Anything that looks like “approve the release note before it hits the announcement channel” has to be built outside Discord, or assembled in a workflow tool that posts a separate approval message first. Discord’s webhook API does not have that state.

### Gaps

- The Discord App Directory was not surveyed bot by bot. A niche release bot with a moderator queue may exist and was not found.
- Make.com’s Discord module list was only partly visible. The fetched pairing page listed many Discord writes (channels, invites, events, delete message) and Patreon reads, but the snippet ended before a complete “post a message” entry, so Make’s Discord send action is not cited as confirmed. — [Make Discord and Patreon](https://www.make.com/integrations/discord/patreon)
- Zapier’s Discord action catalog was not fetched.

## Telegram: channel-post bots and IFTTT/Zapier/n8n Telegram actions. Is there a draft/approval step, or only immediate send?

### Takeaway

The Telegram Bot API `sendMessage` method, IFTTT’s Telegram “Send message” action, and n8n’s documented Telegram “Send Message” operation are immediate-send. Channel posting requires the bot to be an administrator with permission to post. No draft or approval parameter was found on `sendMessage`.

### Cited Findings

- `sendMessage` “send[s] text messages. On success, the sent Message is returned.” Required fields are `chat_id` and `text` (1–4096 characters after entity parsing). `chat_id` may be a channel username `@username`. Optional fields on the method page include thread id, parse mode, link previews, silent send, protect content, paid broadcast, reply markup, and `suggested_post_parameters`. The page describes `suggested_post_parameters` as applying “for direct messages chats only,” and says a suggested post sent as a reply to another suggested post declines that earlier suggestion. The parameter list does not include a schedule time, a channel draft flag, or a moderator-approval flag. — [sendMessage](https://core.telegram.org/bots/api/methods/sendmessage.md)
- Bot API calls are HTTPS `https://api.telegram.org/bot<token>/METHOD_NAME`. — [Telegram Bot API](https://core.telegram.org/bots/api/)
- A bot cannot join a channel by itself. It must be added as an administrator. Without post permission, the API returns errors such as `chat not found` or `bot is not a member of the channel`. A successful channel `sendMessage` returns a Message whose `chat.type` is `channel`. — [Channels — Telegram Bot API practical guide](https://botservice.biz/en/telegram-bot-api/channels) (secondary guide, not the official reference; the permission model matches the official method’s “sent Message” contract)
- IFTTT Telegram actions include “Send message” (“send a text message to a Telegram chat”), “Send photo,” “Send video,” and “Send mp3.” Triggers include “New post in your channel,” which fires when a message is posted in a public channel where you and the @IFTTT bot are admins. The action descriptions do not mention a draft or approval hold. Related services listed on that page include X, Discord, Bluesky, Mastodon.social, Slack, LinkedIn, YouTube, Instagram, Threads, and GitHub. — [IFTTT Telegram](https://ifttt.com/telegram)
- n8n’s Telegram node documentation lists message operations: delete, edit text, pin, send animation, audio, chat action, document, location, media group, message, photo, sticker, video, and unpin. “Send Message” is “Send a text message.” The docs say the bot must be added to a channel to send there. This official node page does not list a wait or approval operation. — [n8n Telegram node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.telegram)
- n8n’s Telegram–X integration marketing page lists an extra Telegram message operation, “Send and Wait for Response,” which the node documentation page above does not list. — [n8n Telegram and X](https://n8n.io/integrations/telegram/and/twitter/); contradicted by the operations list on [n8n Telegram node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.telegram)
- Community n8n templates implement approval outside the Telegram send itself: one sends a draft back to a Telegram chat and publishes to X only after the person approves; another uses Telegram as the review chat and then calls a third-party poster. Those are workflow designs, not a Telegram channel draft API. — [n8n template 6148](https://n8n.io/workflows/6148-publish-linkedin-and-x-posts-with-telegram-bot-gemini-ai-and-vector-memory/); [n8n template 11121](https://n8n.io/workflows/11121-auto-create-and-publish-x-threads-twitter-with-gpt-via-telegram-and-approval-loop/)
- Publer’s help center, updated 23 September 2026, lists Telegram groups and channels as a supported publishing network, alongside Facebook, Instagram, X, LinkedIn, Pinterest, Google Business Profile, YouTube, WordPress, TikTok, Mastodon, Threads, and Bluesky. Discord and Patreon are not in that list. The same help center’s Zapier article lists a “Create Post” action that can publish now, schedule, or save as a draft, and triggers for “Post Pending Approval” and “Post Approved.” — [Publer supported networks](https://publer.com/help/en/article/what-social-networks-are-supported-npoun1/); [Publer Zapier help](https://publer.com/help/en/article/how-to-connect-to-zapier-and-automate-your-workflows-18mun8n/)

Judged against the four criteria:

- Telegram Bot API `sendMessage` to a channel: (a) no built-in release listener, any script can call it, (b) the caller supplies `text` and `parse_mode`, (c) no, immediate-send, (d) one channel per call; the caller can call other networks separately.
- IFTTT “Send message”: (a) only if some other IFTTT trigger fires, (b) applet ingredients can fill the text, (c) no, immediate-send, (d) yes, IFTTT applets can include other services.
- n8n “Send Message”: (a) if the workflow has a webhook or other trigger, (b) yes, (c) no on the documented operation, immediate-send, (d) yes inside a multi-node workflow.
- Publer Telegram: (a) not a native GitHub release listener; Zapier or the Publer API can feed it, (b) yes, post text and drafts, (c) yes, Publer exposes pending-approval and approved states to Zapier, (d) yes, one of the networks in the 23 September 2026 list. Discord and Patreon are not in that list.

### Inferences

- A release bot that “posts to the Telegram channel” is an immediate publish once `sendMessage` is called. A human checkpoint has to happen in the caller (a CI manual approval, an n8n wait step, or a scheduler such as Publer) before that call.
- `suggested_post_parameters` should not be treated as a channel moderation queue. The official method page limits it to direct-message chats.

### Gaps

- Zapier’s Telegram action page was not fetched, so Zapier-specific Telegram fields are not listed. n8n and IFTTT were.
- Whether the current n8n Telegram node actually has “Send and Wait for Response” is unresolved: the marketing integration page names it and the node reference does not.
- The official Bot API page was not separately checked for a distinct `sendMessageDraft` or scheduled-message method beyond the `sendMessage` parameter table returned in search.

## Twitter/X: what official or third-party posting still works in 2026 after API pricing changes, and which tools still offer a compose-then-approve flow

### Takeaway

Posting still works through `POST /2/tweets` on a credit balance. The docs mirror’s 20 April 2026 pricing update sets a plain post at $0.015 and a post that contains a URL at $0.20. X does not provide the approval queue; Buffer, Publer, and several vendor release tools do. IFTTT and n8n’s X “create tweet” operation are immediate-send once the node runs.

### Cited Findings

- A docs.x.com changelog mirror says that, effective 20 April 2026, owned-read endpoints are $0.001 per resource, `POST /2/tweets` is $0.015 per post, posts containing a URL are $0.20 per post, and summoned replies remain $0.01. The same entry says Following, Likes, and Quote-Posts were removed from all self-serve tiers. — [X API changelog mirror](https://x-preview.mintlify.app/changelog)
- The same mirror’s pricing page describes pay-per-use credits with no subscription, purchased in the developer console, deducted per request. Its write table matches the April 20 figures: Post Create $0.015, Post Create with URL $0.200, Post Create summoned $0.010. It also says pay-per-use post reads are capped at 3 million per monthly billing cycle unless you are on Enterprise, and that “prices are subject to change” with current rates in the console and on the developer.x.com pricing page. — [X API pricing mirror](https://x-preview.mintlify.app/x-api/getting-started/pricing)
- An earlier entry on that changelog, the pay-per-use pilot, lists older rates: $0.005 per post read, $0.01 per user read, $0.01 per content create. A separate undated “X Developer Platform” page saved on Amazon S3 still shows “Content: Create” at $0.010 per request. — [X API changelog mirror](https://x-preview.mintlify.app/changelog); [S3 developer-platform snapshot](https://s3.us-west-2.amazonaws.com/vp-files-ore/resources/12months/XO64kBZOZrAAG-RZo6DuWgY39uY.html)
- The pay-per-use launch note on the same changelog says there is a developer console at console.x.com, official Python and TypeScript SDKs (`pip install xdk`, `npm install @xdevplatform/xdk`), a playground, and an MCP server. It says Basic and Pro plans remain available and existing subscribers can opt into pay-per-use. Public-utility apps get free scaled access. Recently active legacy Free-tier users get a one-time $10 voucher. — [X API changelog mirror](https://x-preview.mintlify.app/changelog)
- The changelog also says programmatic replies via `POST /2/tweets` on self-serve tiers are allowed only when the original author has summoned the replier by mention or quote. Enterprise is exempt. That rule is about replies, not about an account posting its own release announcement. — [X API changelog mirror](https://x-preview.mintlify.app/changelog)
- The changelog says X added “new endpoints for drafting and publishing Articles,” and separately that a Premium user can edit their own recent post for one hour via `POST /2/posts` with `edit_options.previous_post_id`. The Articles note does not name the paths. Neither item is a third-party “hold this tweet for a human” API. — [X API changelog mirror](https://x-preview.mintlify.app/changelog)
- Third-party price tables repeat the same $0.015 / $0.200 create rates and attribute them to docs.x.com. — [OpenTweet price table](https://opentweet.io/x-api-pricing); [Postzen](https://www.postzen.dev/blog/twitter-api-pricing)
- n8n’s X node still documents Tweet operations: create or reply, delete, search, like, and retweet, plus create a direct message. The page does not mention drafts or an approval state. The like operation is documented there even though the April 2026 changelog says likes were removed from self-serve tiers. — [n8n X node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.twitter/); [X API changelog mirror](https://x-preview.mintlify.app/changelog)
- IFTTT still lists X actions that “post a new tweet,” post a tweet with an image, and post a tweet with video. The action text says affiliate URLs in the tweet text cause an action error. No draft or approval step is described. Triggers include “New tweet by you,” mentions, search, and a specified user’s tweets. — [IFTTT X](https://ifttt.com/twitter)
- Buffer’s help center lists X/Twitter profiles as a publishing, analytics, and engagement channel. Other publishing channels on that page: Facebook Pages, Facebook groups (notification publishing only), Instagram business/creator, Instagram personal (notification only), LinkedIn Pages, LinkedIn profiles, Pinterest, TikTok, Google Business Profiles, Start Pages, Mastodon, YouTube Shorts, Threads, Bluesky, and Substack. The unsupported list on that page names Snapchat, Reddit, WhatsApp, Telegram, Twitch, OnlyFans, and lemon8. Discord and Patreon are not in the supported table. — [Connecting channels to Buffer](https://support.buffer.com/en-us/articles/connecting-your-channels-to-buffer-HvWLgAJvL9)
- Buffer’s Team-style permission model: a user with “Needs Approval” can create drafts and request approval; they cannot publish. Owners and Full Access users approve from an Awaiting Approval tab, can edit, then Add to Queue or Schedule Post, or Reject. Posts created through the Buffer API, the Buffer MCP server, or a third-party app by a Needs Approval member stay in Drafts until an approver moves them. Collaboration email can notify approvers. — [Buffer draft approval](https://support.buffer.com/en-us/articles/requesting-approval-and-approving-draft-posts-57li7M8tDA); [Buffer permissions](https://support.buffer.com/en-us/articles/adding-users-and-setting-up-permissions-ixjiLpe2fd)
- Publer says that because of “the Twitter Enterprise API cost,” Twitter accounts are supported only on a paid Publer subscription. The help page was updated 23 September 2026. — [Publer supported networks](https://publer.com/help/en/article/what-social-networks-are-supported-npoun1/)
- Typefully’s help center, dated 11 August 2026, says you can create, schedule, and publish on X (posts, threads, and X Articles), LinkedIn profiles and Pages, Threads, Bluesky, Mastodon, and Substack Notes. X Articles cannot be cross-posted. — [Typefully help](https://support.typefully.com/en/articles/8728077-what-and-where-can-i-publish-with-typefully)
- Typefully’s own pages disagree about Instagram. The marketing homepage lists Instagram among current platforms. The scheduling page says native scheduling is X, LinkedIn, Threads, Bluesky, and Mastodon, and that Facebook, Instagram, and TikTok are still to come. — [typefully.com](https://typefully.com/); contradicted by [Typefully scheduling](https://typefully.com/social-media-scheduling) and, for Instagram, by the 11 August 2026 help article above
- Octopost’s GitHub-release page shows a workflow on `release: published` that POSTs to `https://octopost.ink/api/posts` with `platforms: ["twitter"]` and `queueStatus: "pending"`. It says pending posts wait in an approval queue. Publishing without review is a different field, `published: true`. The page says other connected accounts can be added to `platforms`, but it does not name Discord, Telegram, or Patreon. It says a link in the main post counts as 23 characters toward 280, and that one release (main post plus a reply with the link) costs 14 of Octopost’s own monthly X units. Trial offered as 7 days for $1. Vendor page. — [Octopost GitHub release](https://octopost.ink/cross-post-github-release)
- Ship 2 Post’s marketing says GitHub releases become drafts for X and other networks, held for one-click approval, with per-channel autopublish as an opt-in. Vendor page, not independently verified. — [Ship 2 Post](https://s2p.dev/auto-post-github-releases-to-social-media)
- SocialHandoff’s help page says a GitHub release webhook or `socialhandoff-announce-action` creates a draft for X, LinkedIn, Bluesky, or Mastodon, and “It publishes only after you approve it” unless an agent was promoted to auto-publish. The action “does not publish on its own.” Vendor page. — [SocialHandoff GitHub releases](https://socialhandoff.com/help/github-releases/)

Judged against the four criteria:

- Direct `POST /2/tweets`: (a) no, the caller must hear about the release, (b) the caller writes the text, (c) no, the create call posts, (d) X only.
- n8n X “Create” and IFTTT “Post a tweet”: (a) if some trigger fires first, (b) yes, mapped text, (c) no, immediate-send when that action runs, (d) yes if the workflow has other actions. A human gate is possible only by adding a wait or manual step before the X node.
- Buffer for X: (a) not a GitHub release product; an API client or Zapier must create the update, (b) yes, drafts, (c) yes, when the API actor has Needs Approval, (d) yes among Buffer’s channels, which exclude Telegram, Discord, and Patreon.
- Publer for X: (a) external via Zapier or its API, (b) yes, (c) yes, draft and pending-approval states, (d) yes, including Telegram, not Discord or Patreon. X accounts require a paid Publer plan.
- Typefully: (b) yes, drafts and scheduling are documented, (c) a team approval queue was not found on the help page, (d) X plus LinkedIn, Threads, Bluesky, Mastodon, and Substack Notes per the help center. No Discord, Telegram, or Patreon.
- Octopost, Ship 2 Post, SocialHandoff: vendor-claimed (a)(b)(c) for X. Only Ship 2 Post’s site also names Discord. None of the three pages name Telegram or Patreon.

### Inferences

- A release note that includes the GitHub or PyPI URL is the expensive X API case on the 20 April 2026 rate ($0.20), not the $0.015 plain-text rate. Octopost’s “14 units” figure is its own plan accounting, not that X API price.
- Compose-then-approve on X is a property of the scheduler (Buffer, Publer, or the vendor release tools), not of the X create-post endpoint.
- n8n still documenting “like a tweet” does not mean self-serve X API likes still work after the April 2026 removal.

### Gaps

- docs.x.com and developer.x.com returned 403 to the fetch tool on 25 October 2026, so the $0.015 / $0.20 rates were not read off the first-party host. The mirror, OpenTweet, and Postzen agree with each other; the older pilot and the undated S3 snapshot still show about $0.01 for content create.
- The changelog entries are written as “Today” except where they give an effective date. The calendar date of the original pay-per-use launch, apart from the 20 April 2026 price change, was not on the fetched page.
- Article draft endpoint paths were not named in the changelog blurb.
- Zapier’s current X action list was not fetched.
- No source here confirms that Buffer or Typefully can subscribe to a GitHub `release` event without another connector in front.

## Patreon: does Patreon offer scheduled posts, a public post API for creators, or third-party schedulers (including any that cross-post to Patreon)?

### Takeaway

Creators can schedule, draft, and edit posts in Patreon’s own editor. The public API v2 can read posts and can notify you when a post is published. It cannot create them. A Patreon staff reply on 23 April 2026 said there is no way to create posts through the API. Zapier’s published Patreon operations are membership events only. Buffer and Publer do not list Patreon as a destination.

### Cited Findings

- Patreon Help Center, “Scheduled posts,” updated 6 July 2026: in the post creator you can schedule a publish date and time. Steps are Create → Post, title required, optional attachments, toggle “Set publish date,” then Schedule. You can schedule in the future or backdate. You can turn off member notification. Unscheduling turns off “Set publish date” and can leave the post as a draft or publish it now. — [Scheduled posts](https://support.patreon.com/hc/en-us/articles/360031956632-Scheduled-posts)
- “Posting to your Patreon” says that when the post is ready you click Publish or schedule the publish date, and that the app auto-saves drafts. Audience, collections, previews, and tags are post settings. — [Posting to your Patreon](https://support.patreon.com/hc/en-us/articles/115004048046-Posting-to-your-Patreon)
- Early access is a separate control: paid audience, “Offer early access,” public time at least 24 hours out, and it can be combined with a publish date. It is not available in the app’s post editor; desktop or mobile web is required. — [Early access posts](https://support.patreon.com/hc/en-us/articles/115001971426-How-do-I-set-up-an-early-access-post)
- API docs: “Public API v1 is retiring on October 7, 2026. Calls to v1 will stop working after that date.” Integrations must move to v2. An extension requested by 7 October 2026 can keep v1 through 20 January 2027. — [Patreon API reference](https://docs.patreon.com/)
- v2 post endpoints in those docs are `GET /api/oauth2/v2/campaigns/{campaign_id}/posts` and `GET /api/oauth2/v2/posts/{id}`, both requiring the `campaigns.posts` scope. The reference also documents `POST /api/oauth2/v2/lives` for a livestream and `POST /api/oauth2/v2/webhooks`. It does not document a POST that creates a campaign post. Post attributes that can be read include `content`, `title`, `is_public`, `published_at`, `url`, and `tiers`. — [Patreon API reference](https://docs.patreon.com/)
- v2 webhooks can be subscribed to `posts:publish`, `posts:update`, and `posts:delete`, which fire when a post is published, updated, or deleted. That is Patreon calling your URL, not you creating a post. — [Patreon API reference](https://docs.patreon.com/)
- On the Patreon Developers forum, staff account @noertap replied on 23 April 2026: “Currently there is no way to create posts through the api.” A later commenter wrote that Patreon support had told them they have “no attention to ever allow API posting,” and that they would have preferred an API that saved a draft for manual approval. That “no intention” sentence is a user’s report of a support conversation, not a second staff post. — [Creating Posts Via API](https://www.patreondevelopers.com/t/creating-posts-via-api/11305)
- Zapier’s Patreon app page lists six operations, all events: Delete Member, Delete Member Pledge, New Member, New Member Pledge, Updated Member, Updated Member Pledge. No create-post action and no new-post trigger appear in that list. Popular pairings on the page include Patreon + Discord, Patreon + Slack, Patreon + Hootsuite, and Patreon + GitHub, but those are listed as app combinations, not as a Patreon write of a post. — [Zapier Patreon](https://zapier.com/apps/patreon/integrations)
- Make.com’s Discord–Patreon workflow picker shows Patreon actions “Get a Campaign” and “Get a Member,” not a create-post action. — [Make Discord and Patreon](https://www.make.com/integrations/discord/patreon)
- IFTTT’s Patreon page says Patreon applets can “launch and track campaigns, posts, and memberships,” shows a “New campaign” polling trigger and a “List campaigns” query, and says you can share new Patreon posts into Discord. The fetched page did not list a Patreon action that creates a post. — [IFTTT Patreon](https://ifttt.com/patreon); [IFTTT Discord and Patreon](https://ifttt.com/connect/discord/patreon)
- Buffer’s supported-channel table does not include Patreon. — [Connecting channels to Buffer](https://support.buffer.com/en-us/articles/connecting-your-channels-to-buffer-HvWLgAJvL9)
- Publer’s 23 September 2026 network list does not include Patreon. — [Publer supported networks](https://publer.com/help/en/article/what-social-networks-are-supported-npoun1/)
- Ship 2 Post’s destination write-ups name LinkedIn, X, Instagram, Facebook, Threads, Discord, Bluesky, Reddit, Slack, Mastodon, YouTube descriptions and Community posts, and a Hacker News draft you submit manually. The page invites requests for “a destination not listed.” Patreon and Telegram are not in the published list. — [Ship 2 Post integrations](https://s2p.dev/integrations)
- `Shynixn/PatreonPostApi` (Papoa) states that the official API has no POST for creating or publishing posts and that headless browsers are blocked by Cloudflare. Its workaround is a Chrome extension running inside a browser where the creator is already logged in; the extension polls a job queue and fills the Patreon composer. Credentials are not sent to the service, according to the README. This is unofficial browser automation, not a Patreon-supported scheduler. — [Shynixn/PatreonPostApi](https://github.com/Shynixn/PatreonPostApi)

Judged against the four criteria:

- Patreon editor scheduling: (a) no, a person opens the editor, (b) yes, the editor is the draft, (c) yes, a scheduled post can be edited or unscheduled before it publishes, (d) Patreon only.
- Patreon API v2: (a) it can emit `posts:publish` after a human has published, (b) no create template, (c) no, because it cannot create the post, (d) not a publishing channel for a bot.
- Zapier, Make, IFTTT, Buffer, Publer, Ship 2 Post: no cited create-or-cross-post into Patreon. IFTTT and Zapier move membership or “new Patreon post” signals out of Patreon toward other apps.
- PatreonPostApi: (a) a caller can enqueue a job, (b) the job carries post metadata, (c) the README does not document a human approval step inside Patreon before the extension submits, (d) Patreon only, and only while a logged-in browser is open.

### Inferences

- Patreon is a manual last step. A release pipeline can remind a human, or at best drive an unsupported browser session. It cannot call a supported “create post” API as of the 23 April 2026 staff reply and the v2 reference.
- The in-product scheduler already is the approval and edit step, but only after someone pastes the release note into Patreon.
- v1 retirement on 7 October 2026 does not add posting. The migration note tells clients to move reads and webhooks to v2.

### Gaps

- IFTTT’s full Patreon trigger list was incompletely extracted. The page markets “share new Patreon posts,” but the named trigger in the fetch was “New campaign,” so it is unclear whether a distinct new-post trigger exists.
- Hootsuite appears as a Zapier “popular integration” next to Patreon. That does not show Hootsuite publishing to Patreon, and Hootsuite’s own channel list was not fetched.
- No source found for a maintained, Patreon-sanctioned third-party scheduler that cross-posts into Patreon.

## Cross-posters aimed at open-source maintainers, and exactly which networks they hit

### Takeaway

The verified maintainer paths are single-network or do-it-yourself: Discord’s GitHub webhook, a Discord release Action, and hand-written GitHub Actions. Productized “one release, many networks, then approve” tools exist as vendor sites (Ship 2 Post, SocialHandoff, Octopost). Their stated network lists do not include both Telegram and Patreon. General schedulers that already cross-post (Buffer, Publer, Typefully) are not GitHub-release products, and none of them include Patreon.

### Cited Findings

- Discord’s GitHub-compatible webhook posts GitHub events, including `release`, into one Discord channel. Immediate-send. Networks: Discord only. — [Webhook resource](https://docs.discord.com/developers/resources/webhook)
- `SethCohen/github-releases-to-discord` posts a formatted release embed to one Discord webhook. Immediate-send. Networks: Discord only. — [GitHub Marketplace](https://github.com/marketplace/actions/github-releases-to-discord)
- A public sample workflow, `avelikiy/great_cto` `.github/workflows/announce.yml`, is triggered on GitHub `release: published`. Its header comment says it posts to Twitter/X, Discord, Slack, Mastodon, and Bluesky. The retrieved file body shows implemented steps for X (`nearform-actions/github-action-notify-twitter`), a Discord webhook, and a Slack webhook, each with `continue-on-error`. Mastodon and Bluesky steps were named in the comment and were not in the retrieved portion of the file. Immediate-send. No approval step is in the retrieved YAML. — [announce.yml](https://github.com/avelikiy/great_cto/blob/main/.github/workflows/announce.yml)
- Ship 2 Post (vendor) says one GitHub release fans out to LinkedIn, X, Threads, Bluesky, Reddit, Facebook, Instagram, YouTube (including Community tab copy), Hacker News (draft you submit yourself), Substack, Mastodon, Discord, Slack, and signed webhooks. Default is a review queue; autopublish is opt-in per channel. Telegram and Patreon are not listed. — [Auto-post GitHub releases](https://s2p.dev/auto-post-github-releases-to-social-media); [Integrations](https://s2p.dev/integrations); [Features](https://s2p.dev/features)
- SocialHandoff (vendor) says a GitHub release or its GitHub Action creates drafts for X, LinkedIn, Bluesky, and Mastodon, cited back to the release, published after inbox approval. The use-case page describes an X thread, a Bluesky thread, one LinkedIn post, and a Mastodon post sized to 500 characters. Discord, Telegram, and Patreon are not named. — [GitHub releases help](https://socialhandoff.com/help/github-releases/); [Release announcements](https://socialhandoff.com/use-cases/release-announcements/)
- Octopost (vendor) shows a GitHub Actions example whose `platforms` array is `["twitter"]`, with `queueStatus: "pending"` for approval or `published: true` for immediate send. It says any other connected account can be added to that array and that networks which support threads get a reply chain. The page does not enumerate those other networks. — [Octopost](https://octopost.ink/cross-post-github-release)
- Buffer is a general cross-poster, not a release-note product. Publishing destinations on its help page: Facebook Pages, Facebook groups (notification only), Instagram business/creator, Instagram personal (notification only), X, LinkedIn Pages, LinkedIn profiles, Pinterest, TikTok, Google Business Profiles, Start Pages, Mastodon, YouTube Shorts, Threads, Bluesky, Substack. Not Discord, Telegram, or Patreon. Approval exists for API-created drafts when the member Needs Approval. — [Buffer channels](https://support.buffer.com/en-us/articles/connecting-your-channels-to-buffer-HvWLgAJvL9); [Buffer approval](https://support.buffer.com/en-us/articles/requesting-approval-and-approving-draft-posts-57li7M8tDA)
- Publer is a general cross-poster. As of 23 September 2026: Facebook, Instagram business, X (paid plans only), LinkedIn, Pinterest, Google Business Profile, YouTube, WordPress, TikTok, Telegram, Mastodon, Threads, Bluesky. Not Discord or Patreon. Zapier can create a post as publish-now, scheduled, or draft, and can observe pending approval. — [Publer networks](https://publer.com/help/en/article/what-social-networks-are-supported-npoun1/); [Publer Zapier](https://publer.com/help/en/article/how-to-connect-to-zapier-and-automate-your-workflows-18mun8n/)
- Typefully help, 11 August 2026: X, LinkedIn, Threads, Bluesky, Mastodon, Substack Notes. Not Discord, Telegram, or Patreon. Instagram is claimed on the homepage and described as not-yet-shipping on the scheduling page. — [Typefully help](https://support.typefully.com/en/articles/8728077-what-and-where-can-i-publish-with-typefully); [typefully.com](https://typefully.com/); [Typefully scheduling](https://typefully.com/social-media-scheduling)
- n8n is a workflow runner rather than a release cross-poster. Documented nodes used here can send Discord, send Telegram, and create an X post. The Discord node can wait for an approval click. A community template also posts to LinkedIn and X after a Telegram review chat. Native Bluesky, Mastodon, Instagram, and YouTube Community nodes were not confirmed in the pages fetched. — [n8n Discord](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.discord/); [n8n Telegram](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.telegram); [n8n X](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.twitter/); [template 6148](https://n8n.io/workflows/6148-publish-linkedin-and-x-posts-with-telegram-bot-gemini-ai-and-vector-memory/)
- IFTTT is a connector catalog. Its Telegram page lists, among many services, X, Discord, Bluesky, Mastodon.social, Slack, LinkedIn, YouTube, Instagram, Threads, and GitHub. Actions that were actually read are immediate “Send message” (Telegram) and “post a new tweet” (X). — [IFTTT Telegram](https://ifttt.com/telegram); [IFTTT X](https://ifttt.com/twitter)

Adjacent networks these tools already treat as ordinary destinations, which makes them the likely later add-ons: Mastodon (Buffer, Publer, Typefully, SocialHandoff, Ship 2 Post), Bluesky (the same set plus IFTTT), Slack (Ship 2 Post, the sample GitHub Action, IFTTT’s service list), LinkedIn (Buffer, Publer, Typefully, Ship 2 Post, SocialHandoff), YouTube or YouTube Shorts (Buffer Shorts, Publer channels, Ship 2 Post Community copy), Instagram (Buffer, Publer, Ship 2 Post; Typefully’s own pages conflict).

### Inferences

- There is no verified maintainer cross-poster whose own docs say it delivers one release note to Discord, Telegram, X, and Patreon.
- Among vendor products aimed at GitHub releases, Ship 2 Post claims the widest set and is the only one in this set that names Discord. It still does not name Telegram or Patreon.
- Among verified schedulers, Publer is the one that already publishes to both Telegram and X, with drafts. Buffer covers X and the fediverse/Bluesky/LinkedIn side and has the clearest approval docs, but it does not publish to Telegram or Discord.

### Gaps

- Ship 2 Post, SocialHandoff, and Octopost were not corroborated with a source-code repository, a pricing page independent of their marketing sites, or a third-party review. Treat their network lists as vendor claims.
- The great_cto workflow’s Mastodon and Bluesky steps were not in the fetched portion. Only the comment and the X, Discord, and Slack steps are confirmed.
- Hootsuite, Later, and Fedica were not fetched. They may also cross-post to X and the adjacent networks; nothing found here shows them posting to Patreon.

## What would still have to be built if someone adopted the closest existing tool?

### Takeaway

The closest verified base is n8n, because one workflow can take a release webhook, template the text, stop on a Discord approval button, then immediate-send to Discord, Telegram, and X. Adopting it still means building that workflow, paying X per post, and handling Patreon by hand. No closer off-the-shelf tool was verified to include Patreon.

### Cited Findings

- n8n can start from a webhook, send a Discord message, and pause until an Approval button is clicked. — [n8n Discord and Patreon integration page](https://n8n.io/integrations/discord/and/patreon/); [n8n Discord node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.discord/)
- The same product can then “Send Message” on Telegram and “Create” a tweet on X. Those operations, as documented, do not themselves wait. — [n8n Telegram node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.telegram); [n8n X node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.twitter/)
- Patreon staff said on 23 April 2026 that posts cannot be created through the API, and the v2 reference only GETs posts. Scheduling exists only inside Patreon’s editor. — [Developers forum](https://www.patreondevelopers.com/t/creating-posts-via-api/11305); [API reference](https://docs.patreon.com/); [Scheduled posts](https://support.patreon.com/hc/en-us/articles/360031956632-Scheduled-posts)
- If the X post contains the release URL, the 20 April 2026 changelog rate is $0.20 per post rather than $0.015. — [X API changelog mirror](https://x-preview.mintlify.app/changelog)
- Discord webhook content is limited to 2000 characters; Telegram `text` is 1–4096 characters; Octopost states X posts must fit 280 characters with a link counted as 23. A single release body does not fit all three without trimming. — [Webhook resource](https://docs.discord.com/developers/resources/webhook); [sendMessage](https://core.telegram.org/bots/api/methods/sendmessage.md); [Octopost](https://octopost.ink/cross-post-github-release)
- Publer would be the closer product if the requirement were “Telegram and X with a draft/approval state, plus Mastodon, Bluesky, LinkedIn, Instagram, and YouTube,” but its network list omits Discord and Patreon, and it is not a GitHub release listener by itself. — [Publer networks](https://publer.com/help/en/article/what-social-networks-are-supported-npoun1/)
- Ship 2 Post would be the closer product if its marketing is accurate and the requirement were “GitHub release in, approve once, fan out to Discord and X plus Mastodon, Bluesky, LinkedIn, Slack, Instagram, and YouTube Community.” Its site does not list Telegram or Patreon, and the behavior was not verified beyond that site. — [Ship 2 Post integrations](https://s2p.dev/integrations)

### Inferences

Adopting n8n as the base, the pieces that do not already exist as a maintained release announcer are:

- The workflow itself: GitHub or PyPI release webhook in, one template per destination, a Discord Approval wait in a private channel, then publish. n8n supplies the nodes, not a release-notes product.
- Per-network truncation. Discord content is 2000 characters, Telegram text is 4096, X is 280 with links counted inside the cap. The release changelog has to be cut or linked.
- X billing. Each approved announcement that includes a URL is a metered write at the URL rate on the April 2026 schedule, on top of whatever n8n hosting costs.
- Patreon. After approval, a person still has to create or schedule the post in Patreon’s editor. An API client that creates or schedules a Patreon post cannot be built against the documented public API. The only cited alternative is unofficial in-browser automation such as PatreonPostApi, which needs a logged-in browser and is not a supported integration.
- A single shared editor. n8n’s approval buttons approve or reject; they are not the Buffer/Publer draft editor. Editing the text before send means adding a form step or editing the workflow data. Buffer and Publer already have that editor, but then Discord (and, for Buffer, Telegram) and Patreon still have to be added beside them.
- If Ship 2 Post were adopted instead, the unbuilt part would be Telegram plus Patreon, plus a check that its approval queue behaves as advertised. Patreon would remain manual for the same API reason.

### Gaps

- No page fetched describes a PyPI-specific announcer. The release-event sources are GitHub `release` webhooks and Actions. A PyPI project event would need its own webhook or poller in front of the same posters. That adapter was not researched here.
- It was not confirmed whether n8n’s X credential wizard still succeeds on pay-per-use accounts, or whether it still expects a legacy Basic/Pro subscription.
- “Closest” is a judgment among the tools this pass could verify. A maintainer product shipped after these pages were fetched, or a Discord bot not listed on the Marketplace page that was read, could be closer.
