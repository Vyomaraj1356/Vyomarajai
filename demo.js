'use strict';
const $ = id => document.getElementById(id);
let lastPlan = null;
const recipeOptions = {
  bhakti: [{id: 'fruit', label: 'Fruit offering (illustrative)'}, {id: 'coconut', label: 'Coconut offering (illustrative)'}, {id: 'yogurt', label: 'Yogurt offering (illustrative)'}],
  'liquor-bar': [{id: 'chana', label: 'Chana snack (illustrative)'}]
};
function option(label, value) {
  const node = document.createElement('option');
  node.textContent = label; node.value = value;
  return node;
}
function setStatus(message, state) {
  $('plan-status').textContent = message;
  $('plan-status').dataset.state = state || 'info';
}
function updateRecipes() {
  const select = $('recipe-id');
  const previous = select.value;
  const experience = $('experience').value;
  const recipes = catalogData && catalogData.experience === experience
    ? catalogData.items.filter(item => item.kind === 'recipe').map(item => ({id: item.id, label: `${item.title} (illustrative)`}))
    : recipeOptions[experience] || [];
  select.replaceChildren(option('No recipe', ''));
  for (const recipe of recipes) select.append(option(recipe.label, recipe.id));
  if (previous && recipes.some(recipe => recipe.id === previous)) select.value = previous;
}
let catalogData = null;
let catalogRequestId = 0;
function readableStatus(value) {
  return String(value || 'not recorded').replaceAll('_', ' ');
}
function catalogCard(item) {
  const card = document.createElement('article'); card.className = 'content-card';
  const eyebrow = document.createElement('p'); eyebrow.className = 'eyebrow'; eyebrow.textContent = item.section || 'Content';
  const title = document.createElement('h3'); title.textContent = item.title || item.id || 'Untitled entry';
  const state = document.createElement('span'); state.className = 'content-state';
  state.textContent = `Review state: ${readableStatus(item.content_status)}`;
  const description = document.createElement('p');
  description.textContent = item.description || 'No descriptive summary is recorded for this entry.';
  card.append(eyebrow, title, state, description);
  if (Array.isArray(item.metadata) && item.metadata.length) {
    const metadata = document.createElement('ul'); metadata.className = 'content-metadata';
    for (const value of item.metadata) {
      const row = document.createElement('li'); row.textContent = value; metadata.append(row);
    }
    card.append(metadata);
  }
  if ((item.ingredients || []).length || (item.allergens || []).length || (item.steps || []).length) {
    const details = document.createElement('details'); details.className = 'ingredient-notes';
    const summary = document.createElement('summary'); summary.textContent = 'Preparation, ingredients and allergy notes'; details.append(summary);
    if ((item.steps || []).length) {
      const heading = document.createElement('strong'); heading.textContent = 'Preparation notes'; details.append(heading);
      const list = document.createElement('ol');
      for (const value of item.steps) { const row = document.createElement('li'); row.textContent = value; list.append(row); }
      details.append(list);
    }
    if ((item.ingredients || []).length) {
      const heading = document.createElement('strong'); heading.textContent = 'Ingredients'; details.append(heading);
      const list = document.createElement('ul');
      for (const value of item.ingredients) { const row = document.createElement('li'); row.textContent = value; list.append(row); }
      details.append(list);
    }
    const heading = document.createElement('strong'); heading.textContent = 'Allergens'; details.append(heading);
    const list = document.createElement('ul');
    for (const value of item.allergens || []) { const row = document.createElement('li'); row.textContent = value; list.append(row); }
    if (!(item.allergens || []).length) { const row = document.createElement('li'); row.textContent = 'None listed in this local record; this is not a safety guarantee.'; list.append(row); }
    details.append(list); card.append(details);
  }
  const references = Array.isArray(item.source_references) ? item.source_references : [];
  const sourceHeading = document.createElement('h4'); sourceHeading.textContent = 'Source references'; card.append(sourceHeading);
  if (references.length) {
    const list = document.createElement('ul'); list.className = 'source-list';
    for (const reference of references) {
      const row = document.createElement('li');
      const name = reference.title || reference.id || 'Source';
      if (typeof reference.url === 'string') {
        try {
          const url = new URL(reference.url);
          if (url.protocol === 'https:' || url.protocol === 'http:') {
            const link = document.createElement('a'); link.textContent = name; link.href = url.href;
            link.target = '_blank'; link.rel = 'noopener noreferrer'; row.append(link);
          } else row.textContent = name;
        } catch (_) { row.textContent = name; }
      } else row.textContent = name;
      list.append(row);
    }
    card.append(list);
  } else {
    const noSource = document.createElement('p'); noSource.className = 'no-source';
    noSource.textContent = 'No linked source is recorded for this entry yet.'; card.append(noSource);
  }
  return card;
}
function renderCatalog() {
  const grid = $('catalog-grid'); grid.replaceChildren();
  if (!catalogData) return;
  const query = $('catalog-search').value.trim().toLocaleLowerCase();
  const items = (catalogData.items || []).filter(item => {
    const text = [item.title, item.section, item.description, ...(item.metadata || []),
      ...(item.ingredients || []), ...(item.allergens || [])].join(' ').toLocaleLowerCase();
    return !query || text.includes(query);
  });
  if (!items.length) {
    const empty = document.createElement('p'); empty.className = 'catalog-empty';
    empty.textContent = query ? 'No local entries match that filter.' : 'This local pack contains no entries to display.';
    grid.append(empty);
  } else for (const item of items) grid.append(catalogCard(item));
  $('catalog-status').textContent = `${items.length} of ${catalogData.item_count} entries shown · ${catalogData.source_reference_count} distinct source references in this pack.`;
  const meta = $('catalog-meta'); meta.replaceChildren(
    addSummary('Local pack', catalogData.title),
    addSummary('Pack state', readableStatus(catalogData.content_pack_status)),
    addSummary('Pack date', catalogData.updated),
    addSummary('Visible entries', `${items.length} / ${catalogData.item_count}`),
  );
  const gates = $('catalog-gates'); gates.replaceChildren();
  for (const note of catalogData.review_gates || []) {
    const item = document.createElement('li'); item.textContent = note; gates.append(item);
  }
}
async function loadCatalog() {
  const requestId = ++catalogRequestId;
  const experience = $('catalog-experience').value;
  catalogData = null;
  $('catalog-grid').replaceChildren(); $('catalog-meta').replaceChildren(); $('catalog-gates').replaceChildren();
  $('catalog-status').textContent = 'Loading the checked-in local content pack…';
  try {
    const response = await fetch('./demo-catalog.json', {cache: 'no-store'});
    const result = await response.json();
    if (requestId !== catalogRequestId) return;
    if (!response.ok) throw new Error('The static content catalog could not be loaded.');
    const pack = result.packs && result.packs[experience];
    if (!pack || pack.experience !== experience) throw new Error('This content pack is not present in the static export.');
    catalogData = pack;
    updateRecipes();
    renderCatalog();
  } catch (error) {
    if (requestId !== catalogRequestId) return;
    $('catalog-status').textContent = `Local catalog unavailable: ${error.message}`;
  }
}
function addSummary(label, value) {
  const box = document.createElement('div'); box.className = 'summary-item';
  const caption = document.createElement('span'); caption.textContent = label;
  const text = document.createElement('strong'); text.textContent = String(value ?? '—');
  box.append(caption, text); return box;
}
function renderPlan(plan) {
  lastPlan = plan;
  const summary = $('plan-summary'); summary.replaceChildren(
    addSummary('Status', plan.status),
    addSummary('Experience / category', `${plan.experience} / ${plan.category_id}`),
    addSummary('Topic', plan.topic?.title || plan.topic?.id),
    addSummary('Provider / AI calls', `${plan.provider ?? 'none'} / ${plan.ai_calls_made}`),
    addSummary('Publication', plan.publishing_enabled ? 'enabled' : 'not enabled'),
    addSummary('Production', plan.production_deployed ? 'deployed' : 'not deployed'),
  );
  const sources = $('sources'); sources.replaceChildren();
  for (const source of plan.source_references || []) {
    const item = document.createElement('li');
    const name = source.title || source.name || source.id || 'Reference';
    const url = source.url || source.source_url;
    if (typeof url === 'string') {
      try {
        const parsed = new URL(url);
        if (parsed.protocol === 'https:' || parsed.protocol === 'http:') {
          const link = document.createElement('a');
          link.textContent = name; link.href = parsed.href;
          link.target = '_blank'; link.rel = 'noopener noreferrer'; item.append(link);
        } else item.textContent = name;
      } catch (_) { item.textContent = name; }
    } else item.textContent = name;
    sources.append(item);
  }
  if (!sources.children.length) sources.append(Object.assign(document.createElement('li'), {textContent: 'No source references in this plan.'}));
  const gates = $('gates'); gates.replaceChildren();
  for (const gate of plan.review_gates || []) {
    const item = document.createElement('li'); item.textContent = gate; gates.append(item);
  }
  $('plan-json').textContent = JSON.stringify(plan, null, 2);
  $('result').hidden = false;
  $('result').scrollIntoView({behavior: 'smooth', block: 'start'});
}
$('experience').addEventListener('change', () => {
  updateRecipes();
  if ($('catalog-experience').value !== $('experience').value) {
    $('catalog-experience').value = $('experience').value;
    loadCatalog();
  }
});
$('catalog-experience').addEventListener('change', () => {
  $('experience').value = $('catalog-experience').value;
  updateRecipes();
  loadCatalog();
});
$('catalog-search').addEventListener('input', renderCatalog);
$('plan-form').addEventListener('submit', async event => {
  event.preventDefault();
  const button = $('plan-button'); button.disabled = true;
  $('result').hidden = true;
  const body = {
    experience: $('experience').value,
    topic_id: $('topic-id').value.trim() || 'overview',
    mode: $('mode').value,
    diet: $('diet').value,
  };
  if ($('recipe-id').value) body.recipe_id = $('recipe-id').value;
  setStatus('Building a deterministic plan in this browser. No provider or external service is being called…', 'info');
  try {
    if (!catalogData || catalogData.experience !== body.experience) {
      throw new Error('Wait for the selected local content pack to finish loading.');
    }
    const result = window.VyomarajDemoPlanner.buildPlan(body, catalogData);
    renderPlan(result);
    setStatus('Browser-local plan created. Nothing was sent or saved; it was not published or deployed.', 'success');
  } catch (error) {
    setStatus(`Planner unavailable: ${error.message}`, 'error');
  } finally {
    button.disabled = false;
  }
});
$('copy-json').addEventListener('click', async () => {
  if (!lastPlan) return;
  try {
    await navigator.clipboard.writeText(JSON.stringify(lastPlan, null, 2));
    $('copy-json').textContent = 'Copied';
    setTimeout(() => {$('copy-json').textContent = 'Copy JSON';}, 1200);
  } catch (_) {
    setStatus('Clipboard permission is unavailable in this browser; expand the JSON view and copy manually.', 'error');
  }
});
updateRecipes();
loadCatalog();
