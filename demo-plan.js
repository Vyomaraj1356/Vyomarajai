'use strict';
(function register(root, factory) {
  const planner = factory();
  if (typeof module === 'object' && module.exports) module.exports = planner;
  if (root) root.VyomarajDemoPlanner = planner;
})(typeof globalThis === 'undefined' ? this : globalThis, function createPlanner() {
  const experiences = new Set(['bhakti', 'liquor-bar']);
  const modes = new Set(['3d', '4d', '5d']);
  const diets = new Set(['all', 'plant-based', 'vegetarian', 'pescatarian']);
  const sharedGates = [
    'Recipe quantities, ingredient labels and cross-contact require food-safety review.',
    'Visuals are illustrative CSS, not connected AI generation or physical sensory output.',
    'Human review required before public release.',
  ];
  const blockers = {
    bhakti: [
      'Canonical BHAKTI sub-agent slot remains UNMAPPED.',
      'Chapter titles are proposals; the Peetha atlas is a starter, not a complete list.',
      'Separate devotional tradition, documented history and screen adaptation.',
      'Temple-specific ritual rules and all media rights require review.',
    ],
    'liquor-bar': [
      'Local legal-age and alcohol-law review required for alcohol content.',
      'Chapter titles are proposals; exact product specifications remain unverified.',
      'Food is not an alcohol-health, detox or hangover-prevention claim.',
    ],
  };

  function buildPlan(request, catalog) {
    if (!request || typeof request !== 'object' || Array.isArray(request)) {
      throw new Error('Request must be a JSON object.');
    }
    const allowed = new Set(['experience', 'topic_id', 'recipe_id', 'mode', 'diet']);
    if (Object.keys(request).some(key => !allowed.has(key))) {
      throw new Error('Unknown request fields; only allowlisted preferences are accepted.');
    }
    if (!catalog || !experiences.has(catalog.experience) || request.experience !== catalog.experience) {
      throw new Error('Select one of the two allowlisted local demo experiences.');
    }
    const mode = request.mode || '3d';
    const diet = request.diet || 'all';
    if (!modes.has(mode) || !diets.has(diet)) throw new Error('Unknown mode or diet.');
    const topicId = request.topic_id || 'overview';
    if (typeof topicId !== 'string' || topicId.length > 100) throw new Error('Topic ID must be a short known-topic identifier.');
    const recipeId = request.recipe_id || null;
    if (recipeId !== null && (typeof recipeId !== 'string' || recipeId.length > 64)) {
      throw new Error('Recipe ID must be a short recipe identifier.');
    }

    const entries = Array.isArray(catalog.items) ? catalog.items : [];
    let topic;
    if (topicId === 'overview') {
      topic = {
        id: 'overview',
        title: catalog.title,
        source_references: catalog.overview_source_references || [],
      };
    } else {
      topic = entries.find(item => item.kind === 'topic' && item.id === topicId);
      if (!topic) throw new Error('Topic is not part of the selected experience.');
    }
    const recipes = entries.filter(item => item.kind === 'recipe');
    const recipe = recipeId ? recipes.find(item => item.id === recipeId) : null;
    if (recipeId && !recipe) throw new Error('Recipe is not part of the selected experience.');
    if (recipe) {
      const compatible = diet === 'all' || diet === 'pescatarian' || recipe.diet === diet ||
        (diet === 'vegetarian' && recipe.diet === 'plant-based');
      if (!compatible) throw new Error('Selected recipe conflicts with the supplied dietary preferences.');
    }
    const sourceReferences = topic.source_references || [];
    const reviewGates = [...blockers[catalog.experience]];
    if (!sourceReferences.length) reviewGates.push('Selected topic has no cited source yet; research is required.');
    reviewGates.push(...sharedGates);
    return {
      schema_version: 1,
      status: 'local_plan_created',
      created_at_utc: new Date().toISOString(),
      experience: catalog.experience,
      category_id: catalog.category_id,
      canonical_agent_ids: [...(catalog.canonical_agent_ids || [])],
      topic: {id: topic.id, title: topic.title || topic.id},
      mode,
      recipe: recipe ? {id: recipe.id, name: recipe.title} : null,
      preferences: {diet, exclude_allergens: []},
      role_handoff: [
        {role: 'Vyomaraj', implementation: 'deterministic_local_planner',
          action: 'Validated pack, topic, mode and recipe preferences; prepared category route.'},
        {role: 'Jarvis', implementation: 'deterministic_local_handoff',
          action: 'Attached evidence, mapping gaps and approval checklist; no external execution.'},
      ],
      source_references: sourceReferences,
      review_gates: reviewGates,
      provider: null,
      ai_calls_made: false,
      publishing_enabled: false,
      legacy_device_config_loaded: false,
      production_deployed: false,
      dr_sync_verified: false,
      chapter_mapping_status: 'proposed_not_recovered_original_titles',
    };
  }

  return Object.freeze({buildPlan});
});
