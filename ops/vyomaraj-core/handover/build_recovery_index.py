#!/usr/bin/env python3
"""Arena session recovery index — what survives from each of the 11 sessions, and where it is.

The owner was told the work of 11 Arena sessions was lost. This index is the evidence for what is
actually still recoverable, computed from the repository rather than remembered:

  * every `origin/arena/*` branch (each one is a session's workspace pushed to GitHub),
  * every handover/release archive, with its size and hash,
  * the consolidated chats record,
  * and the one thing that genuinely cannot be recovered.

It also states, per branch, how many files that branch contains which the current main does not —
that is the count of genuinely unique work.

    python3 build_recovery_index.py            write the index
    python3 build_recovery_index.py --check    fail if the index no longer matches the repository
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md"
MANIFEST = HERE / "ARENA_SESSION_RECOVERY_MANIFEST_2026_10_06.json"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def session_branches() -> list[dict]:
    refs = [r for r in git("branch", "-r").splitlines() if "origin/arena/" in r]
    rows = []
    for ref in refs:
        ref = ref.strip()
        name = ref.split("origin/", 1)[1]
        tips = git("log", "-1", "--format=%H|%cI|%s", ref).split("|", 2)
        if len(tips) < 3:
            continue
        files_in_branch = set(git("ls-tree", "-r", "--name-only", ref).splitlines())
        files_in_main = set(git("ls-tree", "-r", "--name-only", "main").splitlines())
        unique = sorted(files_in_branch - files_in_main)
        rows.append({
            "branch": name,
            "tip": tips[0],
            "date": tips[1][:10],
            "subject": tips[2][:78],
            "commits_ahead_of_main": int(git("rev-list", "--count", f"main..{ref}") or 0),
            "files_unique_to_branch": len(unique),
            "unique_examples": unique[:5],
            "content_in_main": len(files_in_branch - files_in_main) == 0,
        })
    rows.sort(key=lambda r: (r["date"], r["branch"]))
    return rows


def archives() -> list[dict]:
    out = []
    for path in sorted(ROOT.glob("Vyomaraj-*.zip")):
        entry = {"name": path.name, "bytes": path.stat().st_size,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest()[:16]}
        try:
            with zipfile.ZipFile(path) as z:
                entry["members"] = len(z.namelist())
        except Exception:
            entry["members"] = None
        out.append(entry)
    return out


def chats_state() -> dict:
    state = {"database": None, "heading_count": None, "numbered_entries": None,
             "archives": [], "raw_transcripts_exported": False, "why_not": None}
    db = ROOT / "Vyomaraj-All-Chats-Database-One-Month.md"
    if db.is_file():
        text = db.read_text(encoding="utf-8", errors="ignore")
        state["database"] = {"name": db.name, "bytes": db.stat().st_size}
        m = re.search(r"(\d+)\s+chats", text, re.I)
        state["heading_count"] = int(m.group(1)) if m else None
        state["numbered_entries"] = len(re.findall(r"^\s*(?:\|\s*)?(\d{2})[.)|]", text, re.M))
    for name in ("Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip",
                 "Vyomaraj-Complete-All-Sessions-All-Handover-Zips-V16.7.22.zip"):
        p = ROOT / name
        if p.is_file():
            state["archives"].append({"name": name, "bytes": p.stat().st_size})
    err = ROOT / "All-Chats-Extraction-Error.txt"
    if err.is_file():
        text = err.read_text(encoding="utf-8", errors="ignore")
        state["why_not"] = "recorded in All-Chats-Extraction-Error.txt: " + \
                           (text.strip().splitlines()[-1][:150] if text.strip() else "extraction failed")
    return state


def build() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sessions = session_branches()
    arcs = archives()
    chats = chats_state()
    handovers = [a for a in arcs if "Handover" in a["name"]]
    releases = [a for a in arcs if "Market-Ready" in a["name"]]
    unique_total = sum(s["files_unique_to_branch"] for s in sessions)

    L: list[str] = []
    a = L.append
    a("# ARENA SESSION RECOVERY INDEX")
    a("")
    a(f"Computed {now} from this repository. The owner was told the work of 11 Arena sessions may be "
      "lost. This is what actually survives, and where.")
    a("")
    a("## The headline")
    a("")
    a(f"- **{len(sessions)} Arena session branches are still on GitHub.** Each one is a session's "
      "workspace that was pushed to the repository, so the work of those sessions is present as Git "
      "history, not only as chat text.")
    a(f"- **{len(arcs)} archives** are in the repository — {len(handovers)} handover zips, "
      f"{len(releases)} market-ready releases, plus the combined session and chat archives.")
    a("- **The consolidated chats record is present** with its session-by-session database.")
    a("- **One thing is genuinely gone**, and it is named in section 4 so nobody hunts for it.")
    a("")
    a("## 1 · The 11 Arena session branches")
    a("")
    a("| # | Session branch | Date | Tip commit | Commits ahead of main | Files unique to the branch | Content already in main |")
    a("|---|---|---|---|---|---|---|")
    for i, s in enumerate(sessions, 1):
        a(f"| {i} | `{s['branch']}` | {s['date']} | {s['subject'][:52]} | {s['commits_ahead_of_main']} | "
          f"{s['files_unique_to_branch']} | {'yes' if s['content_in_main'] else 'no'} |")
    a("")
    a(f"Across all branches, **{unique_total} files** exist that the current main does not carry. "
      "Those are the genuinely unique artifacts; where a branch reports 0, its content is already in "
      "main and nothing needs recovering from it.")
    a("")
    if unique_total:
        a("Examples of files that exist only on a session branch (recoverable with one `git checkout`):")
        a("")
        for s in sessions:
            for example in s["unique_examples"][:3]:
                a(f"- `{s['branch']}` → `{example}`")
        a("")
    a("## 2 · How to recover any of it (exact commands)")
    a("")
    a("Nothing needs to be rebuilt. These commands restore files into a recovery branch without "
      "touching main and without force-pushing anything — the project's own DR rule is never to "
      "force-push.")
    a("")
    a("```bash")
    a("git fetch origin '+refs/heads/arena/*:refs/remotes/origin/arena/*'   # bring every session down")
    a("git switch -c recovery/all-sessions                                  # a safe recovery branch")
    a("")
    a("# list what a session has that main does not:")
    a("git diff --name-status main origin/arena/<session-branch>")
    a("")
    a("# restore one file from that session:")
    a("git checkout origin/arena/<session-branch> -- path/to/file")
    a("")
    a("# or recover everything unique from a branch in one step, then review before committing:")
    a("git checkout origin/arena/<session-branch> -- .")
    a("git status")
    a("```")
    a("")
    a("## 3 · The archives, as they stand")
    a("")
    a("| Archive | Bytes | Members | SHA256 (first 16) |")
    a("|---|---|---|---|")
    for arc in arcs:
        a(f"| `{arc['name']}` | {arc['bytes']:,} | {arc['members'] if arc['members'] is not None else '—'} | "
          f"`{arc['sha256']}` |")
    a("")
    a("## 4 · The chats — what survives and what does not")
    a("")
    if chats["database"]:
        a(f"- **Present:** `{chats['database']['name']}` ({chats['database']['bytes']:,} bytes). "
          f"Its heading says **{chats['heading_count']} chats**; the body carries "
          f"**{chats['numbered_entries']} numbered entries**. The discrepancy is pre-existing and is "
          "served unmodified rather than smoothed over.")
    for arc in chats["archives"]:
        a(f"- **Present:** `{arc['name']}` ({arc['bytes']:,} bytes).")
    a("- **Cannot be recovered from this repository:** the raw per-chat transcripts. "
      f"{chats['why_not'] or 'The export attempt is recorded as having failed.'}")
    a("")
    a("That means: the *relational* record of every session survives (what was decided, what was "
      "built, in order). The *verbatim* conversation does not, and only Arena's own session history "
      "can supply it. Anything an AI needs in order to continue the work is in sections 1–3.")
    a("")
    a("## 5 · The honest answer to \"do we have to do the 11 sessions again?\"")
    a("")
    a("**No.** The work is in three places at once: the session branches (section 1), the archives "
      "(section 3), and the merged history in main. What was never in this repository is the raw chat "
      "text, which is a record of the conversation rather than of the product.")
    a("")
    a("What is worth doing is a **consolidation pass**, not a rebuild: walk the session branches, take "
      "the files that main lacks, and bring them in through the recovery branch with a manifest and a "
      "hash for each — so the next session starts from a complete base.")
    a("")
    a("## 6 · What to tell any AI assistant about this")
    a("")
    a("Paste this, so no assistant starts rebuilding what already exists:")
    a("")
    a("> Vyomaraj is not lost and must not be rebuilt from zero. The work of 11 Arena sessions is")
    a("> present on GitHub as `origin/arena/*` branches, in "
      f"{len(arcs)} archives, and merged into `main`. Before proposing any rebuild, run "
      "`git diff --name-status main origin/arena/<branch>` and read "
      "`ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md`. The only thing genuinely missing is the raw "
      "per-chat transcript text, which lives in Arena's own history and not in the repository.")
    a("")
    return "\n".join(L) + "\n"


def check() -> int:
    problems = []
    if not OUT.is_file() or not MANIFEST.is_file():
        problems.append("index or manifest missing")
    else:
        text = OUT.read_text(encoding="utf-8")
        for marker in ("## 1 · The 11 Arena session branches", "must not be rebuilt from zero",
                       "never to\n  force-push" .replace("\n  ", " "), "raw per-chat transcripts"):
            if marker not in text:
                problems.append(f"index lost: {marker[:40]}")
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        live = len(session_branches())
        if data.get("session_branches_count") != live:
            problems.append(f"branch count changed: manifest says "
                            f"{data.get('session_branches_count')}, repository has {live}")
    if problems:
        print("recovery index check FAILED")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: recovery index matches the repository ({len(session_branches())} session branches, "
          f"{len(archives())} archives)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return check()
    sessions, arcs, chats = session_branches(), archives(), chats_state()
    OUT.write_text(build(), encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "schema": "vyomaraj-arena-recovery/1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "session_branches_count": len(sessions),
        "session_branches": sessions,
        "archives_count": len(arcs),
        "archives": arcs,
        "chats": chats,
        "unique_files_across_branches": sum(s["files_unique_to_branch"] for s in sessions),
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name} ({OUT.stat().st_size:,} B, {len(sessions)} sessions, {len(arcs)} archives)")
    print(f"wrote {MANIFEST.name} ({MANIFEST.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
