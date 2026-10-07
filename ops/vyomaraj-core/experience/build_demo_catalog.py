#!/usr/bin/env python3
"""Export only the reviewed, allowlisted local content fields for the static demo."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "demo-catalog.json"


def build() -> dict[str, object]:
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    from public_landing_server import DEMO_EXPERIENCES, _demo_catalog

    return {
        "schema_version": 1,
        "status": "curated_static_content_export",
        "packs": {experience: _demo_catalog(experience)
                  for experience in sorted(DEMO_EXPERIENCES)},
    }


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the committed static export without writing")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("FAIL: demo-catalog.json is stale; rebuild and review")
            return 1
        print(f"OK: {OUTPUT.name} matches the allowlisted source packs")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
