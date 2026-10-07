#!/usr/bin/env python3
"""Vyomaraj network / architecture diagram — colour, generated from the verified stack.

One layout model, two renderers:

  * SVG  -> ARCHITECTURE_DIAGRAM_2026_10_06.svg   (crisp at any zoom, served at /reports/network-diagram)
  * PNG  -> ARCHITECTURE_DIAGRAM_2026_10_06.png   (direct-view image, rasterised with ImageMagick)

Every box comes from something checkable in this checkout: the running servers, the GitHub Pages
build, the Actions workflows, the archive ledger and the stack record. Layers that are NOT owned are
drawn dashed grey; services with nothing running behind them are drawn red. Nothing is drawn as if
it existed when it does not.

    python3 architecture_diagram.py            build both renderings
    python3 architecture_diagram.py --check    verify they exist and still state these facts
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SVG_PATH = OUT / "ARCHITECTURE_DIAGRAM_2026_10_06.svg"
PNG_PATH = OUT / "ARCHITECTURE_DIAGRAM_2026_10_06.png"
LIVE_LEDGER = OUT / "ISSUES_AND_PRS_LEDGER.json"


def current_evidence() -> dict:
    """Read timestamped external/test evidence; never infer runtime health from prose."""
    try:
        ledger = json.loads(LIVE_LEDGER.read_text(encoding="utf-8"))
        live = ledger.get("current_live_recheck_2026_10_07", {})
        dr = live.get("dr_snapshot", {})
    except (OSError, UnicodeError, json.JSONDecodeError):
        live, dr = {}, {}
    try:
        tests = json.loads((OUT / "TEST_EVIDENCE_2026_10_04.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        tests = {}
    return {"live": live, "dr": dr, "tests": tests}


W, H = 1720, 1720
MAIN_X, MAIN_W = 40, 1300          # left column: the system, band by band
PANEL_X, PANEL_W = 1372, 288       # right column: what is claimed but not running

BG = "#0a1628"
BAND = "#0f2036"
BAND_EDGE = "#1e3a5f"
GOLD = "#f59e0b"
GOLD_SOFT = "#ffe9a8"
GREY = "#94a3b8"
GREY_DIM = "#64748b"

PALETTE = {  # kind: (fill, stroke, text)
    "people": ("#0e7490", "#22d3ee", "#e6fbff"),
    "live": ("#15803d", "#4ade80", "#ecfff1"),
    "device": ("#1d4ed8", "#60a5fa", "#ecf2ff"),
    "local": ("#b45309", "#fbbf24", "#fff7e6"),
    "auto": ("#6d28d9", "#a78bfa", "#f5efff"),
    "dr": ("#4338ca", "#818cf8", "#eef1ff"),
    "future": ("#334155", "#94a3b8", "#cbd5e1"),
    "claim": ("#7f1d1d", "#f87171", "#ffeeee"),
}

shapes: list[tuple] = []
texts: list[tuple] = []


def rect(x, y, w, h, kind, r=12, dashed=False):
    fill, edge, _ = PALETTE[kind]
    shapes.append(("rect", x, y, w, h, fill, edge, r, dashed))


def box(x, y, w, h, kind, label, sub="", fs=18, subfs=13, dashed=False):
    rect(x, y, w, h, kind, dashed=dashed)
    _, _, tcol = PALETTE[kind]
    if sub:
        texts.append((x + w / 2, y + h / 2 - 3, label, fs, tcol, True, "middle"))
        texts.append((x + w / 2, y + h / 2 + 22, sub, subfs, tcol, False, "middle"))
    else:
        texts.append((x + w / 2, y + h / 2 + fs * 0.35, label, fs, tcol, True, "middle"))


def band(y, h, title, note="", wide=True):
    """Layer frame. Returns nothing; content boxes are placed inside by the caller."""
    x = MAIN_X if not wide else 40
    w = MAIN_W if not wide else W - 80
    shapes.append(("rect", x, y, w, h, BAND, BAND_EDGE, 16, False))
    texts.append((60, y + 32, title, 20, GOLD, True, "start"))
    if note:
        texts.append((60, y + 56, note, 14, GREY, False, "start"))


def cap(cx, y, text, size=13, colour=None):
    texts.append((cx, y, text, size, colour or GREY, False, "middle"))


def arrow(x, y1, y2, colour=GOLD, width=3, label="", label_x=None):
    head = 9
    shapes.append(("line", x, y1, x, y2 - head * 0.4, colour, width, 0, False))
    shapes.append(("poly", [(x - head, y2 - head), (x + head, y2 - head), (x, y2)], colour, 0, 0, False))
    if label:
        texts.append((label_x or x + 16, (y1 + y2) / 2 + 5, label, 13, colour, False, "start"))


def build_layout():
    c_main = MAIN_X + MAIN_W / 2          # 690 — centre of the system column
    flow = c_main - 300                   # 390 — the vertical flow spine, clear of most boxes

    evidence = current_evidence()
    live, dr, tests = evidence["live"], evidence["dr"], evidence["tests"]
    check_total = len(tests.get("python_suites", [])) + len(tests.get("node_checks", [])) + len(tests.get("builders", []))
    check_failures = len(tests.get("failures", []))
    check_summary = (f"{tests.get('python_tests_total', '—')} Python · "
                     f"{check_total - check_failures}/{check_total} gates · {check_failures} failures"
                     if check_total else "offline gate not recorded")
    main_sha = live.get("main", {}).get("sha", dr.get("head_sha", "unknown"))[:8]
    tree = dr.get("primary_tree", "unknown")[:12]
    dr_time = dr.get("completed_at_utc", "unknown")
    dr_time_label = dr_time[11:16] if len(dr_time) >= 16 else "unknown"
    dr_check = dr.get("check_run_id", "unknown")
    issue_state = f"{live.get('issue_6', {}).get('state', 'unknown')}/{live.get('issue_6', {}).get('priority', 'unknown')}"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    texts.append((W / 2, 58, "VYOMARAJ + JARVIS — SHARED PEER ARCHITECTURE", 38, GOLD, True, "middle"))
    texts.append((W / 2, 90, f"generated {generated} · Pages main {main_sha} · scheduled DR tree MATCH {dr_time[11:16]} UTC · {issue_state} · branch not deployed", 16, GOLD_SOFT, False, "middle"))

    # 1 ─ people -----------------------------------------------------------
    band(118, 186, "1 · PEOPLE & DEVICES", "the only entry points that exist today")
    box(60, 194, 400, 76, "people", "Owner — Android phone", "browser + mic + camera")
    box(480, 194, 380, 76, "people", "Public visitors", "read-only, no accounts")
    box(880, 194, 440, 76, "people", "Owner — laptop", "dry runs, handover, audit")
    cap(c_main, 292, "no login · no payment · no personal data held")

    # 2 ─ live delivery ----------------------------------------------------
    band(336, 238, "2 · PUBLISHED HOSTING — MAIN ONLY",
         "Pages serves main at 04b7ae60; this launch-preview branch is not deployed", wide=False)
    box(60, 410, 450, 94, "live", "GitHub Pages — MAIN",
        "vyomaraj1356.github.io/Vyomarajai · 04b7ae60", fs=21, subfs=14)
    box(530, 410, 420, 94, "local", "Feature-branch shell", "static files · pending owner review", fs=19, subfs=13)
    box(970, 410, 350, 94, "local", "APK artifact", "24,567,022 B · v2 block detected", fs=19, subfs=13)
    cap(1145, 528, "signature validity, signer and device install unverified")
    cap(c_main, 550, "11 October is a target; public deployment requires owner review, merge and a new Pages build")

    # 3 ─ browser runtime --------------------------------------------------
    band(596, 246, "3 · BROWSER RUNTIME — ON THE VISITOR'S DEVICE",
         "real and working, and the reason none of this needs a server bill", wide=False)
    box(60, 670, 300, 64, "device", "Web Speech API", "mic · device permission", fs=16, subfs=12)
    box(380, 670, 320, 64, "device", "getUserMedia · MediaRecorder", "camera · audio · Web Audio", fs=16, subfs=12)
    box(720, 670, 280, 64, "device", "Leaflet 1.9.4 + OSM", "maps at runtime", fs=16, subfs=12)
    box(1020, 670, 300, 64, "device", "Local JSON / SQLite", "state stays on device", fs=16, subfs=12)
    box(60, 752, 400, 46, "device", "On-device voice enrollment — no upload", fs=15)
    box(480, 752, 400, 46, "device", "Consent · withdraw · delete-my-voice", fs=15)
    box(900, 752, 420, 46, "device", "Identity documents stay on uidai.in", fs=15)
    cap(c_main, 822, "no template and no identity document ever leaves the device or enters this repository")

    # 4 ─ peer topology and control plane ----------------------------------
    band(870, 236, "4 · SHARED PEER TOPOLOGY — SAME CONTRACT, NO PROD PEER DAEMONS",
         "Vyomaraj/Bharath ↔ Jarvis/Laxman is the target design; the sandbox has one bounded local planner, not a peer/control plane", wide=False)
    box(60, 944, 400, 58, "local", "Sandbox preview :5310", "allowlisted assets · ephemeral plan only · no writers", fs=17, subfs=12)
    box(480, 944, 400, 58, "claim", "Gateway :4176 · STOPPED", "no authenticated control plane", fs=17, subfs=12)
    box(900, 944, 420, 58, "claim", "Studios :4181 / :4182 · STOPPED", "writer endpoints disabled", fs=17, subfs=12)
    box(60, 1014, 400, 50, "device", "Vyomaraj / Bharath", "local deterministic planning only", fs=14, subfs=12)
    box(480, 1014, 400, 50, "auto", "Shared ShriYantra policy", "least privilege · audit · owner step-up", fs=14, subfs=12)
    box(900, 1014, 420, 50, "local", "Jarvis / Laxman", "guarded harness · no live agent runtime", fs=14, subfs=12)
    cap(c_main, 1088, "local read-only monitor: peer URLs blank · not_configured · no authenticated heartbeat, quorum or failover")

    # 5 ─ automation -------------------------------------------------------
    band(1134, 168, "5 · AUTOMATION & ASSURANCE — CHECKS ARE NOT PRODUCTION",
         "main has a scheduled tracked-tree match; issue #6 target identity/access and target-only review remain open")
    box(60, 1208, 470, 78, "auto", "Offline gate", check_summary, fs=18, subfs=13)
    box(550, 1208, 380, 78, "dr", "DR verify-or-sync", f"{dr_time_label} UTC · equal tracked Git tree", fs=18, subfs=13)
    box(950, 1208, 370, 78, "claim", "Actions settings", "403 · effective target override unknown", fs=18, subfs=13)

    # 6 ─ DR ---------------------------------------------------------------
    band(1330, 152, "6 · DR — TRACKED GIT TREE MATCH; APP / RUNTIME FAILOVER UNVERIFIED",
         f"issue #6 {issue_state} · check-run {dr_check} · same tree {tree} · traffic switched NONE")
    box(60, 1404, 470, 68, "dr", "Primary ↔ secondary tree", "MATCH on main · tracked files only", fs=17, subfs=13)
    box(550, 1404, 380, 68, "claim", "Target identity/access", "Actions override unreadable · owner review pending", fs=16, subfs=12)
    box(950, 1404, 370, 68, "claim", "Not verified by this match", "deployment · runtime · RPO/RTO · failover", fs=16, subfs=12)

    # 7 ─ not owned --------------------------------------------------------
    band(1502, 168, "7 · NOT OWNED — BUY IN THIS ORDER WHEN VYOMARAJ EARNS",
         "drawn dashed because none of it is paid for or switched on")
    for i, label in enumerate(["domain", "host", "DB backup", "payments", "voice vendor",
                               "Play Console", "CDN"]):
        box(60 + i * 180, 1576, 172, 74, "future", label, "", fs=16, dashed=True)

    texts.append((W / 2, 1700, "Green = live and free    ·    Blue = runs on the visitor's device    ·    "
                               "Amber = local rehearsal only    ·    Purple = automation    ·    "
                               "Grey dashed = not owned    ·    Red = claimed, nothing running", 15, GREY, False, "middle"))

    # ── right panel: claimed only ────────────────────────────────────────
    shapes.append(("rect", PANEL_X, 336, PANEL_W, 528, PALETTE["claim"][0], PALETTE["claim"][1], 14, True))
    texts.append((PANEL_X + PANEL_W / 2, 372, "CLAIMED ONLY", 21, "#f87171", True, "middle"))
    texts.append((PANEL_X + PANEL_W / 2, 398, "nothing running behind it", 13, "#fecaca", False, "middle"))
    entries = ["PostgreSQL 5432", "Redis 6379", "FastAPI 8000", "Flask 5000", "HTTPS / HTTP listeners",
               "15 social platform APIs", "every ₹ / follower figure", "ElevenLabs · Twilio",
               "Whisper · 4K60 synthesis", "MediaPipe Face Mesh", "multi-AI \"live\" bus", "Native Android/macOS apps"]
    for i, line in enumerate(entries):
        texts.append((PANEL_X + PANEL_W / 2, 432 + i * 32, line, 15, "#fecaca", False, "middle"))
    texts.append((PANEL_X + PANEL_W / 2, 432 + 12 * 32 + 8, "all of it from README_MARKET_READY.md", 12, GREY_DIM, False, "middle"))
    texts.append((PANEL_X + PANEL_W / 2, 432 + 12 * 32 + 30, "do not quote these to a partner", 13, GOLD_SOFT, False, "middle"))

    # ── right column, panels B and C: security and scale, honestly split ──
    def panel(y, h, title, good, limits, good_head, limit_head):
        shapes.append(("rect", PANEL_X, y, PANEL_W, h, BAND, BAND_EDGE, 14, False))
        texts.append((PANEL_X + PANEL_W / 2, y + 34, title, 19, GOLD, True, "middle"))
        texts.append((PANEL_X + 16, y + 64, good_head, 13, "#86efac", True, "start"))
        yy = y + 90
        for line in good:
            texts.append((PANEL_X + 16, yy, "✓ " + line, 14, "#bbf7d0", False, "start"))
            yy += 26
        yy += 12
        texts.append((PANEL_X + 16, yy, limit_head, 13, "#fcd34d", True, "start"))
        yy += 26
        for line in limits:
            texts.append((PANEL_X + 16, yy, "· " + line, 14, "#fde68a", False, "start"))
            yy += 26

    panel(890, 400, "SECURE — TODAY vs NOT YET",
          ["HTTPS on Pages", "no PII collected or held", "no secrets in this repo",
           "voice stays on device", "report routes allowlisted"],
          ["product has no login or 2FA", "APK signing validity/device install unverified", "preview links are session-only",
           "DR verifies files, not runtime"],
          "holding now", "still open")
    panel(1316, 350, "SCALABLE — TODAY vs NOT YET",
          ["static files, CDN-backed", "no database to size or pay", "browser does the heavy work",
           "free on this repo's Pages"],
          ["no accounts or payments yet", "single-owner control plane", "no rate limits or monitoring",
           "git snapshot is not runtime DR"],
          "holds now", "limits")

    # ── the spine: how a request actually reaches the page ──────────────
    arrow(flow, 306, 332, colour="#4ade80", label="HTTPS")
    arrow(flow, 576, 592, colour="#60a5fa", label="static files only")
    arrow(flow, 844, 866, colour="#fbbf24", label="preview-only; writer services stopped")
    arrow(flow, 1108, 1130, colour="#a78bfa", label="PR checks ≠ deployment")
    arrow(flow, 1304, 1326, colour="#818cf8", label="Git-tree match ≠ runtime failover")


# ---------------------------------------------------------------- renderers
def to_svg() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="Vyomaraj network and architecture diagram" '
        f'font-family="DejaVu Sans, Segoe UI, Arial, sans-serif">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]
    for s in shapes:
        if s[0] == "rect":
            _, x, y, w, h, fill, edge, r, dashed = s
            dash = ' stroke-dasharray="9 7"' if dashed else ""
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
                         f'stroke="{edge}" stroke-width="2"{dash}/>')
        elif s[0] == "line":
            _, x1, y1, x2, y2, colour, width, _, _ = s
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}"/>')
        else:
            _, pts, colour, _, _, _ = s
            p = " ".join(f"{a},{b}" for a, b in pts)
            parts.append(f'<polygon points="{p}" fill="{colour}"/>')
    for x, y, text, size, colour, bold, anchor in texts:
        esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        weight = ' font-weight="bold"' if bold else ""
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{colour}"{weight} '
                     f'text-anchor="{anchor}">{esc}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


_width_cache: dict[tuple[str, int], int] = {}


def text_width(text: str, size: int) -> int:
    key = (text, size)
    if key not in _width_cache:
        out = subprocess.run(
            ["convert", "-font", "DejaVu-Sans", "-pointsize", str(size), f"label:{text}", "-format", "%w", "info:"],
            capture_output=True, text=True,
        )
        _width_cache[key] = int(out.stdout.strip() or 0)
    return _width_cache[key]


def to_png() -> None:
    args = ["convert", "-size", f"{W}x{H}", f"xc:{BG}"]
    draw: list[str] = []
    for s in shapes:
        if s[0] == "rect":
            _, x, y, w, h, fill, edge, r, dashed = s
            dash = " stroke-dasharray 9 7" if dashed else ""
            draw.append(f'fill {fill} stroke {edge} stroke-width 2{dash} roundrectangle {x},{y} {x + w},{y + h} {r},{r}')
        elif s[0] == "line":
            _, x1, y1, x2, y2, colour, width, _, _ = s
            draw.append(f'stroke {colour} stroke-width {width} line {x1},{y1} {x2},{y2}')
        else:
            _, pts, colour, _, _, _ = s
            draw.append(f'fill {colour} stroke {colour} polygon ' + " ".join(f"{a},{b}" for a, b in pts))
    args += ["-draw", " ".join(draw)]
    for x, y, text, size, colour, bold, anchor in texts:
        font = "DejaVu-Sans-Bold" if bold else "DejaVu-Sans"
        if anchor == "middle":
            x = x - text_width(text, size) / 2
        args += ["-font", font, "-pointsize", str(size), "-fill", colour, "-annotate", f"+{int(x)}+{int(y)}", text]
    args.append(str(PNG_PATH))
    subprocess.run(args, check=True)


def facts() -> list[str]:
    checks = []

    def expect(path: str, needle: str, label: str) -> None:
        p = ROOT / path
        ok = p.is_file() and needle in p.read_text(errors="ignore")
        checks.append(f"{'OK  ' if ok else 'FAIL'} {label}")

    expect("index.html", "The King of the Sky", "the Pages page is the product entry point")
    expect("ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md", "04b7ae60",
           "the stack record states the current Pages build and branch non-deployment")
    expect("ops/vyomaraj-core/governance/VOICE_ENROLLMENT_POLICY.json", "on_device_only_no_vendor",
           "voice enrollment policy is on-device only")
    checks.append(f"{'OK  ' if (ROOT / 'Vyomaraj-App.apk').is_file() else 'FAIL'} "
                  f"the APK is present; a v2 signing-block entry was detected, but cryptographic "
                  f"verification and device installation remain unverified")
    dr = current_evidence()["dr"]
    matched = (dr.get("status") == "MATCH" and dr.get("data_match") is True
               and dr.get("primary_tree") == dr.get("secondary_tree")
               and dr.get("traffic_switched") == "NONE")
    checks.append(f"{'OK  ' if matched else 'FAIL'} latest recorded scheduled DR annotation reports an equal tracked Git tree without traffic switch")
    tests = current_evidence()["tests"]
    gate_total = len(tests.get("python_suites", [])) + len(tests.get("node_checks", [])) + len(tests.get("builders", []))
    gate_failures = len(tests.get("failures", []))
    checks.append(f"{'OK  ' if gate_total and 0 <= gate_failures <= gate_total else 'FAIL'} diagram gate summary comes from recorded offline evidence ({tests.get('python_tests_total', 0)} Python tests; {gate_total - gate_failures}/{gate_total} gates; {gate_failures} failures)")
    return checks


def check() -> int:
    problems = []
    if not SVG_PATH.is_file() or SVG_PATH.stat().st_size < 8000:
        problems.append(f"{SVG_PATH.name} missing or too small")
    if not PNG_PATH.is_file() or PNG_PATH.stat().st_size < 100_000:
        problems.append(f"{PNG_PATH.name} missing or too small")
    if SVG_PATH.is_file():
        svg = SVG_PATH.read_text()
        # The SVG escapes "&", so markers must be chosen to survive escaping.
        for marker in ("SHARED PEER ARCHITECTURE", "GitHub Pages — MAIN", "CLAIMED ONLY",
                       "NOT OWNED", "v2 block detected", "unverified", "uidai.in", "04b7ae60",
                       "issue #6 OPEN/P0", "Sandbox preview :5310", "not_configured",
                       "TRACKED GIT TREE MATCH", "986288ee2cc4", "traffic switched NONE",
                       "RPO/RTO", "Native Android/macOS apps"):
            if marker not in svg:
                problems.append(f"svg lost marker: {marker}")
    problems += [line for line in facts() if line.startswith("FAIL")]
    if problems:
        print("architecture diagram check FAILED")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: architecture diagram matches the latest recorded tracked-tree result, "
          f"peer/preview limits and repository facts (svg {SVG_PATH.stat().st_size} B, "
          f"png {PNG_PATH.stat().st_size} B)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    build_layout()
    SVG_PATH.write_text(to_svg())
    print(f"wrote {SVG_PATH.name} ({SVG_PATH.stat().st_size} B, {len(shapes)} shapes, {len(texts)} labels)")
    if shutil.which("convert"):
        to_png()
        print(f"wrote {PNG_PATH.name} ({PNG_PATH.stat().st_size} B, {W}x{H})")
    else:
        print("ImageMagick 'convert' not found — SVG written, PNG skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
