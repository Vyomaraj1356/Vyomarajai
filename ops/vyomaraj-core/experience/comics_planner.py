"""Deterministic original comics planning. Trilingual editions (Hindi/English/Hinglish) with
preserved past versions and plannable future versions. No copied characters, no artwork
rendering, no media hosting and no provider calls."""
from datetime import datetime, timezone
import json

FORMAT_LIMITS = {'strip': (3, 6), 'oneshot': (8, 32), 'issue': (24, 64),
                 'graphic-novel': (96, 240)}
LANGUAGES = ('hi', 'en', 'hinglish')
CAPTION_KEYS = {'hi': 'Hindi', 'en': 'English', 'hinglish': 'Hinglish'}


class InvalidComicsPlan(ValueError):
    pass


def build_comics_plan(request, path):
    if set(request) - {'experience', 'item_ids', 'format', 'primary_language',
                       'versions', 'seed', 'panels'}:
        raise InvalidComicsPlan('Unknown comics-planning fields; files and URLs are not accepted.')
    ids = request.get('item_ids', [])
    if (not isinstance(ids, list) or len(ids) > 6 or any(not isinstance(x, str) for x in ids)
            or len(set(ids)) != len(ids)):
        raise InvalidComicsPlan('Select up to six distinct reference IDs.')
    kind = request.get('format', 'strip')
    language = request.get('primary_language', 'en')
    lineage = request.get('versions', 'all')
    seed_name = request.get('seed', 'monsoon-post')
    if kind not in FORMAT_LIMITS:
        raise InvalidComicsPlan('Unknown comic format.')
    if language not in LANGUAGES:
        raise InvalidComicsPlan('Edition languages are hi, en and hinglish — one primary display language.')
    if lineage not in ('past', 'future', 'all'):
        raise InvalidComicsPlan('Version lineage is past, future or all.')
    if seed_name not in ('monsoon-post', 'first-flight'):
        raise InvalidComicsPlan('Unknown original story seed.')
    data = json.loads(path.read_text(encoding='utf-8'))
    fmt = next(f for f in data['formats'] if f['id'] == kind)
    panels = request.get('panels', fmt['default_panels'])
    if type(panels) is not int or not FORMAT_LIMITS[kind][0] <= panels <= FORMAT_LIMITS[kind][1]:
        raise InvalidComicsPlan('Panel count is outside the selected format’s local planning range.')
    index = {i['id']: i for i in data['items']}
    if any(i not in index for i in ids):
        raise InvalidComicsPlan('Unknown comics reference ID.')
    references = [index[i] for i in ids]

    routes = {'heritage-reference': 1, 'humour-strip': 2}
    slots = {f'ENT-CARTOON-S{routes.get(i["kind"], 3)}' for i in references}
    slots.add('ENT-CARTOON-S2' if kind == 'strip' else 'ENT-CARTOON-S3')
    slots.add('ENT-CARTOON-S3')  # every plan carries the trilingual edition + version lineage desk
    source_ids = {s for i in references for s in i['source_ids']}

    seed = data['original_seeds'][seed_name]
    per, extra = divmod(panels, len(fmt['beats']))
    panel_plan, number = [], 1
    for n, beat in enumerate(fmt['beats']):
        count = per + (n < extra)
        panel_plan.append({'beat': beat, 'panel_numbers': list(range(number, number + count)),
                           'budget_panels': count,
                           'art_cue': 'Plan an original layout; no published artwork is referenced or inserted.',
                           'lettering_cue': 'Lettering is planned for all three editions (Hindi, English, Hinglish); '
                                            'caption lengths differ per language and are checked per edition.'})
        number += count
    editions = [{'language': code, 'title': seed['editions'][code]['title'],
                 'tagline': seed['editions'][code]['tagline']} for code in LANGUAGES]
    lineage_selected = {scope: list(seed['versions'][scope]) for scope in ('past', 'future')
                        if lineage in ('all', scope)}
    return {
        'schema_version': 1, 'status': 'local_plan_created', 'experience': 'comics',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'category_id': 'ENTERTAINMENT', 'canonical_agent_ids': sorted(slots),
        'assignment_status': 'proposed_functional_bindings_not_recovered_names',
        'proposed_agent_bindings': [a for a in data['agents'] if a['slot'] in slots],
        'format': kind, 'panels': panels, 'panel_budget': panel_plan,
        'panel_budget_basis': 'panel_counts_not_finished_artwork',
        'primary_language': language,
        'language_matrix': {
            'policy': data['language_policy']['rule'],
            'required_edition_languages': list(LANGUAGES),
            'editions': editions,
            'coverage': 'all_three_editions_are_produced_for_every_plan_and_every_version'},
        'version_lineage': {
            'selected': lineage,
            'past_rule': data['version_policy']['past_versions'],
            'future_rule': data['version_policy']['future_versions'],
            **lineage_selected},
        'original_seed': {'id': seed_name, 'title': seed['title'], 'premise': seed['premise']},
        'sample_captions_language': CAPTION_KEYS[language],
        'sample_captions': seed['captions'][CAPTION_KEYS[language]],
        'role_handoff': [
            {'role': 'Vyomaraj', 'implementation': 'deterministic_local_comics_router',
             'action': 'Validated references, format and panel budget; assigned existing cartoon slots '
                       'using proposed functional bindings; attached the trilingual edition matrix.'},
            {'role': 'Jarvis', 'implementation': 'deterministic_local_comics_review',
             'action': 'Prepared the version lineage, caption samples and review gates, and routed the '
                       'finished plan to the owner approval queue (central nostalgic camera) — never to a publisher.'}],
        'owner_gate': {'status': 'PENDING_OWNER_PERMISSION',
                       'queue': 'ops/vyomaraj-core/approvals (central nostalgic camera)',
                       'rule': 'Nothing publishes without the owner reviewing it in the camera queue '
                               'and choosing approve / reject / rework / submit.'},
        'source_references': [s for s in data['sources'] if s['id'] in source_ids],
        'review_gates': [
            'Original characters and artwork only: no published character, likeness, logo or art style is copied or imitated.',
            'Heritage entries are context references, not licences; Amar Chitra Katha, Tinkle, Chacha Chaudhary, '
            'Raj Comics, Indrajal and Chandamama material stays with its owners.',
            'Every edition (Hindi, English, Hinglish) needs native-language review before release; '
            'Hinglish must stay a natural mix, not a mechanical transliteration.',
            'Past editions are preserved read-only; future editions extend the line — never overwrite or merge versions.',
            'Fact-bearing panels (astronomy, food, mythology) need the same review as the corresponding knowledge lanes.',
            'This plan is panel budgets and captions, not finished artwork, lettering or a printed comic.',
            'Human review is required before any public release.'],
        'provider': None, 'ai_calls_made': False, 'artwork_rendered': False,
        'publishing_enabled': False, 'media_hosted': False,
        'legacy_device_config_loaded': False, 'production_deployed': False, 'dr_sync_verified': False
    }
