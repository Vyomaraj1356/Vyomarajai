#!/usr/bin/env python3
"""Deterministic Vyomaraj/Jarvis/Arena recovery importer.
Reads repository evidence and optional Arena exports; never invents chats,
never pushes, never deletes, and never executes archive members."""
from pathlib import Path
from datetime import datetime, timezone
import os,re,json,hashlib,zipfile,tarfile,shutil,argparse

REPO=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("RECOVERY_OUT_DIR",str(REPO/".arena-recovery")))
STAGE=OUT/"staged"; REPORT=OUT/"reports"
TEXT_EXT={".md",".markdown",".txt",".json",".jsonl",".csv",".log",".yaml",".yml",".xml",".html",".htm"}
KEYS=("chat","session","handover","arena","vyomaraj-all-chats","all-chats-array","git-commits-one-month")
SECRET_PATTERNS=[
 (re.compile(r"(?i)ghp_[A-Za-z0-9_-]{20,}"),"[REDACTED_GITHUB_TOKEN]"),
 (re.compile(r"(?i)github_pat_[A-Za-z0-9_-]{20,}"),"[REDACTED_GITHUB_PAT]"),
 (re.compile(r"(?i)sk-[A-Za-z0-9_-]{20,}"),"[REDACTED_API_KEY]"),
 (re.compile(r"(?i)Bearer\s+[A-Za-z0-9._-]{20,}"),"Bearer [REDACTED]"),
 (re.compile(r"(?i)(password\s*[:=]\s*)[^\s,;]+",),r"\1[REDACTED]"),
 (re.compile(r"(?i)(secret\s*[:=]\s*)[^\s,;]+",),r"\1[REDACTED]"),
]
def redact(s):
    for p,r in SECRET_PATTERNS: s=p.sub(r,s)
    return s
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
def export_dirs():
    vals=[]
    raw=os.getenv("ARENA_EXPORT_DIRS","")
    if raw: vals += [x.strip() for x in raw.split(";") if x.strip()]
    one=os.getenv("ARENA_SESSION_DIR","")
    if one: vals.append(one)
    return [Path(x).expanduser().resolve() for x in vals if Path(x).expanduser().exists()]
def files_under(root):
    if root.is_file(): yield root; return
    for p in root.rglob("*"):
        if p.is_file(): yield p
def discover():
    out=[]; seen=set(); roots=export_dirs()
    candidates=[]
    for pat in ("**/*chat*","**/*session*","**/*handover*","**/*arena*","**/*.zip","**/*.tar","**/*.tgz"):
        candidates += list(REPO.glob(pat))
    candidates += [REPO/"Vyomaraj-All-Chats-Database-One-Month.md",
                   REPO/"All-Chats-Array-From-Index.txt",
                   REPO/"Git-Commits-One-Month.txt"]
    for r in roots: candidates += list(files_under(r))
    for p in candidates:
        try: p=p.resolve()
        except Exception: continue
        if not p.is_file() or p in seen: continue
        seen.add(p)
        explicit=any(str(p).startswith(str(r)+os.sep) or p==r for r in roots)
        relevant=explicit or any(k in str(p).lower() for k in KEYS)
        if not relevant: continue
        try:
            if explicit:
                # Keep exported session names and runner/user home paths out of
                # uploaded reports. The SHA-256 remains the local correlation key.
                label="ARENA_EXPORT/item-%04d%s"%(len(out)+1,p.suffix.lower())
                scope="ARENA_EXPORT"
            else:
                try: label=p.relative_to(REPO).as_posix()
                except ValueError: label="REPOSITORY/item-%04d%s"%(len(out)+1,p.suffix.lower())
                scope="REPOSITORY"
            out.append({"source":label,"_local_path":str(p),"scope":scope,
                        "size":p.stat().st_size,"sha256":sha(p),"extension":p.suffix.lower()})
        except Exception:
            out.append({"source":"UNREADABLE/item-%04d%s"%(len(out)+1,p.suffix.lower()),
                        "scope":"UNREADABLE","error":"source could not be read"})
    return sorted(out,key=lambda x:x["source"].lower())
def safe_zip(src,dst):
    n=0
    with zipfile.ZipFile(src) as z:
        for i in z.infolist():
            t=(dst/i.filename).resolve()
            if not str(t).startswith(str(dst.resolve())+os.sep): raise RuntimeError("unsafe ZIP member")
            if i.is_dir(): continue
            t.parent.mkdir(parents=True,exist_ok=True)
            with z.open(i) as r,t.open("wb") as w: shutil.copyfileobj(r,w)
            n+=1
    return n
def safe_tar(src,dst):
    n=0
    with tarfile.open(src,"r:*") as z:
        for i in z.getmembers():
            t=(dst/i.name).resolve()
            if not str(t).startswith(str(dst.resolve())+os.sep): raise RuntimeError("unsafe TAR member")
            if not i.isfile(): continue
            t.parent.mkdir(parents=True,exist_ok=True)
            r=z.extractfile(i)
            if r:
                with r,t.open("wb") as w: shutil.copyfileobj(r,w)
                n+=1
    return n
def stage(records):
    STAGE.mkdir(parents=True,exist_ok=True); readable=[]; archives=[]
    for n,r in enumerate(records,1):
        if r.get("scope")=="UNREADABLE": continue
        s=Path(r.get("_local_path",r["source"]))
        d=STAGE/("%04d_source%s"%(n,s.suffix.lower() or ".txt"))
        try:
            if s.suffix.lower()==".zip":
                d.mkdir(parents=True,exist_ok=True); archives.append({"source":str(s),"members":safe_zip(s,d)})
            elif s.suffix.lower() in (".tar",".tgz") and tarfile.is_tarfile(s):
                d.mkdir(parents=True,exist_ok=True); archives.append({"source":str(s),"members":safe_tar(s,d)})
            elif s.suffix.lower() in TEXT_EXT and s.stat().st_size<=10*1024*1024:
                d=d.with_suffix(".txt"); d.parent.mkdir(parents=True,exist_ok=True)
                d.write_text(redact(s.read_text(encoding="utf-8",errors="replace")),encoding="utf-8")
                readable.append(str(d))
        except Exception as e:
            archives.append({"source":str(s),"error":str(e)})
    return readable,archives
def markers(text):
    # Only publish non-sensitive release/version labels; omit raw session IDs,
    # chat numbers and arbitrary strings extracted from private session text.
    return sorted(set(re.findall(r"(?i)\bV(?:15|16)\.[0-9]+(?:\.[0-9]+)?\b",text)))[:100]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--check-only",action="store_true"); ap.parse_args()
    records=discover(); readable,archives=stage(records)
    staged=[]
    for p in readable:
        t=Path(p).read_text(encoding="utf-8",errors="replace")
        staged.append({"staged":Path(p).relative_to(OUT).as_posix(),"sha256":sha(Path(p)),"markers":markers(t)})
    REPORT.mkdir(parents=True,exist_ok=True)
    manifest={
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "system":"VYOMARAJ-AI-STUDIO",
      "integration":"VYOMARAJ + JARVIS + ARENA",
      "primary":"Vyomaraj1356/Vyomarajai",
      "arena_branch":os.getenv("VYOMARAJ_ARENA","arena/01a0f634-vyomarajai"),
      "policy":"RECOVER -> RECONCILE -> IMPLEMENT -> VERIFY -> PREVIEW -> HANDOFF",
      "counts":{"discovered":len(records),"accessible":sum(r.get("scope")!="UNREADABLE" for r in records),
                "archives":len(archives),"text_sources":len(readable)},
      "sources":[{k:v for k,v in r.items() if not k.startswith("_")} for r in records],
      "staged":staged,
      "missing_rule":"UNRECOVERED — SOURCE NOT AVAILABLE; never invent unavailable Arena chats.",
      "write_rule":"read-only recovery scan; no push, merge, delete or force operations"
    }
    (REPORT/"RECOVERY_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    lines=["# VYOMARAJ / JARVIS / ARENA VERIFIED RECOVERY HANDOFF","",
           "Primary: Vyomaraj1356/Vyomarajai",
           "Arena branch: "+manifest["arena_branch"],
           "Jarvis: continuity/orchestration; Arena: coding/preview execution",
           "","## Evidence","A source is RECOVERED only when it was actually found and hashed.",
           "An old filename, PID, screenshot, ZIP or commit message is not proof of current live state.",
           "","## Counts"] + ["- %s: %s"%(k,v) for k,v in manifest["counts"].items()] + ["","## Sources"]
    for x in staged: lines.append("- SOURCE_FOUND: "+x["staged"]+" | markers: "+(", ".join(x["markers"]) or "none"))
    if not export_dirs(): lines += ["","## Important","ARENA_EXPORT_DIRS/ARENA_SESSION_DIR was not supplied. Only repository evidence was scanned.",
                                     "Private Arena sessions not exported into the runtime remain UNRECOVERED."]
    lines += ["","## Required next gates",
               "1. Expose Arena session export/database dump through ARENA_EXPORT_DIRS.",
               "2. Re-run importer and review RECOVERY_MANIFEST.json.",
               "3. Reconcile Arena changes with current PRIMARY main; do not blindly merge stale PR #1.",
               "4. Run current preview/build/tests and record current commit, URL and HTTP result.",
               "5. Verify PRIMARY and DR independently before calling the preview VERIFIED.",
               "","No force-push, no automatic DR-to-PRIMARY promotion, no deletion."]
    (REPORT/"VYOMARAJ_JARVIS_ARENA_HANDOFF.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("RECOVERY_SCAN_COMPLETE")
    print("DISCOVERED="+str(manifest["counts"]["discovered"]))
    print("ACCESSIBLE="+str(manifest["counts"]["accessible"]))
    print("MANIFEST="+str(REPORT/"RECOVERY_MANIFEST.json"))
    print("HANDOFF="+str(REPORT/"VYOMARAJ_JARVIS_ARENA_HANDOFF.md"))
    if not export_dirs(): print("WARNING=ARENA_EXPORT_DIRS_NOT_SET")
if __name__=="__main__": main()
