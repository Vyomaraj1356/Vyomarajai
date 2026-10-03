"""Deterministic original film/stage/ad outlines. No copied scripts, media rendering or provider calls."""
import json
from datetime import datetime, timezone

LIMITS = {'feature': (1800, 10800), 'short': (60, 1800), 'clip': (6, 180),
          'long-play': (1800, 10800), 'one-act': (120, 1800), 'advert': (6, 120), 'mix': (15, 600)}


class InvalidFilmPlan(ValueError):
    pass


def build_film_plan(request, path):
    if set(request) - {'experience', 'item_ids', 'format', 'language', 'seed', 'duration_seconds'}:
        raise InvalidFilmPlan('Unknown film-planning fields; files and URLs are not accepted.')
    ids = request.get('item_ids', [])
    if (not isinstance(ids, list) or len(ids) > 8 or any(not isinstance(x, str) for x in ids)
            or len(set(ids)) != len(ids)):
        raise InvalidFilmPlan('Select up to eight distinct reference IDs.')
    kind, language, seed = request.get('format', 'short'), request.get('language', 'Marathi'), request.get('seed', 'shelf')
    if not isinstance(kind, str) or kind not in LIMITS or language not in ('Marathi', 'Hindi', 'English'):
        raise InvalidFilmPlan('Unknown format or dialogue language.')
    if not isinstance(seed, str) or seed not in ('shelf', 'repair'):
        raise InvalidFilmPlan('Unknown original story seed.')
    data = json.loads(path.read_text(encoding='utf-8'))
    format = next(f for f in data['formats'] if f['id'] == kind)
    duration = request.get('duration_seconds', format['default_seconds'])
    if type(duration) is not int or not LIMITS[kind][0] <= duration <= LIMITS[kind][1]:
        raise InvalidFilmPlan('Duration is outside the selected format’s local planning range.')
    index = {i['id']: i for i in data['items']}
    if any(i not in index for i in ids):
        raise InvalidFilmPlan('Unknown film reference ID.')
    references = [index[i] for i in ids]
    routes = {'feature': 1, 'version-check': 1, 'short': 2, 'clip': 3, 'archive': 3, 'advert': 6}
    def route(item):
        return routes.get(item['kind'], 4 if item['language'] == 'Marathi' else 5)
    primary = {'feature': 1, 'short': 2, 'clip': 3, 'mix': 3, 'advert': 6}.get(kind, 4 if language == 'Marathi' else 5)
    slots = {f'ENT-MOVIE-S{primary}'} | {f'ENT-MOVIE-S{route(i)}' for i in references}
    source_ids = {s for i in references for s in i['source_ids']}
    if kind == 'advert':
        source_ids.add('asci')
    chosen = data['original_seeds'][seed]
    per, extra = divmod(duration, len(format['beats']))
    start, beats = 0, []
    for n, title in enumerate(format['beats']):
        seconds = per + (n < extra)
        beats.append({'number': n + 1, 'title': title, 'start_seconds': start, 'budget_seconds': seconds,
                      'visual_or_stage_cue': ('Stage a clear entrance, blocking change and exit using the original premise.'
                          if kind in ('long-play', 'one-act') else
                          'Plan an original wide, medium or detail shot; no reference footage is automatically inserted.'),
                      'sound_cue': 'Original dialogue or cleared sound; preserve intelligibility and caption timing.'})
        start += seconds
    return {
        'schema_version': 1, 'status': 'local_plan_created', 'experience': 'film',
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'category_id': 'ENTERTAINMENT',
        'canonical_agent_ids': sorted(slots), 'assignment_status': 'proposed_functional_bindings_not_recovered_names',
        'proposed_agent_bindings': [a for a in data['agents'] if a['slot'] in slots],
        'format': kind, 'duration_seconds': duration, 'duration_basis': 'outline_budget_not_finished_runtime',
        'planning_notes_language': 'English', 'sample_dialogue_language': language,
        'original_seed': {'id': seed, 'title': chosen['title'], 'premise': chosen['premise']},
        'sample_dialogue': chosen['dialogue'][language], 'beats': beats,
        'script_status': 'original_outline_and_short_dialogue_sample_not_full_screenplay',
        'references': references, 'reference_usage': 'research_context_only_not_adaptation_or_footage_permission',
        'source_references': [s for s in data['sources'] if s['id'] in source_ids],
        'role_handoff': [
            {'role': 'Vyomaraj', 'action': 'Validated format, reference IDs and original seed; routed existing Movie slots locally.'},
            {'role': 'Jarvis', 'action': 'Prepared budgeted beats, original dialogue samples and review gates; no media rendered.'}],
        'review_gates': [
            'Canonical slot names remain UNKNOWN; proposed assignments need approval.',
            'An outline is not a full screenplay, completed play or rendered movie. Develop and rehearse it before production.',
            'Reference titles are research context only. Clear adaptation, translation, performance, footage and distribution rights separately.',
            'Check music, logos, artwork, likeness/performer consent, archival restrictions and territories for the intended use.',
            'No universal safe clip length is assumed; fair-use/fair-dealing and other exceptions depend on purpose and jurisdiction.',
            'Review Marathi/Hindi wording, subtitles, captions, audio description and content advisories.',
            'For advertising, substantiate claims, verify current ASCI/legal requirements and disclose material connections where required.',
            'A brand’s own remake does not license third-party campaign copies or jingles.',
            'Local edit decisions are not an encoded MP4; production rendering and audio mixing are not connected.',
            'Human approval is required before publishing or public performance.'],
        'provider': None, 'ai_calls_made': False, 'media_rendered': False, 'streaming_connected': False,
        'publishing_enabled': False, 'legacy_device_config_loaded': False, 'production_deployed': False, 'dr_sync_verified': False
    }
