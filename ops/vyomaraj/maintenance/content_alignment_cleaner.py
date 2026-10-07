#!/usr/bin/env python3
"""Deterministic Vyomaraj/Jarvis content-alignment maintenance scanner."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
REG=ROOT/"ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
IDX=ROOT/"ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json"
OWN=ROOT/"ops/vyomaraj-core/agents/CONTENT_OWNERSHIP_CURRENT.json"
OUT=ROOT/"reports"/"maintenance"
OUT.mkdir(parents=True,exist_ok=True)
def norm(v): return re.sub(r"[^a-z0-9]+"," ",str(v or "").lower()).strip()
def fp(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def scan():
    reg,idx,own=load(REG),load(IDX),load(OWN); agents=reg["agents"]
    ids=[a["id"] for a in agents]
    dup_ids=sorted({x for x in ids if ids.count(x)>1})
    valid_refs={a["id"] for a in agents}|{a["category_id"] for a in agents}
    invalid_parent=[a["id"] for a in agents if a["parent_id"] not in valid_refs]
    unnamed=[a["id"] for a in agents if a.get("counted") and not a.get("name")]
    merged=[{"id":a["id"],"target":a["merge_target_id"],"target_exists":a["merge_target_id"] in {x["id"] for x in agents}} for a in agents if a.get("merge_target_id")]
    title_groups={}
    for r in idx.get("records",[]): title_groups.setdefault((r.get("owner_category"),norm(r.get("title"))),[]).append(r)
    exact=[]; possible=[]
    for key,records in title_groups.items():
        if len(records)<2: continue
        fps={fp({"kind":x.get("kind"),"source_refs":x.get("source_refs"),"title":x.get("title"),"owner_category":x.get("owner_category")}) for x in records}
        item={"key":key,"ids":[x.get("id") for x in records],"count":len(records)}
        (exact if len(fps)==1 else possible).append(item)
    indexed_ids={r.get("id") for r in idx.get("records",[])}
    orphan=[r.get("id") for r in own.get("education_topics",[]) if r.get("id") not in indexed_ids]
    return {"generated_at":datetime.now(timezone.utc).isoformat(),
      "registry_sha256":hashlib.sha256(REG.read_bytes()).hexdigest(),
      "content_index_sha256":hashlib.sha256(IDX.read_bytes()).hexdigest(),
      "counts":{"categories":len({a["category_id"] for a in agents}),"counted_agents":sum(1 for a in agents if a.get("counted")),"named_counted_agents":sum(1 for a in agents if a.get("counted") and a.get("name")),"unnamed_counted_agents":len(unnamed),"content_records":len(idx.get("records",[]))},
      "findings":{"duplicate_agent_ids":dup_ids,"invalid_parent_ids":invalid_parent,"legacy_merged_records":merged,"exact_content_duplicates":exact,"possible_duplicate_groups":possible,"orphan_education_ownership_records":orphan,"unnamed_counted_ids":unnamed},
      "rules":{"exact_duplicate":"merge with complete provenance + tombstone/alias; no silent deletion","possible_duplicate":"proposal only","conflict":"stop and escalate"}}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("mode",choices=["scan","weekly","monthly","merge-plan"]); args=ap.parse_args()
    result=scan(); result["mode"]=args.mode; result["depth"]="deep" if args.mode=="monthly" else "standard"
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); path=OUT/f"content-alignment-{args.mode}-{stamp}.json"
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"; path.write_text(text,encoding="utf-8"); (OUT/"LATEST_CONTENT_ALIGNMENT.json").write_text(text,encoding="utf-8")
    print(text); return 0 if not result["findings"]["duplicate_agent_ids"] and not result["findings"]["invalid_parent_ids"] else 2
if __name__=="__main__": raise SystemExit(main())
