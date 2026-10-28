# Public Secret Diff Guard

## Purpose

The `Public Secret Diff Guard` workflow is a lightweight, dependency-free safety check for accidental credential additions to the public Vyomaraj repository.

It inspects only **added lines in a pull-request diff** and newly added sensitive file paths. When it finds a known token shape or private-key header, it reports the path, line number, and rule identifier—not the matched value or surrounding line.

## Covered indicators

- Common OpenAI and Anthropic API-key shapes
- GitHub personal-access-token shapes
- AWS access-key IDs
- Google API-key shapes
- Slack token shapes
- Stripe live-secret-key shapes
- PEM private-key headers
- Newly added `.env`/private environment files and common private-key container extensions

Explicit `.example`, `.sample`, `.template`, and `.dist` templates are allowed by path policy.

## Workflow-change risk rules

For newly added lines in GitHub Actions workflow YAML or composite-action YAML, the same guard also blocks these high-risk constructs by default:

- `pull_request_target` triggers, including inline and list-style trigger declarations
- Self-hosted runners, including list entries used with a multi-line `runs-on` value
- `permissions: write-all`
- Explicit `contents: write` or `id-token: write`
- `persist-credentials: true` in checkout configuration

These rules are intentionally conservative. A legitimate use requires a separate, explicit security review and a deliberate policy change; do not bypass the scanner by hiding the setting in comments or documentation. The scanner ignores commented lines and does not apply workflow-specific rules to ordinary docs/tests.

This remains a diff guard, not a complete GitHub Actions policy engine. It does not parse the entire YAML execution graph, validate action pinning, evaluate repository rulesets, or prove that branch protection requires the check. Protect the workflow and guard implementation with owner review and repository rulesets.

## Limitations and safe operation

- This is a **best-effort accidental-leak guard**, not a complete secret scanner.
- It does not read or scan unchanged files, historical Git blobs, deleted lines, or the entire working tree.
- It does not replace GitHub secret scanning, independent repository-history review, or credential rotation.
- It does not prove that a repository is free of secrets.
- The scanner never prints matched text. Do not add debug output that emits diff lines.
- Existing legacy tracked material requires a separate owner-reviewed remediation. This workflow does not delete, rewrite history, or alter any protected DR path.
- Preserve `ops/jarvis/jarvis.env` in DR under policy B; this guard does not inspect or change the DR repository.

## Verification

The workflow runs only on pull requests with `contents: read`, uses Python's standard library, and performs no network calls beyond GitHub Actions checkout. It creates no resources, uses no secrets, and makes no repository writes.
