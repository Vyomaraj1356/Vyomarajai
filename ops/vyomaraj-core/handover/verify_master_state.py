#!/usr/bin/env python3
"""Read-only runtime/configuration verification for Vyomaraj.

This tool never enables providers, publishing, monetization, failover or failback.
It reports evidence classes only and never prints secret values.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "handover" / "VYOMARAJ_MASTER_STATE.json"

REQUIRED = [
    "VYOMARAJ_MASTER_STATE.json",
]
SECRET_RE = re.compile(r"(token|secret|password|api[_-]?key|private[_-]?key)", re.I)

def safe_env_presence():
    names = [
        "OPENAI_API_KEY","ANTHROPIC_API_KEY","GEMINI_API_KEY",
        "YOUTUBE_ACCESS_TOKEN","META_ACCESS_TOKEN","X_ACCESS_TOKEN",
        "LINKEDIN_ACCESS_TOKEN","TELEGRAM_BOT_TOKEN","WHATSAPP_TOKEN",
        "DATABASE_URL","REDIS_URL","DR_SECONDARY_TOKEN"
    ]
    return {n: bool(os.getenv(n)) for n in names}

def classify_path(p: Path):
    return "PRESENT" if p.exists() else "MISSING"

def optional_http_probe(url: str):
    """Only probe an explicitly supplied URL; never invent or mutate endpoints."""
    try:
        req = Request(url, method="GET", headers={"User-Agent":"Vyomaraj-read-only-verifier/1.0"})
        with urlopen(req, timeout=5) as r:
            return {"status":"VERIFIED", "http_status":r.status}
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {"status":"UNVERIFIED", "reason":type(exc).__name__}

def main():
    if not STATE.exists():
        print(json.dumps({"ok":False,"error":"master state missing"}, indent=2))
        return 2
    state = json.loads(STATE.read_text(encoding="utf-8"))
    result = {
        "ok": True,
        "source": "read-only repository/runtime verifier",
        "master_state": classify_path(STATE),
        "source_commit": state.get("source_commit"),
        "environment_secret_presence": safe_env_presence(),
        "components": {}
    }

    for item in state["components"]:
        result["components"][item["id"]] = {
            "inventory_status": item["status"],
            "runtime_status": item["runtime_status"],
            "next_verification": item["next_verification"]
        }

    # Optional explicit endpoint probes. URL values are supplied by the operator;
    # no secret or endpoint is read from repository files.
    for name in ("VYOMARAJ_PROBE_URL", "JARVIS_PROBE_URL", "QUEUE_PROBE_URL"):
        url = os.getenv(name)
        if url:
            result["components"][name] = optional_http_probe(url)

    result["safety"] = {
        "external_calls_enabled": False,
        "automatic_publishing_enabled": False,
        "automatic_monetization_enabled": False,
        "automatic_failover_enabled": False,
        "automatic_failback_enabled": False,
        "zero_rpo_claim": False,
        "zero_rto_claim": False,
        "secrets_printed": False
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
