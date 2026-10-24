#!/usr/bin/env python3
"""Read-only repository inventory; reports paths and counts, never file contents."""
import argparse, json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone

SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
EXPECTED = {
    "README": "README.md",
    "System inventory": "ops/vyomaraj-core/handover/FULL_SYSTEM_INVENTORY_2026_10_03.md",
    "Architecture": "docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md",
    "LLM harness": "ops/jarvis/llm_harness.py",
    "Prompt registry": "config/ai/PROMPT_REGISTRY_V1.json",
    "Knowledge policy": "config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json",
    "DR policy": "ops/dr/DR_POLICY.json",
    "DR package parity": "ops/dr/PACKAGE_PARITY.json",
    "Peer heartbeat report": "ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md",
    "Runbook": "ops/vyomaraj-core/handover/VYOMARAJ_RUNBOOK_2026_10_06.md",
    "Runner acceptance workflow": ".github/workflows/secure-local-runner-acceptance.yml",
    "Master inventory": "docs/engineering/VYOMARAJ_JARVIS_MASTER_SYSTEM_INVENTORY_2026-10-24.md",
}

def git(root, *args):
    try:
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True, timeout=3).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    root = Path(a.root).resolve()
    if not root.is_dir(): p.error("root must be a directory")
    files, ext, workflows, dirs = 0, {}, [], set()
    for base, children, names in os.walk(root):
        children[:] = [x for x in children if x not in SKIP]
        for name in names:
            f = Path(base) / name
            if f.is_symlink(): continue
            rel = f.relative_to(root).as_posix()
            files += 1
            suffix = f.suffix.lower() or "[none]"
            ext[suffix] = ext.get(suffix, 0) + 1
            dirs.add(rel.split("/")[0])
            if rel.startswith(".github/workflows/") and suffix in {".yml", ".yaml"}:
                workflows.append(rel)
    result = {
        "report": "READ_ONLY_REPOSITORY_INVENTORY",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root), "branch": git(root, "branch", "--show-current"),
        "commit": git(root, "rev-parse", "HEAD"),
        "worktree": "CLEAN" if git(root, "status", "--porcelain") == "" else "DIRTY_OR_UNKNOWN",
        "files_counted": files, "extension_counts": dict(sorted(ext.items())),
        "top_level_directories": sorted(dirs), "workflow_paths": sorted(workflows),
        "expected_artifacts": {k: {"path": v, "present": (root / v).is_file()} for k, v in EXPECTED.items()},
        "safety": {"reads_file_contents": False, "network_calls": False, "installs_or_writes": False, "contacts_dr": False},
        "limitation": "File presence does not prove a tool is installed, configured, deployed, connected, authorized or healthy.",
    }
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print("# Read-only repository inventory")
        print("\nGenerated UTC:", result["generated_at_utc"])
        print("Branch:", result["branch"] or "UNKNOWN", "| Commit:", result["commit"] or "UNKNOWN")
        print("Worktree:", result["worktree"], "| Files counted:", files)
        print("\n## Expected artifacts")
        for k, v in result["expected_artifacts"].items(): print(("- [x] " if v["present"] else "- [ ] ") + k + ": `" + v["path"] + "`")
        print("\n## Workflows")
        for item in sorted(workflows): print("- `" + item + "`")
        print("\n## Extensions")
        for k, v in sorted(ext.items()): print(f"- {k}: {v}")
        print("\nSafety: no file contents read; no network calls; no installations or writes; no DR access.")
        print("Presence is not proof of runtime readiness.")

if __name__ == "__main__": main()