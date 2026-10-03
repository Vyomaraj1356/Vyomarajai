"""Local music sub-agent functions: metadata routes and timed editorial plans, not media execution."""
from datetime import datetime, timezone
import json


class InvalidMusicPlan(ValueError):
    pass


def build_music_plan(request, pack_path):
    allowed = {'experience', 'item_ids', 'mode', 'duration_minutes'}
    if set(request) - allowed:
        raise InvalidMusicPlan('Unknown music request fields.')
    ids = request.get('item_ids', [])
    if (not isinstance(ids, list) or not 1 <= len(ids) <= 8 or
            any(not isinstance(x, str) for x in ids) or len(set(ids)) != len(ids)):
        raise InvalidMusicPlan('Choose 1–8 distinct catalogue IDs.')
    mode = request.get('mode', 'radio')
    minutes = request.get('duration_minutes', 30)
    if mode not in ('radio', 'audio', 'video') or type(minutes) is not int or minutes not in (15, 30, 60):
        raise InvalidMusicPlan('Choose radio/audio/video and a 15, 30 or 60 minute planning budget.')
    data = json.loads(pack_path.read_text(encoding='utf-8'))
    index = {item['id']: item for item in data['items']}
    if any(id not in index for id in ids):
        raise InvalidMusicPlan('Unknown music catalogue ID.')
    items = [index[id] for id in ids]
    roles = {kind: agent for agent in data['agents'] for kind in agent['kinds']}
    slots = {roles[item['kind']]['slot'] for item in items}
    slots.add(roles['video' if mode == 'video' else 'audio']['slot'])
    if mode == 'radio':
        slots.add(roles['radio']['slot'])
    source_ids = {id for item in items for id in item['source_ids']}
    bindings = [a for a in data['agents'] if a['slot'] in slots]
    rundown = [{'start_seconds': 0, 'budget_seconds': 45, 'type': 'original_intro',
                'text': 'Welcome to Memory & Melody. Explore familiar radio memories and new listening routes, with a source and a credit for every stop.'}]
    available = minutes * 60 - 120
    budget, remainder = divmod(available, len(items))
    start = 45
    for i, item in enumerate(items):
        seconds = budget + (1 if i < remainder else 0)
        rundown.append({'start_seconds': start, 'budget_seconds': seconds, 'type': 'editorial_feature',
                        'item_id': item['id'], 'title': item['title'],
                        'catalogue_credits': item['artists'], 'language': item['language'],
                        'record_type': item['record_type'], 'catalogue_year': item['year'],
                        'proposed_agent_slot': roles[item['kind']]['slot'],
                        'cue': 'Introduce the context and credits; select a cleared recording or original commentary. This budget is not a measured track length.',
                        'source_ids': item['source_ids'], 'media_url': None})
        start += seconds
    rundown += [{'start_seconds': start, 'budget_seconds': 30, 'type': 'source_credits',
                 'text': 'Credit the sources and performers; state any chart period and territory aloud.'},
                {'start_seconds': start + 30, 'budget_seconds': 45, 'type': 'original_outro',
                 'text': 'Keep exploring beyond the familiar. This programme remains a planning document until its recordings, facts and permissions are reviewed.'}]
    return {
        'schema_version': 1, 'status': 'local_plan_created', 'experience': 'music',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'category_id': 'ENTERTAINMENT', 'canonical_agent_ids': sorted(slots),
        'assignment_status': 'proposed_functional_bindings_not_recovered_names',
        'proposed_agent_bindings': bindings, 'mode': mode, 'duration_minutes': minutes,
        'duration_basis': 'editorial_slot_budgets_not_recording_lengths',
        'item_ids': ids, 'rundown': rundown,
        'source_references': [s for s in data['sources'] if s['id'] in source_ids],
        'chart_snapshot': data['chart_snapshot'] if 'ifpi2025' in ids else None,
        'role_handoff': [
            {'role': 'Vyomaraj', 'implementation': 'deterministic_local_music_router',
             'action': 'Validated catalogue selections and budget; assigned existing music slots using proposed functional bindings.'},
            {'role': 'Jarvis', 'implementation': 'deterministic_local_music_review',
             'action': 'Prepared timed rundown, source credits and rights gates; no playback, external AI or publication.'}],
        'review_gates': [
            'Original names of the six music sub-agents remain UNKNOWN; proposed assignments need approval.',
            'Verify performer, composer, lyricist, edition and recording dates; discovery is not a full discography.',
            'Clear applicable recording, composition, broadcast, lyrics, artwork, sync and video rights for the intended use and territory.',
            'Provider links are not playback licences; historical or folk recordings are not automatically public domain.',
            'Review explicit/clean editions, captions and accessibility; catalogue entries are not certified child-safe.',
            'Use original presenter commentary, not an impersonation or unlicensed archive rebroadcast.',
            'Charts keep separate publisher, period, territory and metric. Annual snapshots are not live weekly rankings.',
            'No-sources production-format cards are proposals, not evidence-backed historical claims.',
            'Confirm actual recording lengths before converting this timed editorial budget into a broadcast.',
            'Human review is required before public release.'],
        'provider': None, 'ai_calls_made': False, 'streaming_connected': False,
        'live_charts_connected': False, 'publishing_enabled': False,
        'legacy_device_config_loaded': False, 'production_deployed': False, 'dr_sync_verified': False
    }
