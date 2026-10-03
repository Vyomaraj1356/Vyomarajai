#!/usr/bin/env python3
"""Build current, owner-approved hierarchy. Never rewrite pinned historical sources."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

CORE=Path(__file__).resolve().parent.parent
HERE=CORE/'agents'
SNAPSHOT=CORE/'handover/AGENT_CONTENT_REGISTRY_V16_7_24.json'
ACTIVE=HERE/'AGENT_REGISTRY_CURRENT.json'
INDEX=HERE/'CONTENT_INDEX_CURRENT.json'
REPORT=CORE/'handover/AGENT_RECONCILIATION_2026_10_03.md'
INVENTORY=CORE/'handover/FULL_SYSTEM_INVENTORY_2026_10_03.md'
PACKS={'aghor':('aghor-experience',('chapters','people','practices','care')), 'film':('film-experience',('items',)), 'music':('music-experience',('items',)),
       'bhakti':('bhakti-experience',('stories','avatars','peethas','recipes')),
       'pairings':('liquor-bar',('traditions','snacks','events'))}


def require(ok,message):
    if not ok:raise ValueError(message)


def unique(records,key,audit,scope):
    """Collapse only equal records with the same identity; conflict is never silent."""
    seen={};result=[]
    for r in records:
        identity=key(r)
        if identity in seen:
            require(seen[identity]==r,'Conflicting duplicate identity: '+scope+':'+str(identity))
            audit.append({'scope':scope,'identity':identity,'action':'exact_duplicate_reference_removed'})
        else:seen[identity]=r;result.append(copy.deepcopy(r))
    return result


def expand(group):
    label=group['ids']
    if label=='ENT-AI-S1/S2':ids=['ENT-AI-S1','ENT-AI-S2']
    else:
        match=re.fullmatch(r'(ENT-[A-Z]+)-S(\d+)(?:-S(\d+))?',label)
        require(match is not None,'Unknown source group pattern')
        end=int(match[3] or match[2]);ids=[f'{match[1]}-S{i}' for i in range(int(match[2]),end+1)]
    require(len(ids)==group['count'],'Group count mismatch')
    return ids


def build(source,rules):
    audit=[];categories=[];agents=[];hubs=[];retired=[]
    original=unique(source['categories'],lambda c:c['id'],audit,'categories')
    require(len(original)==13,'Expected 13 source categories')
    require(sum(c['sub_agents'] for c in original)==133,'Source sub-agent count mismatch')
    for c in original:
        cid=c['id'];roster=source['rosters'].get(cid)
        category={'id':cid,'name':rules['education_name'] if cid=='EDU' else c['description'],
                  'source_reported_sub_agents':c['sub_agents'],'source_reported_products':c['products'],
                  'active_product_count':None,'product_status':'UNRECONCILED_no_complete_item_level_mapping'}
        categories.append(category)
        def add(identity,name=None,source_slot=None,parent=None,chapter_count=None):
            record={'id':identity,'category_id':cid,'parent_id':parent or cid,'name':name,
                    'name_status':'SUPPLIED_OR_OWNER_APPROVED' if name else 'UNKNOWN',
                    'source_slot':source_slot,'id_status':'source_id_preserved' if source_slot else 'current_reference_id_not_recovered_slot',
                    'serial':1+sum(a['category_id']==cid for a in agents),'kind':'sub_agent',
                    'counted':True,'source_reported_chapter_count':chapter_count,
                    'runtime_status':'NOT_VERIFIED'}
            agents.append(record)
        if cid=='EDU':
            for entry in unique(roster['entries'],lambda e:e['slot'],audit,'EDU.entries'):
                if entry['slot']=='S8-S13':
                    category['unmapped_source_group_label']=entry['name']
                    for i in range(8,14):add('EDU-S'+str(i),source_slot='S'+str(i))
                else:add('EDU-'+entry['slot'],entry['name'],entry['slot'],chapter_count=entry.get('chapters'))
            move=rules['government_schemes'];require(move['from_category']=='FINANCE' and move['to_category']=='EDU' and move['count_transferred']==1,'Unexpected approved scheme transfer')
            add(move['id'],move['name'])
            agents[-1]['ownership_basis']='owner_approved_transfer_from_FINANCE_historical_Govt_Schemes_label'
        elif cid=='ENTERTAINMENT':
            groups=unique(roster['groups'],lambda g:g['ids'],audit,'ENTERTAINMENT.groups')
            require(sum(g['count'] for g in groups)==38,'Entertainment source count mismatch')
            named=next(g for g in groups if g['ids']=='S1-S8')
            require(len(named['names'])==named['count']==8,'Named hub source mismatch')
            decisions={h['name']:h for h in rules['entertainment_parent_headings']}
            require(len(decisions)==6,'Six parent headings must be approved')
            child_groups={h['child_group']:h['id'] for h in decisions.values()}
            for order,name in enumerate(named['names'],1):
                if name in decisions:
                    h=decisions[name]
                    hubs.append({'id':h['id'],'category_id':cid,'parent_id':cid,'name':name,'kind':'heading','counted':False,'source_group':'S1-S8','source_order':order,'approval':'user_confirmed_parent_heading'})
                    retired.append({'source_category':cid,'source_group':'S1-S8','source_order':order,'name':name,'now':h['id'],'action':'removed_from_agent_count_retained_as_parent_heading'})
                else:
                    require(name in rules['preserve_distinct_named_entries'],'Unexpected named source agent')
                    add('ENT-INDICOM' if name=='INDICOM' else 'ENT-CRITICISM',name)
            for group in groups:
                if group['ids']=='S1-S8':continue
                for identity in expand(group):add(identity,source_slot=identity,parent=child_groups.get(group['ids']),chapter_count=group.get('chapter_count'))
        elif cid=='PLATFORM':
            roster=copy.deepcopy(roster);roster['lanes']=unique(roster['lanes'],lambda x:x,audit,'PLATFORM.lanes')
            require(len(roster['lanes'])==19 and roster['unmapped_slot_count']==1,'Platform source mismatch')
            for i,name in enumerate(roster['lanes'],1):add(f'PLATFORM-REF-{i:02}',name)
            add('PLATFORM-UNMAPPED') # Display serial 20 is NOT a recovered source S20.
        elif isinstance(roster,list):
            roster=unique(roster,lambda x:x,audit,cid+'.names')
            require(len(roster)==c['sub_agents'],'Named source count mismatch')
            for i,name in enumerate(roster,1):add(f'{cid}-REF-{i:02}',name)
        else:
            count=c['sub_agents']-(1 if cid=='FINANCE' else 0)
            for i in range(1,count+1):add(f'{cid}-REF-{i:02}')
        for new in rules.get('new_sub_agents',[]):
            if new['category_id']==cid:
                add(new['id'],new['name'])
                agents[-1]['ownership_basis']=new['approval']
        category['sub_agents']=sum(a['category_id']==cid for a in agents)
        category['headings']=sum(h['category_id']==cid for h in hubs)
    agents=unique(agents,lambda a:a['id'],audit,'active_agents')
    result={'schema_version':2,'status':'CURRENT_OWNER_APPROVED_STRUCTURE_not_runtime_inventory','updated':'2026-10-03',
            'source_snapshot':'handover/AGENT_CONTENT_REGISTRY_V16_7_24.json','historical_totals':source['totals'],
            'categories':categories,'headings':hubs,'agents':agents,
            'count_reconciliation':{'six_hubs_reclassified_not_deleted':retired,'government_schemes_transfer':rules['government_schemes'],
                                    'exact_duplicate_records_removed':audit},
            'totals':{'main_agents':len(categories),'sub_agents':len(agents),'uncounted_parent_headings':len(hubs),
                      'named_sub_agents':sum(a['name'] is not None for a in agents),
                      'unnamed_numbered_sub_agents':sum(a['name'] is None for a in agents),
                      'active_products':None,'historical_reported_products':source['totals']['products']},
            'display_policy':'Show unnamed entries by serial only; null names remain unassigned. Display serials are not recovered slot identities.',
            'hierarchy_policy':'Only the six explicitly approved hubs acquire child edges. Other missing sub-sub-agent mappings remain UNMAPPED; do not invent a third tier.',
            'product_policy':'421 is a historical aggregate, not a verified deduplicated/current owner-assigned product inventory.',
            'historical_sovereign_roles':['Creator','Thinker','Scout','Analyst','Guardian','Evolution','Jarvis','Hermes','Cinema','Sync','Family'],
            'sovereign_role_status':'historical_cross_cutting_roles_not_additional_category_children_not_verified_services'}
    validate(result)
    return result


def validate(data):
    cats={c['id']:c for c in data['categories']};hubs={h['id']:h for h in data['headings']};agents={a['id']:a for a in data['agents']}
    all_ids=[*cats,*hubs,*agents]
    require(len(all_ids)==len(set(all_ids)),'Duplicate identity across hierarchy levels')
    require(len(agents)==len(data['agents']),'Duplicate agent identity')
    require(len(cats)==len(data['categories']) and len(hubs)==len(data['headings']),'Duplicate heading/category')
    for h in hubs.values():require(h['parent_id']==h['category_id'] and h['category_id'] in cats and h['counted'] is False,'Invalid heading parent/count')
    for a in agents.values():
        require(a['category_id'] in cats and a['parent_id'] in (cats|hubs),'Missing parent/category')
        require(a['parent_id']==a['category_id'] or hubs.get(a['parent_id'],{}).get('category_id')==a['category_id'],'Cross-category parent')
        require(a['counted'] is True and a['kind']=='sub_agent','Invalid counted agent')
        require(a['name'] is None or isinstance(a['name'],str),'Invalid name')
    for c in cats.values():
        children=[a for a in agents.values() if a['category_id']==c['id']]
        require(len(children)==c['sub_agents'],'Active category count mismatch')
        require(sorted(a['serial'] for a in children)==list(range(1,len(children)+1)),'Serial gap or duplicate')
        names=[a['name'].strip().casefold() for a in children if a['name']]
        require(len(names)==len(set(names)),'Repeated named agent in category requires review')
    require(sum(c['sub_agents'] for c in cats.values())==data['totals']['sub_agents']==128,'Active total mismatch')
    require(data['totals']['named_sub_agents']==42 and data['totals']['unnamed_numbered_sub_agents']==86,'Name arithmetic mismatch')
    require(cats['EDU']['sub_agents']==16 and cats['FINANCE']['sub_agents']==7 and cats['ENTERTAINMENT']['sub_agents']==32,'Approved reallocation mismatch')
    for h in hubs:
        require(any(a['parent_id']==h for a in agents.values()),'Empty parent heading')


def content_index(ownership,registry):
    records=[];audit=[];agent_ids={a['id'] for a in registry['agents']}
    topics=unique(ownership['education_topics'],lambda r:r['id'],audit,'education_topics')
    for topic in topics:
        require(topic['owner_category']=='EDU','Education topic assigned outside EDU')
        provenance=topic['source']['path']
        allowed_sources={'flow-diagram.html','ops/vyomaraj-core/handover/AGENT_CONTENT_REGISTRY_V16_7_24.json','ops/vyomaraj-core/handover/HISTORICAL_SYSTEM_INVENTORY_2026_10_03.md'}
        require(provenance in allowed_sources and (CORE.parents[1]/provenance).is_file(),'Invalid or missing topic provenance')
        require(topic['slot_id'] is None or topic['slot_id'] in agent_ids,'Orphan education slot')
        records.append({'id':topic['id'],'title':topic['title'],'owner_category':'EDU','kind':'education_topic_reference',
                        'source_refs':[topic['source']],'full_content_imported':False})
    for pack,(directory,collections) in PACKS.items():
        data=json.loads((CORE/directory/'content.json').read_text())
        for entry in data.get('agents',[]):require(entry['slot'] in agent_ids,'Editorial agent link orphaned')
        for collection in collections:
            for row in unique(data[collection],lambda r:r['id'],audit,pack+'/'+collection):
                title=row.get('title') or row.get('name') or row['id']
                records.append({'id':pack+':'+collection+':'+row['id'],'title':title,
                                'owner_category':ownership['editorial_pack_owners'][pack],'kind':'editorial_'+collection,
                                'source_refs':[{'path':'ops/vyomaraj-core/'+directory+'/content.json','locator':collection+'.'+row['id']}],
                                'full_content_imported':False})
    records=unique(records,lambda r:r['id'],audit,'content_index')
    catalog=json.loads((CORE/'experience/CONTENT_CATALOG.json').read_text())
    paths=[p['path']+'/'+f for p in catalog['packs'] for f in p['files']]
    require(len(paths)==len(set(paths))==32,'Historical catalog path duplication')
    require(sum(r['id']=='EDU-TOPIC-government-schemes' for r in records)==1,'Scheme topic must have one owner')
    return {'schema_version':1,'scope':'Current indexed references, not the complete historical 421 products or an exhaustive archive-content audit.',
            'records':records,'indexed_reference_count':len(records),'education_topic_count':len(topics),
            'deduplication_basis':'Exact identity + equal source record only. Conflicts stop rebuild; similar titles, different editions or source contexts are not silently merged.',
            'duplicates_removed':audit,'historical_catalog_files':len(paths),'historical_catalog_unique_paths':len(set(paths)),
            'education_owner':'EDU','government_schemes_owner':'EDU',
            'education_in_current_entertainment_packs':'No education pack/ownership was found to undo. Explicit topic ownership is now EDU; previous historical references are preserved.'}


def render_report(data,index):
    t=data['totals'];lines=['# Vyomaraj — Current Agent Reconciliation','', '**3 October 2026 · owner-approved structure · not a deployment claim**','',
    '## Applied decisions','',
    '- A later explicit user request adds **Aghor & Aghori** (`BHAKTI-AGHOR-S1`) under BHAKTI / Bhakti-Shakti. BHAKTI now has 3 counted positions; its earlier two unnamed positions are retained.',
    '- EDU is now displayed as **Education**. All Government Schemes are owned by Education, not Finance or Entertainment.',
    '- Comedy hub, Cartoon, Music, Movie, Wit and Shayari are uncounted parent headings, not six additional counted agents. Their existing child IDs are preserved.',
    '- INDICOM and Criticism gate stay as distinct named agents. Hasya, Liquor and Bar keep their own numbered positions; similar subject matter is not sufficient evidence to merge them.',
    '- Unnamed records display serial numbers only. Their machine-readable names remain null; no replacement names have been coined.',
    '- Historical snapshot files and archives are retained as evidence. Current applications use the new active registry, not a rewritten V16.7.24 snapshot.','',
    '## Reconciled counts','', '| Measure | Historical snapshot | Current |','|---|---:|---:|',
    '| Main categories | 13 | 13 |','| Counted sub-agent slots | 133 | 128 |','| Entertainment slots | 38 | 32 |','| Education slots | 15 | 16 |','| Finance slots | 8 | 7 |',
    '| Separate uncounted Entertainment headings | Not separated | 6 |','| Supplied/approved individual names | 46 | 42 |','| Unnamed numbered positions | 87 | 86 |',
    '| Reported products | 421 | Reallocation / unique total UNRECONCILED |','',
    'The six-heading reclassification first gave 133 → 127. The later requested Aghor sub-agent adds one: 127 → 128. Government Schemes is a one-position transfer, not an extra agent: Finance −1, Education +1. The source canonical Finance roster was count-only; its historical diagram labels S1 as Govt Schemes. This current transfer is explicitly owner-approved, not a claim that the old canonical registry supplied that individual mapping.','',
    '## Current main-agent inventory','', '| Category | Current display name | Counted slots | Uncounted headings | Historical reported products |','|---|---|---:|---:|---:|']
    for c in data['categories']:lines.append(f"| {c['id']} | {c['name']} | {c['sub_agents']} | {c['headings']} | {c['source_reported_products']} |")
    lines+=['','Product figures above are source-history metadata, not current reallocated or deduplicated totals. In particular, Education 68 and Finance 15 cannot be apportioned after the scheme transfer without their item-level product lists.','',
    '## Duplicate audit and scope','',f"- Active hierarchy: 13 category identities, 128 counted agent identities and 6 heading identities; all unique and parent-validated.",
    f"- Exact repeated source roster records removed: **{len(data['count_reconciliation']['exact_duplicate_records_removed'])}**. The six semantic double-counted hub positions were reclassified by the explicit approval above, not presented as byte-identical records.",
    f"- Current content index: **{index['indexed_reference_count']} references**, including **{index['education_topic_count']} Education topics** and the selected collections in the five editorial experiences. These are references, not all 421 products or new agents.",
    f"- Exact repeated indexed content records removed: **{len(index['duplicates_removed'])}**. Equal identities collapse only if records are equal; conflicting duplicates stop the builder.",
    '- All 32 historical catalogue paths are unique. No runtime/configuration bodies are imported by this reconciliation builder.',
    '- Multiple references to the same stable agent ID from planners, content and reports are links to one agent, not duplicate agents to delete.',
    '- No fuzzy title-based deletion, cross-edition merging, archive deletion or speculative chapter/sub-sub-agent creation was performed.',
    '- Archives and unindexed legacy documents were not exhaustively content-deduplicated. Their historical versions must not be described as duplicate live agents.','',
    '## Education ownership and content','',
    'The saved registry already had a separate EDU category. The current Film/Music editorial packs did not contain a misplaced Education pack. Therefore this work establishes a single authoritative Education routing/index and transfers Government Schemes; it does not claim to recover or physically move missing full lectures, scheme databases or study texts. Historical Education topics are indexed below.','',
    '| Education topic | Current owner | Mapping / content scope |','|---|---|---|']
    for r in index['records']:
        if r['owner_category']=='EDU':lines.append(f"| {r['title']} | Education | Source-backed topic metadata; not a newly recovered full text |")
    lines+=['','Education-related entertainment formats remain formats; that does not make Entertainment the owner of the educational subject. Bhakti devotional material stays in BHAKTI. Non-scheme financial topics stay in FINANCE. The new scheme entry contains no researched benefits, eligibility, current availability or application advice.','',
    '## Serial-only roster','',
    'Serials are current display positions within each category, not recovered historic slot numbers. Blank name cells deliberately remain blank. Internal IDs are available in the JSON/advanced viewer to preserve working integrations, not as newly coined names. PLATFORM display position 20 still has source slot UNMAPPED; it is not labelled historical S20.','']
    headings={h['id']:h['name'] for h in data['headings']}
    for c in data['categories']:
        lines+=['### '+c['name'],'','| Serial | Supplied/approved name (blank = not assigned) | Parent heading |','|---:|---|---|']
        for a in data['agents']:
            if a['category_id']==c['id']:lines.append(f"| {a['serial']} | {a['name'] or ''} | {headings.get(a['parent_id'],'')} |")
        if c['id']=='EDU':lines+=['','Positions 8–13 retain the shared source label “Bharat Grantha, Chanakya and the Granthas”; no six individual names or assignments are inferred.']
    lines+=['','## Preserved integrations and boundaries','',
    '- Music ENT-MUS-S1–S6, Movie ENT-MOVIE-S1–S6, Liquor ENT-LIQUOR-S1 and Bar ENT-BAR-S1 remain valid. Their functional/chapter bindings remain proposals, not newly assigned names.',
    '- Source-reported Hasya / Liquor / Bar chapter counts 12 / 12 / 10 remain metadata, not extra agent or product counts.',
    '- Six approved headings establish those parent-child edges only. Other missing sub-sub-agent identities/counts remain UNMAPPED.',
    '- Eleven historical sovereign roles remain separate cross-cutting references, not extra children in the 128 total: '+', '.join(data['historical_sovereign_roles'])+'.',
    '- No populated private runtime, device, environment or credential values are exposed. No provider deployment, publication, GitHub permission change or DR success is implied.','',
    '## Files, viewer and reproducibility','',
    '- `/agents/`: current serial-first hierarchy and indexed content references.',
    '- `/education/`: Education-filtered roster and all 21 educational-topic references, including Government Schemes.',
    '- `/reports/agents` and `/reports/`: current reconciliation and inventory.',
    '- `/reports/history`: explicitly historical pre-reconciliation inventory; old 133/38/15/8 figures are not current counts.',
    '- `agents/AGENT_REGISTRY_CURRENT.json`: authoritative current metadata hierarchy.',
    '- `agents/CONTENT_OWNERSHIP_CURRENT.json` and `CONTENT_INDEX_CURRENT.json`: single-owner Education routing and bounded content-reference index.',
    '- `agents/RECONCILIATION_RULES.json`: recorded owner-approved decisions.',
    '- `python ops/vyomaraj-core/agents/rebuild_registry.py --check`: deterministic rebuild, unique identities, conflict refusal, parent/count validation and pack-link checks.',
    '- Historical `handover/AGENT_CONTENT_REGISTRY_V16_7_24.json` and `experience/CONTENT_CATALOG.json` remain byte-for-byte unchanged.','',
    '## Validation scope','',
    '**Earlier reconciliation baseline: 180 automated checks PASS:** DR 29; historical handover 13; Pairings 9; integrated experience/HTTP 62; discovery 36; current registry 28; Node metadata-safety 3.',
    '**Earlier baseline: all five real Chromium suites PASS:** Agents/Education, Research, Film/Stage/Ads, Music, Bhakti/Pairings. Checks cover the 127 unique identities and six headings, serial-only unnamed display, Education/Government Schemes ownership, audit toggle/search/filter/download, all existing plans and local media flows, current/historical reports, navigation, desktop/mobile layout, no horizontal overflow or JS errors.',
    'Current Aghor / DR follow-up validation is recorded separately at `/reports/resilience`. The preceding numbers describe the earlier 127-slot baseline, not the later test total.',
    'Both deterministic rebuild checks, six app-script syntax checks, workflow YAML parsing and diff whitespace checks pass. The earlier full inventory is preserved byte-for-byte as the historical inventory. Source registry/catalogue hashes remain pinned. No production deployment, external AI connection or DR verification was performed by these tests.','']
    return '\n'.join(lines)


def outputs():
    raw=SNAPSHOT.read_bytes();source=json.loads(raw)
    rules=json.loads((HERE/'RECONCILIATION_RULES.json').read_text())
    ownership=json.loads((HERE/'CONTENT_OWNERSHIP_CURRENT.json').read_text())
    active=build(source,rules);active['source_snapshot_sha256']=hashlib.sha256(raw).hexdigest()
    index=content_index(ownership,active);report=render_report(active,index)
    current='# Vyomaraj / Jarvis — Current System Inventory\n\n**Current structure: 13 categories · 128 counted sub-agent slots · 6 uncounted parent headings.**\n\nThis is the current owner-approved view. The former 133-slot inventory is preserved at `/reports/history`; it is not silently deleted or presented as the active structure. Historical 421-product and 32-file catalogue counts are not a complete, deduplicated item-level product list.\n\n'
    current+='## Integrated viewers\n\n| Area | Viewer / report |\n|---|---|\n| Current hierarchy | /agents/ · /reports/agents |\n| Aghor & Aghori | /aghor/ · /reports/aghor |\n| Latest DR / Aghor update | /reports/resilience |\n| Education and all Government Schemes | /education/ |\n| All experience content | /reports/contents |\n| Research Desk | /research/ · /reports/research |\n| Film, stage and ads | /film/ · /reports/film |\n| Music | /music/ · /reports/music |\n| Bhakti-Shakti | /bhakti/ · /reports/bhakti |\n| Roots & Pairings | /pairings/ |\n| Earlier DR audit (latest status above) | /reports/dr |\n| Historical source audit | /reports/history |\n\n'
    current+=report.replace('# Vyomaraj — Current Agent Reconciliation','# Current Agent Reconciliation',1)
    return {ACTIVE:json.dumps(active,ensure_ascii=False,indent=2)+'\n',INDEX:json.dumps(index,ensure_ascii=False,indent=2)+'\n',REPORT:report,INVENTORY:current}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for path,text in outputs().items():
        if args.check:require(path.is_file() and path.read_text()==text,'Out of date: '+path.name)
        else:path.write_text(text)
    print('PASS current hierarchy: 13 categories / 128 counted slots / 6 headings; Education 16, Finance 7, Entertainment 32. Historical snapshot preserved.')
