"""Deterministic Vyomaraj/Jarvis local planning; no model, shell or network calls."""
from datetime import datetime, timezone
import json
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent
PACKS = {'bhakti': CORE / 'bhakti-experience/content.json',
         'liquor-bar': CORE / 'liquor-bar/content.json'}


class InvalidPlan(ValueError):
    pass


def build_plan(request):
    if not isinstance(request, dict):
        raise InvalidPlan('Request must be a JSON object.')
    allowed = {'experience', 'topic_id', 'recipe_id', 'mode', 'diet', 'exclude_allergens'}
    if set(request) - allowed:
        raise InvalidPlan('Unknown request fields; only allowlisted preferences are accepted.')
    experience = request.get('experience')
    mode = request.get('mode', '3d')
    diet = request.get('diet', 'all')
    if not isinstance(experience, str) or experience not in PACKS:
        raise InvalidPlan('Unknown experience.')
    if mode not in ('3d', '4d', '5d') or diet not in ('all', 'plant-based', 'vegetarian', 'pescatarian'):
        raise InvalidPlan('Unknown mode or diet.')
    exclude = request.get('exclude_allergens', [])
    if (not isinstance(exclude, list) or len(exclude) > 4 or
            any(not isinstance(x, str) or x not in ('milk', 'peanut', 'soy', 'fish') for x in exclude)):
        raise InvalidPlan('Invalid allergen preferences.')
    topic_id = request.get('topic_id', 'overview')
    recipe_id = request.get('recipe_id')
    if not isinstance(topic_id, str) or (recipe_id is not None and not isinstance(recipe_id, str)):
        raise InvalidPlan('Topic and recipe IDs must be strings.')
    data = json.loads(PACKS[experience].read_text(encoding='utf-8'))
    if experience == 'bhakti':
        topics = data['stories'] + data['avatars'] + data['peethas']
        topics += [{'id': 'mahadev-tv', 'title': data['television']['title'],
                    'source_ids': data['television']['source_ids']}]
        recipes = data['recipes']
        category, agents = 'BHAKTI', []
        blockers = ['Canonical BHAKTI sub-agent slot remains UNMAPPED.',
                    'Chapter titles are proposals; the Peetha atlas is a starter, not a complete list.',
                    'Separate devotional tradition, documented history and screen adaptation.',
                    'Temple-specific ritual rules and all media rights require review.']
    else:
        topics = data['traditions']
        recipes = data['snacks']
        category, agents = 'ENTERTAINMENT', ['ENT-LIQUOR-S1', 'ENT-BAR-S1']
        blockers = ['Local legal-age and alcohol-law review required for alcohol content.',
                    'Chapter titles are proposals; exact product specifications remain unverified.',
                    'Food is not an alcohol-health, detox or hangover-prevention claim.']
    if topic_id == 'overview':
        topic = {'id': 'overview', 'title': data['title'],
                 'source_ids': [s['id'] for s in data['sources']]}
    else:
        topic = next((t for t in topics if t['id'] == topic_id), None)
        if topic is None:
            raise InvalidPlan('Topic is not part of the selected experience.')
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if recipe_id is not None and recipe is None:
        raise InvalidPlan('Recipe is not part of the selected experience.')
    if recipe:
        compatible = (diet in ('all', 'pescatarian') or recipe['diet'] == diet or
                      (diet == 'vegetarian' and recipe['diet'] == 'plant-based'))
        if not compatible or set(exclude) & set(recipe['allergens']):
            raise InvalidPlan('Selected recipe conflicts with the supplied dietary/allergen preferences.')
    source_ids = topic['source_ids']
    sources = [s for s in data['sources'] if s['id'] in source_ids]
    if not sources:
        blockers.append('Selected topic has no cited source yet; research is required.')
    return {
        'schema_version': 1, 'status': 'local_plan_created',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'experience': experience, 'category_id': category, 'canonical_agent_ids': agents,
        'topic': {'id': topic['id'], 'title': topic.get('title', topic.get('name'))},
        'mode': mode, 'recipe': None if recipe is None else {'id': recipe['id'], 'name': recipe['name']},
        'preferences': {'diet': diet, 'exclude_allergens': sorted(set(exclude))},
        'role_handoff': [
            {'role': 'Vyomaraj', 'implementation': 'deterministic_local_planner',
             'action': 'Validated pack, topic, mode and recipe preferences; prepared category route.'},
            {'role': 'Jarvis', 'implementation': 'deterministic_local_handoff',
             'action': 'Attached evidence, mapping gaps and approval checklist; no external execution.'}],
        'source_references': sources, 'review_gates': blockers + [
            'Recipe quantities, ingredient labels and cross-contact require food-safety review.',
            'Visuals are illustrative CSS, not connected AI generation or physical sensory output.',
            'Human review required before public release.'],
        'provider': None, 'ai_calls_made': False, 'publishing_enabled': False,
        'legacy_device_config_loaded': False, 'production_deployed': False, 'dr_sync_verified': False,
        'chapter_mapping_status': 'proposed_not_recovered_original_titles'
    }
