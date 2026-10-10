# Production execution script — Vyomaraj/Jarvis prompt runtime

**State:** a release-preflight script is added; this is not a production deployment or a claim that PR #61 is ready to merge.

## Run the script

From the root of a local clone of \`Vyomaraj1356/Vyomarajai\`:

\`\`\`sh
bash ops/jarvis/production_preflight.sh
\`\`\`

The script fails closed and:
1. Requires Python 3.10+.
2. Parses \`config/ai/PROMPT_REGISTRY_V1.json\`, validates each preset and allowed role, and checks core research, child education/safety, publishing, legal-review and release-gate presets.
3. Runs offline tests for \`ops/jarvis/llm_harness.py\`.
4. Verifies private local provider/DR environment files are not tracked and are Git-ignored.
5. Verifies preset discovery works without provider configuration or network access.

## Optional provider smoke test

Only when an operator deliberately requests a provider request:

\`\`\`sh
bash ops/jarvis/production_preflight.sh --provider-smoke-test
\`\`\`

Configure the approved endpoint, model and key via the ignored local env file or a deployment secret manager first. Never put secrets in Git, prompts, screenshots or logs. The smoke test sends one fixed non-sensitive prompt; it does not publish content or write business data. A response proves only that the request returned—not that the service is deployed, secure, monitored, tool-enabled or production-ready.

## Deliberate non-actions

This script does **not** merge the PR, deploy a server, enable tools, publish or schedule social content, send email, perform finance writes, trigger DR sync, or execute failover/failback. Those actions require separate access, authorization, safeguards and verified acceptance tests.

## Current release blockers

- PR #61 must pass required checks and be reviewed through the repository's normal merge process.
- Configure and owner-approve a provider/model and perform a separate provider smoke test.
- Deploy to an identified target environment, then verify the deployed commit, health checks, telemetry, cost/privacy settings and rollback.
- Existing CI diagnostics and Primary-to-DR sync failures are independent blockers. Do not treat this preflight as DR evidence or manually trigger/approve destructive sync based on this script.
