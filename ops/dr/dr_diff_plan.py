#!/usr/bin/env python3
"""Read-only, path-level Primary/DR tree diff plan.

Uses GET-only GitHub API calls. Never creates blobs, trees, commits, refs, or writes
to either repository. Output contains paths, modes, and Git blob SHAs only (no file
contents or credentials). A MISMATCH is a successful plan result, not a sync.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from dr_sync import APIError, CheckError, GitHub, PRIMARY, snapshot, source_entries, validate_target


def compare_entries(primary_entries, secondary_entries, primary_snapshot, secondary_snapshot):
    p = {e["path"]: e for e in primary_entries}
    d = {e["path"]: e for e in secondary_entries}
    primary_only = sorted(set(p) - set(d))
    secondary_only = sorted(set(d) - set(p))
    common = sorted(set(p) & set(d))
    changed = [path for path in common
               if p[path].get("sha") != d[path].get("sha")
               or p[path].get("mode") != d[path].get("mode")]
    unchanged = len(common) - len(changed)
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "GET_only",
        "writes_attempted": False,
        "traffic_switched": False,
        "primary_repository": PRIMARY,
        "secondary_repository": os.environ.get("DR_REPO", ""),
        "branch": "main",
        "primary": primary_snapshot,
        "secondary": secondary_snapshot,
        "status": "MATCH" if primary_snapshot["tree"] == secondary_snapshot["tree"] else "MISMATCH",
        "counts": {
            "primary_only": len(primary_only),
            "secondary_only": len(secondary_only),
            "changed_common": len(changed),
            "unchanged_common": unchanged,
            "primary_files": len(p),
            "secondary_files": len(d),
        },
        "primary_only": [{"path": x, "mode": p[x]["mode"], "sha": p[x]["sha"]} for x in primary_only],
        "secondary_only": [{"path": x, "mode": d[x]["mode"], "sha": d[x]["sha"]} for x in secondary_only],
        "changed_common": [{
            "path": x,
            "primary_mode": p[x]["mode"],
            "secondary_mode": d[x]["mode"],
            "primary_sha": p[x]["sha"],
            "secondary_sha": d[x]["sha"],
        } for x in changed],
        "note": "Path-level comparison only; no file content was fetched or written. Review target-only and changed-common paths before any exact-snapshot sync.",
    }


def plan(target, primary=None, secondary=None, environ=None):
    env = os.environ if environ is None else environ
    target = validate_target(target)
    primary = primary or GitHub(env.get("PRIMARY_TOKEN"))
    secondary = secondary or GitHub(env.get("DR_TOKEN"))
    for client, repo in ((primary, PRIMARY), (secondary, target)):
        info = client.request("GET", f"repos/{repo}")
        if info.get("full_name", "").lower() != repo.lower():
            raise CheckError("Repository identity mismatch or rename; confirmation required")
        if info.get("archived") or info.get("disabled"):
            raise CheckError("Repository is archived/disabled")
    src, dst = snapshot(primary, PRIMARY), snapshot(secondary, target)
    src_tree = primary.request("GET", f"repos/{PRIMARY}/git/trees/{src['tree']}?recursive=1")
    dst_tree = secondary.request("GET", f"repos/{target}/git/trees/{dst['tree']}?recursive=1")
    source = source_entries(src_tree)
    destination = source_entries(dst_tree, allow_empty=True)
    result = compare_entries(source, destination, src, dst)
    result["secondary_repository"] = target
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=os.environ.get("DR_REPO", ""))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = plan(args.target)
        code = 0
    except (CheckError, ValueError, KeyError, TypeError):
        # Never log raw exceptions or provider response bodies in diagnostic evidence.
        result = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "mode": "GET_only",
            "writes_attempted": False,
            "traffic_switched": False,
            "status": "BLOCKED",
            "reason": "read_only_plan_failed; inspect sanitized workflow logs",
        }
        code = 2
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    raise SystemExit(code)


if __name__ == "__main__":
    main()
