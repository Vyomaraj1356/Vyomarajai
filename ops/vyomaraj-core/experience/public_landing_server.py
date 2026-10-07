#!/usr/bin/env python3
"""Serve an exact allowlist of public assets and a bounded, read-only sandbox planner.

This is not an AI API, approval service, private control plane, or production host. The only
write-method route constructs an ephemeral deterministic plan in memory; it does not store,
queue, publish, notify, call providers, or expose any privileged writer.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parents[3]
EXPERIENCE_DIR = ROOT / "ops" / "vyomaraj-core" / "experience"
ROUTES = {
    "/": (ROOT / "demo.html", "text/html; charset=utf-8"),
    "/index.html": (ROOT / "index.html", "text/html; charset=utf-8"),
    "/demo.html": (ROOT / "demo.html", "text/html; charset=utf-8"),
    "/demo.css": (ROOT / "demo.css", "text/css; charset=utf-8"),
    "/demo.js": (ROOT / "demo.js", "text/javascript; charset=utf-8"),
    "/launch.css": (ROOT / "launch.css", "text/css; charset=utf-8"),
    "/launch.js": (ROOT / "launch.js", "text/javascript; charset=utf-8"),
    "/manifest.webmanifest": (ROOT / "manifest.webmanifest", "application/manifest+json; charset=utf-8"),
    "/sw.js": (ROOT / "sw.js", "text/javascript; charset=utf-8"),
    "/offline.html": (ROOT / "offline.html", "text/html; charset=utf-8"),
    "/assets/vyomaraj-icon.svg": (ROOT / "assets/vyomaraj-icon.svg", "image/svg+xml"),
    "/assets/vyomaraj-icon-192.png": (ROOT / "assets/vyomaraj-icon-192.png", "image/png"),
    "/assets/vyomaraj-icon-512.png": (ROOT / "assets/vyomaraj-icon-512.png", "image/png"),
    "/ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg": (
        ROOT / "ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg", "image/svg+xml"),
    "/ops/vyomaraj-core/handover/GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md": (
        ROOT / "ops/vyomaraj-core/handover/GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md", "text/plain; charset=utf-8"),
    "/ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md": (
        ROOT / "ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md", "text/plain; charset=utf-8"),
    "/ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md": (
        ROOT / "ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md", "text/plain; charset=utf-8"),
}
API_ROUTE = "/api/plan"
CATALOG_ROUTE = "/api/catalog"
DEMO_EXPERIENCES = {"bhakti", "liquor-bar"}
CONTENT_PACKS = {
    "bhakti": EXPERIENCE_DIR.parent / "bhakti-experience" / "content.json",
    "liquor-bar": EXPERIENCE_DIR.parent / "liquor-bar" / "content.json",
}
DEMO_REQUEST_FIELDS = {"experience", "topic_id", "recipe_id", "mode", "diet"}
TOPIC_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z")
RECIPE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_REQUEST_BYTES = 16 * 1024
MAX_RESPONSE_BYTES = 256 * 1024


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field.")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> object:
    raise ValueError("Non-finite JSON numbers are not allowed.")


def _demo_plan(request: object) -> dict:
    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object.")
    if set(request) - DEMO_REQUEST_FIELDS:
        raise ValueError("Unknown request fields; only allowlisted planner preferences are accepted.")
    experience = request.get("experience")
    if not isinstance(experience, str) or experience not in DEMO_EXPERIENCES:
        raise ValueError("Select one of the two allowlisted local demo experiences.")
    topic_id = request.get("topic_id", "overview")
    if not isinstance(topic_id, str) or not TOPIC_ID.fullmatch(topic_id):
        raise ValueError("Topic ID must be a short known-topic identifier.")
    mode = request.get("mode", "3d")
    if not isinstance(mode, str) or mode not in {"3d", "4d", "5d"}:
        raise ValueError("Select one of the allowlisted planning modes.")
    diet = request.get("diet", "all")
    if not isinstance(diet, str) or diet not in {"all", "plant-based", "vegetarian", "pescatarian"}:
        raise ValueError("Select one of the allowlisted dietary preferences.")
    recipe_id = request.get("recipe_id")
    if recipe_id is not None and (not isinstance(recipe_id, str) or not RECIPE_ID.fullmatch(recipe_id)):
        raise ValueError("Recipe ID must be a short recipe identifier.")

    experience_path = str(EXPERIENCE_DIR)
    if experience_path not in sys.path:
        sys.path.insert(0, experience_path)
    from local_planner import InvalidPlan, build_plan

    try:
        plan = build_plan({
            "experience": experience,
            "topic_id": topic_id,
            "recipe_id": recipe_id,
            "mode": mode,
            "diet": diet,
        })
    except InvalidPlan as exc:
        raise ValueError(str(exc)) from exc
    if plan.get("experience") not in DEMO_EXPERIENCES:
        raise RuntimeError("Planner returned an experience outside the demo allowlist.")
    return plan


def _demo_catalog(experience: object) -> dict[str, object]:
    if not isinstance(experience, str) or experience not in DEMO_EXPERIENCES:
        raise ValueError("Select one of the two allowlisted local content packs.")
    path = CONTENT_PACKS[experience].resolve(strict=True)
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise RuntimeError("Allowlisted content pack is unavailable.")
    data = json.loads(path.read_text(encoding="utf-8"))
    source_index = {source.get("id"): source for source in data.get("sources", [])
                    if isinstance(source, dict) and isinstance(source.get("id"), str)}
    items: list[dict[str, object]] = []

    def source_references(record: dict[str, object]) -> list[dict[str, str]]:
        source_ids = record.get("source_ids", [])
        if not isinstance(source_ids, list):
            return []
        references = []
        for source_id in source_ids:
            source = source_index.get(source_id)
            if not isinstance(source, dict):
                continue
            title = source.get("title")
            if not isinstance(title, str) or not title.strip():
                continue
            item = {"id": str(source_id), "title": title[:240]}
            url = source.get("url")
            if isinstance(url, str):
                parsed = urlsplit(url)
                if parsed.scheme in {"https", "http"} and parsed.netloc:
                    item["url"] = url[:2048]
            references.append(item)
        return references

    def add_item(record: dict[str, object], section: str, title: object, description: object,
                 metadata: list[tuple[str, object]], status: object, *,
                 ingredients: object = None, allergens: object = None, steps: object = None) -> None:
        identity = record.get("id")
        if not isinstance(identity, str) or not TOPIC_ID.fullmatch(identity):
            return
        if not isinstance(title, str) or not title.strip():
            return
        summary = description.strip()[:4000] if isinstance(description, str) else ""
        clean_metadata = [f"{label}: {value.strip()[:200]}" for label, value in metadata
                          if isinstance(value, str) and value.strip()]
        clean_ingredients = ([value[:160] for value in ingredients[:20]
                              if isinstance(value, str) and value.strip()]
                             if isinstance(ingredients, list) else [])
        clean_allergens = ([value[:80] for value in allergens[:16]
                            if isinstance(value, str) and value.strip()]
                           if isinstance(allergens, list) else [])
        clean_steps = ([value[:800] for value in steps[:20]
                        if isinstance(value, str) and value.strip()]
                       if isinstance(steps, list) else [])
        items.append({
            "id": identity,
            "section": section[:80],
            "title": title.strip()[:240],
            "description": summary,
            "metadata": clean_metadata,
            "content_status": status[:100] if isinstance(status, str) else "editorial_proposal",
            "ingredients": clean_ingredients,
            "allergens": clean_allergens,
            "steps": clean_steps,
            "source_references": source_references(record),
        })

    if experience == "bhakti":
        for record in data.get("stories", []):
            add_item(record, "Sacred stories", record.get("title"), record.get("summary"),
                     [("Tradition", record.get("category")), ("Evidence type", record.get("evidence_type"))],
                     record.get("chapter_status"))
        for record in data.get("avatars", []):
            add_item(record, "Avatar traditions", record.get("name"), record.get("note"),
                     [("Tradition", record.get("category")), ("Form", record.get("form"))],
                     record.get("record_status", "selected_overview"))
        for record in data.get("peethas", []):
            description = " ".join(value for value in
                                   (record.get("history_overview"), record.get("origin_note"))
                                   if isinstance(value, str) and value.strip())
            add_item(record, "Peetha starter profiles", record.get("name"), description,
                     [("Location", record.get("location")), ("Region", record.get("region")),
                      ("Record", record.get("record_status"))],
                     record.get("record_status"))
        tv = data.get("television", {})
        if isinstance(tv, dict) and tv.get("source_ids"):
            tv_record = dict(tv, id="mahadev-tv")
            add_item(tv_record, "Screen adaptation", tv.get("title"), tv.get("summary"),
                     [("Lane", tv.get("category")), ("Rights", "reference only; no clips or media supplied")],
                     tv.get("rights_status"))
        for record in data.get("recipes", []):
            add_item(record, "Illustrative food concepts", record.get("name"), record.get("note"),
                     [("Diet", record.get("diet")), ("Origin", record.get("origin_status"))],
                     record.get("origin_status", "illustrative"),
                     ingredients=record.get("ingredients"), allergens=record.get("allergens"),
                     steps=record.get("procedure"))
        review_gates = [
            "Stories are editorial proposals; devotional traditions and interpretations vary.",
            "The Peetha list is a source-attributed starter, not a complete atlas.",
            "Temple practices and food concepts require tradition-specific human review.",
        ]
    else:
        for record in data.get("traditions", []):
            description = " ".join(value for value in (record.get("history"), record.get("style"))
                                   if isinstance(value, str) and value.strip())
            add_item(record, "Regional traditions", record.get("name"), description,
                     [("Region", record.get("region")), ("Scope", record.get("scope"))],
                     record.get("research_status"))
        for record in data.get("snacks", []):
            description = " ".join(value for value in
                                   (record.get("pairing_style"), record.get("non_alcoholic_pairing"))
                                   if isinstance(value, str) and value.strip())
            add_item(record, "Pairing ideas", record.get("name"), description,
                     [("Region", record.get("region")), ("Diet", record.get("diet"))],
                     record.get("origin_status", "illustrative"),
                     ingredients=record.get("ingredients"), allergens=record.get("allergens"),
                     steps=record.get("procedure"))
        for record in data.get("events", []):
            event_dates = " – ".join(value for value in (record.get("start"), record.get("end"))
                                     if isinstance(value, str) and value.strip())
            add_item(record, "Recorded event listings", record.get("name"), record.get("note"),
                     [("Region", record.get("region")), ("Dates", event_dates),
                      ("Date state", record.get("date_status"))],
                     record.get("date_status"))
        review_gates = [
            "Tradition entries may be research candidates; producer, product strength and provenance are not certified.",
            "Event records can be historical; do not present a past edition as upcoming.",
            "Local legal-age and alcohol-law review is required before any alcohol-related release.",
            "Ingredients, allergens, food handling and cross-contact require human review.",
        ]
    source_count = len({reference["id"] for item in items for reference in item["source_references"]})
    return {
        "schema_version": 1,
        "status": "local_catalog_loaded",
        "experience": experience,
        "title": str(data.get("title", experience))[:240],
        "content_pack_status": str(data.get("status", "unverified"))[:120],
        "updated": str(data.get("updated", "not recorded"))[:40],
        "item_count": len(items),
        "source_reference_count": source_count,
        "items": items,
        "review_gates": review_gates,
        "provider": None,
        "ai_calls_made": False,
        "publishing_enabled": False,
        "production_deployed": False,
    }


class PublicLandingHandler(BaseHTTPRequestHandler):
    server_version = "VyomarajPublicPreview/2"
    sys_version = ""

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(10)

    def _headers(self, content_type: str, size: int, status: int = 200,
                 extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(size))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
            "connect-src 'self'; manifest-src 'self'; worker-src 'self'; object-src 'none'; "
            "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()

    def _send_json(self, status: int, data: dict[str, object], *, include_body: bool = True,
                   allow: str | None = None) -> None:
        body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        extra = {"Allow": allow} if allow else None
        self._headers("application/json; charset=utf-8", len(body), status, extra)
        if include_body:
            self.wfile.write(body)

    def _serve_catalog(self) -> None:
        parsed = urlsplit(self.path)
        if len(parsed.query) > 256:
            self._send_json(400, {"error": "Catalog query is too long."})
            return
        try:
            fields = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True,
                               max_num_fields=1)
        except ValueError:
            self._send_json(400, {"error": "Supply exactly one experience query parameter."})
            return
        if len(fields) != 1 or fields[0][0] != "experience":
            self._send_json(400, {"error": "Supply only the experience query parameter."})
            return
        try:
            catalog = _demo_catalog(fields[0][1])
            body = json.dumps(catalog, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if len(body) > MAX_RESPONSE_BYTES:
                self._send_json(500, {"error": "Catalog output exceeded the demo response limit."})
                return
            self._headers("application/json; charset=utf-8", len(body))
            self.wfile.write(body)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception:
            self._send_json(500, {"error": "Local content catalog is temporarily unavailable."})

    def _serve(self, include_body: bool) -> None:
        path = urlsplit(self.path).path
        if path == API_ROUTE:
            self._send_json(405, {"error": "Use POST to build a bounded local plan."},
                            include_body=include_body, allow="POST")
            return
        if path == CATALOG_ROUTE:
            if include_body:
                self._serve_catalog()
            else:
                self._send_json(405, {"error": "Use GET to read the local content catalog."},
                                include_body=False, allow="GET")
            return
        if path == "/landing.html":
            self.send_response(302)
            self.send_header("Location", "./index.html")
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        entry = ROUTES.get(path)
        if entry is None or entry[0] is None:
            body = b"Not found\n"
            self._headers("text/plain; charset=utf-8", len(body), 404)
            if include_body:
                self.wfile.write(body)
            return
        file_path, content_type = entry
        try:
            resolved = file_path.resolve(strict=True)
            if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                raise OSError("Not an approved public file")
            size = resolved.stat().st_size
            if size > MAX_FILE_BYTES:
                raise OSError("Approved public file exceeds size limit")
            body = resolved.read_bytes() if include_body else b""
        except OSError:
            body = b"Preview asset unavailable\n"
            self._headers("text/plain; charset=utf-8", len(body), 503)
            if include_body:
                self.wfile.write(body)
            return
        self._headers(content_type, size)
        if include_body:
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._serve(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._serve(include_body=False)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlsplit(self.path).path
        if path == CATALOG_ROUTE:
            self._send_json(405, {"error": "The content catalog is read-only; use GET."}, allow="GET")
            return
        if path != API_ROUTE:
            self._send_json(404, {"error": "Not found."})
            return
        if urlsplit(self.path).query:
            self._send_json(400, {"error": "Query parameters are not accepted."})
            return
        if self.headers.get("Transfer-Encoding"):
            self._send_json(400, {"error": "Transfer-encoded requests are not accepted."})
            return
        if self.headers.get("Content-Encoding", "identity").casefold() != "identity":
            self._send_json(415, {"error": "Compressed request bodies are not accepted."})
            return
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().casefold()
        if content_type != "application/json":
            self._send_json(415, {"error": "Content-Type must be application/json."})
            return
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            self._send_json(411, {"error": "Content-Length is required."})
            return
        try:
            length = int(raw_length, 10)
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length."})
            return
        if length < 0:
            self._send_json(400, {"error": "Invalid Content-Length."})
            return
        if length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "Request body exceeds the demo limit."})
            return
        try:
            body = self.rfile.read(length)
            if len(body) != length:
                self._send_json(400, {"error": "Incomplete request body."})
                return
            request = json.loads(body.decode("utf-8"), object_pairs_hook=_unique_object,
                                 parse_constant=_reject_json_constant)
            plan = _demo_plan(request)
            response = json.dumps(plan, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if len(response) > MAX_RESPONSE_BYTES:
                self._send_json(500, {"error": "Planner output exceeded the demo response limit."})
                return
            self._headers("application/json; charset=utf-8", len(response))
            self.wfile.write(response)
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
            self._send_json(400, {"error": str(exc) or "Invalid JSON request."})
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            # Do not reflect request data or filesystem paths, and do not emit a traceback to clients.
            self._send_json(500, {"error": "Local planner is temporarily unavailable."})

    def do_OPTIONS(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlsplit(self.path).path
        if path == API_ROUTE:
            self._send_json(405, {"error": "Cross-origin preflight and OPTIONS are not supported."}, allow="POST")
        elif path == CATALOG_ROUTE:
            self._send_json(405, {"error": "Cross-origin preflight and OPTIONS are not supported."}, allow="GET")
        else:
            self._send_json(404, {"error": "Not found."})

    def handle_expect_100(self) -> bool:
        self._send_json(417, {"error": "Expect headers are not supported by the sandbox API."})
        return False

    def log_message(self, _format: str, *args) -> None:
        # No query strings, IP addresses, request bodies, or browser identifiers are logged.
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5310)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    server = ThreadingHTTPServer((args.host, args.port), PublicLandingHandler)
    print(
        f"Vyomaraj public preview on {args.host}:{args.port}; "
        f"serving {len(ROUTES)} allowlisted public assets, {CATALOG_ROUTE} (curated local content), "
        f"and {API_ROUTE} (bounded planner); no privileged APIs or private files",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
