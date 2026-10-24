# Social Platform Operations — Evidence Gates

Status: proposed operational contract; documentation only. This file does not assert that any platform account, API, publisher, analytics feed, or scheduler is production-connected.

## Authority and safety

- Owner remains the final authority for public publishing, paid promotion, account-setting changes, deletions, replies with material risk, and access grants.
- Default to draft/review. Never publish solely because a content item exists in the registry.
- Use official platform APIs or an owner-approved third-party connector. Confirm the account identity, scopes, token expiry, and supported capabilities independently.
- Never place credentials, access tokens, account recovery details, private channel identifiers, or customer data in source control, public logs, prompts, or reports.
- Respect platform terms, local law, copyright/licensing, privacy, disclosure, age suitability, and AI-generated-content labeling requirements.
- No artificial views, likes, follows, comments, engagement exchanges, or deceptive automation.

## Per-platform evidence record

For each platform/account, record only sanitized evidence:

1. Platform and account alias (no secrets; public identifiers only when deliberately approved).
2. Connection mechanism and owner-approved scope list.
3. Last successful read timestamp and a non-sensitive request/result reference.
4. Last successful publish test, only after explicit owner authorization, including platform receipt/post URL and idempotency key.
5. Analytics freshness and metric definitions, plus comparison with the platform-native dashboard.
6. Token expiry/permission health and alert status.
7. Supported media/content formats, rate limits, restrictions, and known gaps.
8. Approval policy, rollback/takedown path, accountable owner, and next review date.

Use explicit states: `not_configured`, `configured_unverified`, `read_verified`, `publish_verified`, `analytics_verified`, `degraded`, `revoked`. Do not infer one state from another. Configuration or a successful CI test is not proof of a live account connection.

## Required gates before any publishing rollout

- [ ] Confirm account ownership and least-privilege permissions.
- [ ] Read-only authentication test passes; secrets remain redacted.
- [ ] Platform-specific content and media validation passes.
- [ ] Owner approval is recorded for the exact content, destinations, and intended time.
- [ ] Duplicate prevention uses a stable idempotency key; retries are bounded.
- [ ] A dry-run produces a preview without an external write.
- [ ] If an authorized test publish is performed, verify it by reading back the platform receipt/post and URL.
- [ ] Compare analytics with the platform-native dashboard; missing data must not be reported as zero.
- [ ] Confirm alerts, token-revocation handling, audit trail, and takedown/rollback procedure.
- [ ] Roll out one platform/account at a time and revalidate after permission or API changes.

## Initial rollout order

1. YouTube and Threads: already present in the connected Metricool brand configuration, but account-level analytics still require reconciliation with native dashboards. Treat as `configured_unverified` until the evidence record is complete.
2. Instagram and Facebook: verify Meta account/Page linkage, scopes, media constraints, and Insights independently.
3. X and LinkedIn: verify official account access, post capabilities, and analytics independently.
4. Pinterest, Bluesky, Twitch, and other channels: enable only where a supported and authorized connector exists.
5. Telegram, WhatsApp, Discord, Reddit, Snapchat, Vimeo, Tumblr, and Mastodon: treat as separate integration projects; do not imply that a scheduler supports every action on every service.
6. TikTok: keep disabled in the India operating plan until current legal, platform, account, and API-access requirements have been checked and approved.

## Analytics and Kuber reconciliation

- Store platform-reported metrics with source, timestamp, timezone, period, currency, and metric definition.
- Distinguish unavailable/null, stale, zero, estimated, and settled values.
- Views and engagement are not revenue. Reconcile platform earnings, affiliate conversions, sponsorship invoices, fees, refunds, and received payments separately.
- Preserve source receipts and an append-only audit trail; do not fabricate missing values.

## Current evidence boundary

The connected Metricool brand configuration has exposed YouTube and Threads network entries. A recent query for scheduled posts covering 24 October through 7 November 2026 returned an empty list. A recent analytics query returned zero-valued and null fields; this is insufficient to establish real audience activity, revenue, or end-to-end publishing. No publishing test was performed as part of this check.

This document is a guardrail and rollout plan, not a claim that the gates have passed.
