# Deep session re-integration audit — 2026-10-02

**Scope:** fixed branch `arena/01a0f634-vyomarajai` only. No push or merge to PRIMARY `main` was made.

## Current branch and upstream state

- Code integration merge: `f4b18c08ecfbb646f40f03acfa5b39c1f0650caf`; parents are the previous Arena release-page head `4800cf9d2e5de4679cdd1cd6f9ce535316aeb790` and the later Arena recovery branch head `94b8fbe21f0cd66a5f9de05a3065de727d85ff3f`. The first parent already contains PRIMARY `main` through `1347f7939157c4fe3a0d18d9141fb8d9bba0bed0`.
- The additional PRIMARY commits since the previous integration were `3d52194` (API ref endpoint change) and `1347f79` (verification trigger). The additional Arena commits `8611da4`, `ec11069`, `8439ddb`, `ec9ad0c`, `b04322f`, `d32fef5`, and `94b8fbe` introduced the recovery workflow/importer, fixed its export input, and then changed the DR writer.
- PR [#1](https://github.com/Vyomaraj1356/Vyomarajai/pull/1) is open, `CLEAN`/`MERGEABLE`, and unmerged. PRIMARY `main` remains at `1347f79`.
- The initial checkout reopened at `ab41354` with local files that looked untracked. I preserved the full snapshot in `stash@{0}`, fast-forwarded the local branch to the existing Arena tip, and compared the saved files with it: all 14 saved untracked files were byte-identical to the already-committed Arena copies; no unique local changes were lost. The stash remains intact.

## Session changes reintegrated

- Merged the latest `main` history into Arena and then incorporated all commits that had arrived on the Arena branch during this audit. The only conflict in the main integration was the workflow/heartbeat pair; the heartbeat records are a unique, chronologically sorted UTC union.
- Restored the previous tested exact-Git-ref DR workflow in the final tree. The incoming API workflow on `94b8fbe` was not selected: its run #352 succeeded in reading back the API-generated mirror ref, but the code only hard-fails a source/target SHA mismatch for `main`, not for `arena/*`. A green #352 therefore is **not** proof that the Arena PRIMARY and SECONDARY commit SHAs match. The earlier exact check in #316 applies only to the historical `18fde50` SHA.
- The guarded archive/`--force-with-lease` recovery logic in the retained workflow was not modified or invoked. The merge commit carries `[skip ci]` because the latest API run may have left a synthetic SECONDARY ref; an unskipped run of the older exact writer could enter that guarded recovery path. No authorization for that recovery was given. The current Arena tip therefore has **no new exact-SHA SECONDARY verification**.
- Preserved the new read-only Arena recovery workflow and importer from the concurrent Arena updates. The importer safely extracts archives without executing members, ignores local `.arena-recovery/` output, and now keeps absolute paths, raw session IDs/chat numbers, and staged chat text out of uploaded reports. Its run #350 passed before these privacy hardenings, but that push run had no Arena export directory; it scanned repository evidence only. Private Arena sessions remain **UNRECOVERED — SOURCE NOT AVAILABLE** unless an owner-provided export is mounted.
- Removed stale `/health`, `/download-apk`, root-absolute, and unavailable Mac-ZIP links from the legacy landing alias by redirecting `landing.html` and `Index.html` to canonical `index.html`. The canonical page now links to the repository APK with an explicit version/signing caveat, links the preserved Git commit list and recovery scope, and corrects the v194/current-catalogue labels. README navigation was rebuilt. Historical v194 ZIP contents were not rewritten.

## Validation

- Local HTML/link audit: zero missing local links or broken anchors in `index.html`, `Index.html`, `landing.html`, and `flow-diagram.html`; all 26 linked historical handover files exist. Root README has no missing local links.
- Parsed all 45 tracked JSON files. The canonical roster still has 13 categories, 133 sub-agents, and 421 products; the separate 394/12/52/5 readiness figures remain unreconciled rather than guessed.
- Python compilation and importer checks passed: release-version-only marker output, safe ZIP extraction, and ZIP path-traversal rejection. `node --check` passes for `preview-stable-fix.js`; two other tracked `.js` files (`multi-ai-coordination.js` and `shriyantra-protection.js`) contain only a Git fatal diagnostic, so they are not valid JavaScript. Those identical blobs already exist on PRIMARY `main`, were introduced without source in their parent commit, and have no tracked HTML/Markdown references. They were left untouched rather than inventing replacement code.
- The 34-chat archive remains exactly 3 expected members, 34 numbered entries, no duplicate entry numbers, V15.0–V16.7.22 scope, and unchanged commit references/Image 1 labels. SHA-256 remains `9d6e2033a43bb4906af63dd77098097c8ecbc576693d6af774a116ed3dd1b432`.
- The v194 archive remains 9 members and SHA-256 `79b17bcc6128014fe6fc13c72ff632fdf759b1ee5387b9ceec4f25dd520dc92a`. v168 and v193 archive hashes remain as listed in the archive index. No archive was rebuilt or replaced.
- The legal/safety text remains first-pass research and a proposed policy; it makes no compliance claim.

## DR, GitHub Pages, and remaining limits

- PRIMARY `main` runs #342, #343 and scheduled #344 failed in the API replication step. Actions log retrieval returned EOF, so the exact HTTP/assertion error is not claimed. No SECONDARY `main` SHA equality was established.
- Arena run #352 is green for the later API-written ref at `94b8fbe`, but that implementation does not require exact source-SHA equality on Arena refs. Its Actions log could not be retrieved; no target SHA is asserted here.
- The code-integration commit and subsequent documentation-only follow-ups used `[skip ci]` to avoid invoking the guarded archive/lease recovery without approval. An attempted manual dispatch of `arena-recovery.yml` was denied with HTTP 403 (`Resource not accessible by integration`); local importer tests passed, but no new GitHub push run exists for the code-integration merge or its documentation-only follow-ups.
- GitHub Pages still serves `main` at `/`. The Arena branch is not production-deployed; PR #1 has not been merged. The latest primary/secondary `main` sync remains unverified.
- No credential values were read, requested, or recorded.
