# Vyomaraj + Jarvis — Zero-Cost India-First Observability Plan

**Status:** PROPOSED / NOT CONNECTED  
**Budget policy:** INR 0 recurring subscription and no metered overages without explicit owner approval.  
**Data residency:** Prefer India for hosted telemetry. Verify the actual region for logs, metrics, traces, backups, and support access before sending production data.  
**Scope:** Observability only. This plan does not provision accounts, install agents, change Render settings, or enable external telemetry.

## Decision

Do not depend on Datadog for this deployment. Use vendor-neutral OpenTelemetry instrumentation and choose one of these paths:

1. **Preferred hosted candidate:** Grafana Cloud Free. Official Grafana documentation currently lists India on AWS `ap-south-1` and GCP `asia-south1`. The public pricing page describes Free as always $0, with no credit card required and no charges; published examples include 10,000 active metric series/month, 50 GB logs/month, 50 GB traces/month, and 14-day retention. Recheck the current product-specific quota at signup; reaching a Free-tier limit may block or constrain ingestion rather than provide unlimited service.
2. **Self-hosted fallback:** Prometheus + Grafana OSS for metrics/dashboards, Loki for logs, Tempo for traces, and Uptime Kuma for external uptime checks. Software licences are free; compute, storage, backups, and operations are not automatically free. Run only on already-available free/zero-incremental-cost capacity.
3. **Alternative candidate:** SigNoz Community Edition self-hosted. Do not select its paid cloud tier for the $0 target without separate owner approval.

Official references checked 2026-10-22: [Grafana Cloud regional availability](https://grafana.com/docs/grafana-cloud/platform/security-and-account-management/account-management/regional-availability/), [Grafana pricing](https://grafana.com/pricing/), [pricing and usage](https://grafana.com/docs/grafana-cloud/platform/pricing-and-usage/). The India region is listed; this does not create a stack or prove that this user's account has been configured. Verify the exact region on the created stack and each telemetry service before connecting. Free plan is the only hosted tier allowed by this project’s budget policy; never switch to Pro.

## Existing baseline

- Render service: `vyomaraj-public-preview`
- URL: `https://vyomaraj-public-preview.onrender.com`
- Current Render plan observed: `free`; service region observed: `singapore`.
- Health endpoint: `/healthz`; a successful response proves process liveness only, not database/provider readiness, data integrity, or disaster recovery.
- The existing integration truth matrix marks production observability as partial and the full control plane / runtime DR as not proven.
- No Grafana Cloud, SigNoz, Prometheus, Loki, Tempo, or Uptime Kuma integration has been verified as connected to the application.

## Required signals

1. **Availability:** HTTP status, response time, uptime and TLS/certificate failures.
2. **Application:** request counts, latency percentiles, errors, restarts, and saturation where measurable.
3. **Dependencies:** database connection/readiness and provider availability, without logging credentials or full payloads.
4. **Security:** authentication failures, authorization denials, rate-limit events, suspicious activity, and secret-redaction failures.
5. **DR:** replication lag, last successful backup, restore-drill timestamp, and independent read-after-write evidence. A Git sync success is not application DR proof.
6. **Cost guardrails:** event volume, telemetry bytes, retention, active series, and remaining free quota.

## $0 guardrails

- No paid trial, paid tier, metered add-on, or automatic upgrade.
- Select the Free plan only. Grafana's current public pricing page says no credit card is required and describes Free as $0 with no charges. Do not upgrade to Pro; keep usage within the published limits and stop optional telemetry if a quota is approached.
- Set conservative sampling, short retention, bounded labels/cardinality, and log-volume limits.
- Alert before free-tier quotas; stop optional export before reaching the limit. Keep local health checks operating if hosted export is disabled.
- Never collect secrets, authorization headers, cookies, passwords, raw database connection strings, private prompts, or unredacted personal data.
- Use TLS and least-privilege, write-only telemetry credentials; store them only in protected deployment secrets.
- No public dashboards or unauthenticated metrics endpoints.
- Keep health probes separate from readiness checks. Readiness must not expose internal dependency details.
- Do not send production telemetry until region, retention, processor terms, access controls, and deletion behavior are reviewed.

## Implementation sequence

### Gate 0 — Account and cost preflight
- Create a new stack explicitly in India (`ap-south-1` AWS or `asia-south1` GCP) only after account owner review; an existing stack's region cannot be changed.
- Confirm the stack details show India for Grafana, metrics, logs and traces endpoints; review data retention and access scope.
- Confirm the plan is Free and do not enable Pro, paid add-ons or Marketplace billing. Stay within current quotas; stop optional export rather than upgrade.

### Gate 1 — Baseline probes
- Add external checks for `/` and `/healthz` at a conservative interval.
- Do not treat `/healthz` as dependency readiness.
- Record expected status, timeout, and acceptable latency. Alert delivery is not proven until a test notification is received.

### Gate 2 — Minimal instrumentation
- Use OpenTelemetry SDK/exporter only after the destination and secret storage are approved.
- Begin with metrics and redacted structured logs; enable traces only if the free quota supports them.
- Exclude high-cardinality IDs and request/response bodies by default.

### Gate 3 — Acceptance tests
- Verify one synthetic test event reaches the chosen destination and is queryable.
- Verify a deliberate test error appears without secrets or private payloads.
- Verify quota/egress disablement does not break the application.
- Verify an alert reaches its configured receiver.
- Verify dashboards and ingestion are region-correct and access-controlled.
- Record timestamp, destination, test result, retention, quota and rollback instructions.

### Gate 4 — DR and operational acceptance
- Verify database writes with independent read-back; separately run a restore drill.
- Test exporter outage, destination quota exhaustion, and alert receiver failure.
- Do not claim production-ready until on-call ownership, retention, restore, and failure behavior are documented and tested.

## Registry status vocabulary

- **PRESENT:** plan/source exists.
- **CONFIGURED:** non-secret config validates.
- **CONNECTED:** authenticated live export to intended destination succeeded.
- **TESTED:** acceptance tests and alert delivery passed with evidence.
- **PRODUCTION-READY:** security, data residency, cost, recovery, access and rollback gates passed.

**Current status:** PRESENT (plan only). No monitoring provider is claimed connected or tested. No resources have been created by this document.
