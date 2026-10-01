# Handover — V16.7.23 (v193)

## Start point
Continue from **V16.7.22 (v192)**. The existing handover archives from v167 through v192 are retained unchanged; v175 has no archive in this repository.

## This release
- Adds the current v193 handover download to the main page.
- Restores the complete list of the 25 available earlier handover ZIPs, with the size labels supplied for each version.
- Records exact historical ZIP byte counts and labels in `HANDOVER_ARCHIVE_INDEX_V16_7_23.json`.
- Fixes the release-note control so one click produces one action, and makes it keyboard accessible.
- Keeps the Shani Blue / Kuber Gold styling and existing bank, revenue-snapshot, cinema and owner content.
- Clarifies that the financial figures are static handover content, not a live banking feed.

## Archive size convention
Historical labels are KiB rounded up: `ceil(file_bytes / 1024)`. The manifest records both the exact bytes and the displayed label. All 25 linked archive files were present and verified while preparing this handover.

## Package contents
The v193 ZIP contains the current `index.html`, `README.md`, `.github/`, and `ops/` source tree. It does not embed earlier handover ZIPs inside itself; the main page links to them separately. The one-month chat archive remains a separate root download: `Vyomaraj-All-Chats-Database-One-Month.md` (34 entries through V16.7.22) plus `Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip`, which contains the database, `Git-Commits-One-Month.txt`, and `All-Chats-Array-From-Index.txt`.

## Verification
- Confirm every historical path in the manifest exists and its byte count and rounded label match.
- Confirm all 25 historical ZIPs pass `ZipFile.testzip()`.
- Confirm the v193 archive opens and includes the current page and handover manifest.
- On an Arena-ref run, the sync workflow pushes only that exact branch to PRIMARY and SECONDARY, verifies each remote SHA, refuses force updates, and skips DR-to-main failover logic.
- This release does not publish GitHub Pages or alter `main`; the Arena preview is the review target.
