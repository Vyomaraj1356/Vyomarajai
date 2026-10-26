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
