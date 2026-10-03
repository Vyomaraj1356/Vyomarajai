"""Deterministic, non-medical Aghor study handoff. No initiation or dangerous ritual generation."""
import json
from datetime import datetime,timezone

def build_aghor_plan(request,path):
    if not isinstance(request,dict) or set(request)-{'experience','topic_id','mode'}:raise ValueError('Only experience, topic_id and mode are accepted; no symptoms or treatment requests.')
    topic_id=request.get('topic_id','meaning');mode=request.get('mode','study')
    if not isinstance(topic_id,str) or not isinstance(mode,str) or mode not in ('study','reflection','service'):raise ValueError('Choose study, reflection or service; no ritual or treatment mode.')
    data=json.loads(path.read_text());topic=next((t for t in data['chapters'] if t['id']==topic_id),None)
    if not topic:raise ValueError('Unknown Aghor study chapter.')
    routine=next(p for p in data['practices'] if p['id']==mode)
    ids=set(topic['source_ids']+routine['source_ids'])
    return {'schema_version':1,'status':'local_plan_created','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'experience':'aghor','category_id':'BHAKTI','canonical_agent_ids':['BHAKTI-AGHOR-S1'],
        'topic':{'id':topic['id'],'title':topic['title'],'evidence_classification':topic['classification']},
        'mode':mode,'steps':routine['steps'],'chapter_mapping_status':'proposed_editorial_chapter',
        'source_references':[s for s in data['sources'] if s['id'] in ids],
        'role_handoff':[{'role':'Vyomaraj','action':'Select a bounded, source-labelled study topic.'},{'role':'Jarvis','action':'Attach safe optional steps and review gates; no external execution.'}],
        'review_gates':data['editorial_rules']+['This is not a medical diagnosis, treatment prescription, initiation, supernatural claim or endorsement of a teacher.','Check dates, source limits, consent and any current institution arrangements before external publication.'],
        'provider':None,'ai_calls_made':False,'publishing_enabled':False,'medical_treatment':False,'dangerous_ritual_instructions':False,'production_deployed':False,'dr_sync_verified':False}
