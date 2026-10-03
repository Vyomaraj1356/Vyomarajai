"""Rebuild the public all-experiences index from four allowlisted editorial packs only."""
import json
from pathlib import Path
CORE = Path(__file__).resolve().parent.parent

def build():
    packs = {key: json.loads((CORE / directory / 'content.json').read_text()) for key, directory in
             [('film','film-experience'),('music','music-experience'),('bhakti','bhakti-experience'),('pairings','liquor-bar')]}
    lines = ['# Vyomaraj — All Experience Contents', '', '**Updated 3 October 2026 · Review-branch local studio**', '',
             'This index lists all content records in the four new editorial extensions. It is not all 421 canonical product titles, all historical archives or a complete world catalogue. Detailed metadata, source review basis and recipes remain in each allowlisted content.json and experience viewer.', '',
             '| Experience | Viewer | Detailed report |', '|---|---|---|',
             '| Frame & Stage | /film/ | /reports/film |', '| Memory & Melody | /music/ | /reports/music |',
             '| Bhakti-Shakti | /bhakti/ | /reports/bhakti |', '| Roots & Pairings | /pairings/ | liquor-bar/README.md |', '',
             'Repeatable metadata discovery and review: /research/. Integrated connection, configuration and DR follow-up report: /reports/research. Discovery queue records are separate from the four editorial packs and are not new canonical products. Public API runtime checks are blocked; SearXNG/Ollama and the opt-in daily schedule are not active.', '',
             'Full historical system inventory: /reports/. Music and Movie slot bindings are proposals; canonical names remain UNKNOWN. BHAKTI child mapping remains UNMAPPED. The 13 / 133 / 421 registry totals and 32-file historical catalog are unchanged.', '',
             'Local capabilities: discovery, food rotation/steps/preferences, deterministic Vyomaraj/Jarvis plans, authorized-file audio/video playback, local trim/reorder/sequence preview and edit-decision export. No commercial media hosting, external AI renderer, automatic publication, production release or verified DR is claimed.']
    for key in ('film','music'):
        data=packs[key]; lines += ['', '## '+data['title'], '', '| Existing slot | Proposed function |', '|---|---|']
        lines += [f"| {a['slot']} | {a['proposed_label']} — canonical name UNKNOWN |" for a in data['agents']]
        lines += ['', '| ID | Title | Format | Language / route | Summary |', '|---|---|---|---|---|']
        lines += [f"| {i['id']} | {i['title']} | {i['kind']} | {i['language']} | {i['summary']} |" for i in data['items']]
        if key=='film':
            lines += ['', '### All original planning formats', '']+[f"- {f['title']}: default budget {f['default_seconds']} seconds; an outline, not finished media." for f in data['formats']]
            lines += ['', 'Original seeds: The Shared Shelf; The Repair Table. Each has Marathi, Hindi and English short dialogue samples. Plans are not complete screenplays or theatre texts.']
        else:
            c=data['chart_snapshot'];lines += ['', '### '+c['title'], '', 'Period '+c['period']+'; published '+c['published']+'; dated annual snapshot, not live.', '']+[f"- {e['rank']}. {e['title']} — {e['artist']}" for e in c['entries']]
    d=packs['bhakti'];lines+=['','## Bhakti-Shakti','']
    for key,title in [('stories','Proposed story chapters'),('avatars','Selected avatar overview'),('peethas','Starter Peetha/regional profiles'),('recipes','Prasad-style food concepts')]:
        lines+=['','### '+title,'']
        for i in d[key]:lines.append('- '+i.get('title',i.get('name',i['id'])))
    lines+=['','Television-context card: '+d['television']['title']+' — catalogue context only, no episode import.']
    d=packs['pairings'];lines+=['','## Roots & Pairings','', 'Existing sibling agents ENT-LIQUOR-S1 / ENT-BAR-S1; adult/legal and food-safety constraints remain.']
    for key,title in [('traditions','Regional/world tradition entries'),('snacks','Food concepts'),('events','Dated events and candidates')]:
        lines+=['','### '+title,'']
        for i in d[key]:lines.append('- '+i.get('title',i.get('name',i.get('id','UNMAPPED'))))
    for key in ('liquor','bar'):
        lines+=['','### Proposed '+key+' chapters','']
        for i in d['chapter_mapping'][key]:lines.append('- '+(i if isinstance(i,str) else i.get('title',i.get('name','UNMAPPED'))))
    lines+=['','## Complete extension source indexes','', 'Per-record attribution is retained in the corresponding pack; research is not necessarily full-text verification.']
    for key,data in packs.items():
        lines+=['','### '+data['title'],'']
        lines += ['- '+s['title']+' — '+s.get('citation',s['url']) for s in data['sources']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    (CORE/'handover/EXPERIENCE_CONTENTS_2026_10_03.md').write_text(build())
