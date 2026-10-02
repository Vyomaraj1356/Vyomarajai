(() => {
  "use strict";

  const PATHS = {
    config: "ops/vyomaraj-core/experience/EXPERIENCE_ORCHESTRATOR.json",
    catalog: "ops/vyomaraj-core/experience/CONTENT_CATALOG.json",
    registry: "ops/vyomaraj-core/handover/AGENT_CONTENT_REGISTRY_V16_7_24.json",
    policy: "ops/vyomaraj-core/handover/CONTENT_SAFETY_POLICY_V16_7_24.json"
  };

  const state = { config: null, catalog: null, registry: null, policy: null, currentPlan: null };
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const el = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };

  async function loadJson(path) {
    const response = await fetch(path, { credentials: "same-origin", cache: "no-store" });
    if (!response.ok) throw new Error(`Could not load ${path} (${response.status}).`);
    return response.json();
  }

  function setStatus(message, isError = false) {
    const status = $("#system-status");
    status.textContent = message;
    status.classList.toggle("status-error", isError);
  }

  async function init() {
    try {
      [state.config, state.catalog, state.registry, state.policy] = await Promise.all([
        loadJson(PATHS.config),
        loadJson(PATHS.catalog),
        loadJson(PATHS.registry),
        loadJson(PATHS.policy)
      ]);
      renderAll();
      setStatus("ROUTE MAP LOADED · EXECUTION OFF");
      const totals = state.registry.totals || {};
      const adapters = state.config.tool_adapters || [];
      $("#stat-line").textContent = `${totals.main_agents ?? 13} categories · ${totals.sub_agents ?? 133} sub-agents · ${adapters.length} adapters disabled`;
      $("#policy-status").textContent = state.policy.status || "Policy status not stated in source.";
      bindForm();
    } catch (error) {
      setStatus("SYSTEM MAP UNAVAILABLE", true);
      $("#form-message").textContent = error.message || "Could not load the local registry files.";
      $("#form-message").classList.add("error-text");
      $("#job-form").querySelectorAll("button, input, select, textarea").forEach((control) => { control.disabled = true; });
    }
  }

  function renderAll() {
    renderDomainSelect();
    renderModeSelect();
    renderOutputOptions();
    renderContentPackOptions();
    renderAgentDirectory();
    renderContentCatalog();
    renderAdapters();
    renderConfigurations();
  }

  function renderDomainSelect() {
    const select = $("#job-domain");
    select.replaceChildren();
    (state.config.domain_routes || []).forEach((route) => {
      const option = el("option", "", route.label);
      option.value = route.id;
      select.append(option);
    });
  }

  function renderModeSelect() {
    const select = $("#experience-mode");
    select.replaceChildren();
    Object.entries(state.config.experience_modes || {}).forEach(([id, mode]) => {
      const option = el("option", "", mode.label);
      option.value = id;
      select.append(option);
    });
  }

  function renderOutputOptions() {
    const wrap = $("#output-options");
    wrap.replaceChildren();
    Object.entries(state.config.outputs || {}).forEach(([id, output]) => {
      const label = el("label", "option-card");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.name = "requested_outputs";
      input.value = id;
      const copy = el("span");
      copy.append(el("strong", "", output.label));
      const required = (output.required_adapters || []).map((toolId) => adapterLabel(toolId)).join(" · ");
      copy.append(el("small", "", required || "No adapter requirement stated"));
      label.append(input, copy);
      wrap.append(label);
    });
    applyModeDefaults();
  }

  function renderContentPackOptions() {
    const wrap = $("#content-pack-options");
    wrap.replaceChildren();
    (state.catalog.packs || []).forEach((pack) => {
      const label = el("label", "content-pack-option");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.name = "content_pack_ids";
      input.value = pack.id;
      const copy = el("span");
      copy.append(el("strong", "", pack.label));
      copy.append(el("small", "", `${pack.module_count} filenames · metadata only`));
      label.append(input, copy);
      wrap.append(label);
    });
    applyRecommendedPacks();
  }

  function applyModeDefaults() {
    const modeId = $("#experience-mode").value;
    const defaults = (state.config.experience_modes[modeId] || {}).default_outputs || [];
    $$("input[name='requested_outputs']").forEach((input) => { input.checked = defaults.includes(input.value); });
  }

  function applyRecommendedPacks() {
    const route = (state.config.domain_routes || []).find((item) => item.id === $("#job-domain").value);
    const categoryIds = new Set((route && route.category_ids) || []);
    $$("input[name='content_pack_ids']").forEach((input) => {
      const pack = (state.catalog.packs || []).find((item) => item.id === input.value);
      input.checked = Boolean(pack && (pack.category_ids || []).some((id) => categoryIds.has(id)));
    });
  }

  function renderAgentDirectory() {
    const totals = state.registry.totals || {};
    const categories = state.registry.categories || [];
    const namedRosters = Object.keys(state.registry.rosters || {}).length;
    const summary = $("#agent-summary");
    summary.replaceChildren();
    [
      [totals.main_agents ?? categories.length, "Main categories"],
      [totals.sub_agents ?? categories.reduce((sum, item) => sum + (item.sub_agents || 0), 0), "Sub-agent slots"],
      [totals.products ?? categories.reduce((sum, item) => sum + (item.products || 0), 0), "Product count"],
      [namedRosters, "Roster details supplied"]
    ].forEach(([number, label]) => {
      const tile = el("div", "summary-tile");
      tile.append(el("strong", "", number), el("span", "", label));
      summary.append(tile);
    });

    const grid = $("#agent-grid");
    grid.replaceChildren();
    categories.forEach((category) => {
      const card = el("article", "agent-card");
      const head = el("div", "agent-card-head");
      const copy = el("div");
      copy.append(el("div", "agent-id", category.id));
      copy.append(el("div", "agent-desc", category.description));
      const counts = el("div", "agent-counts");
      counts.append(countBadge(category.sub_agents, "agents"), countBadge(category.products, "products"));
      head.append(copy, counts);
      card.append(head);
      card.append(el("div", "roster-status", category.named_roster_status || "Individual names not supplied."));
      const roster = (state.registry.rosters || {})[category.id];
      if (roster !== undefined) {
        const details = el("details", "roster-details");
        const summary = el("summary", "", "View supplied roster details");
        details.append(summary, buildRosterBody(category.id, roster));
        card.append(details);
      }
      grid.append(card);
    });
  }

  function countBadge(value, label) {
    const badge = el("div", "agent-count");
    badge.append(el("strong", "", value), el("span", "", label));
    return badge;
  }

  function buildRosterBody(categoryId, roster) {
    const body = el("div", "roster-body");
    if (Array.isArray(roster)) {
      const list = el("ul");
      roster.forEach((name) => list.append(el("li", "", name)));
      body.append(list);
      return body;
    }
    if (!roster || typeof roster !== "object") {
      body.append(el("p", "", "No individual roster detail supplied."));
      return body;
    }
    if (Array.isArray(roster.entries)) {
      const list = el("ul");
      roster.entries.forEach((entry) => {
        const item = el("li");
        const slot = el("strong", "", `${entry.slot || "Slot"} · `);
        item.append(slot, document.createTextNode(entry.name || "Name not supplied"));
        list.append(item);
      });
      body.append(list);
      if (roster.note) body.append(el("p", "", roster.note));
      return body;
    }
    if (Array.isArray(roster.groups)) {
      roster.groups.forEach((group) => {
        const section = el("div", "roster-group");
        const ids = group.ids || "Supplied group";
        const count = group.count === undefined ? "" : ` · ${group.count} slots`;
        section.append(el("p", "roster-group-title", `${ids}${count}`));
        if (Array.isArray(group.names) && group.names.length) {
          const list = el("ul");
          group.names.forEach((name) => list.append(el("li", "", name)));
          section.append(list);
        } else {
          section.append(el("p", "", "Slot count supplied; individual names not supplied."));
        }
        body.append(section);
      });
      if (roster.count_check) body.append(el("p", "", `Source count check: ${roster.count_check}`));
      return body;
    }
    if (Array.isArray(roster.lanes)) {
      const list = el("ul");
      roster.lanes.forEach((lane) => list.append(el("li", "", lane)));
      list.append(el("li", "route-unmapped", `${roster.unmapped_slot_count || 1} UNMAPPED slot · ID not supplied`));
      body.append(list);
      if (roster.note) body.append(el("p", "", roster.note));
      return body;
    }
    body.append(el("p", "", `${categoryId}: roster details exist but have no recognized named-list structure.`));
    return body;
  }

  function renderContentCatalog() {
    const grid = $("#content-grid");
    grid.replaceChildren();
    (state.catalog.packs || []).forEach((pack) => {
      const card = el("article", "content-card");
      const top = el("div", "content-card-top");
      const identity = el("div");
      identity.append(el("h3", "", pack.label), el("code", "", pack.path));
      top.append(identity, el("span", "file-count", pack.module_count));
      card.append(top);
      const list = el("ul", "file-list");
      (pack.files || []).forEach((filename) => list.append(el("li", "", filename)));
      card.append(list);
      card.append(el("p", "", `${(pack.category_ids || []).join(" · ") || "Cross-cutting configuration"} · ${pack.review_before_external_use ? "Review before external use" : "No external use configured"}`));
      grid.append(card);
    });

    const readiness = state.registry.content_readiness || {};
    const note = $("#readiness-note");
    note.replaceChildren();
    const values = [
      `Registry reports ${readiness.active_content_products_reported ?? "—"} active-content products, ${readiness.placeholder_videos_shared ?? "—"} placeholder videos shared, ${readiness.pending_products_requiring_chapters ?? "—"} pending products requiring chapters, and ${readiness.planned_products_requiring_chapters ?? "—"} planned products requiring chapters.`
    ];
    note.append(el("strong", "", "Separate readiness report — not reconciled: "), document.createTextNode(`${values[0]} ${readiness.reconciliation_status || ""}`));
  }

  function renderAdapters() {
    const icons = { image_generation: "▧", video_generation: "▷", model_3d_generation: "◇", animation: "↗", rendering: "◉", ar_runtime: "⌖", trend_source: "⌁", publisher: "⇧" };
    const grid = $("#adapter-grid");
    grid.replaceChildren();
    (state.config.tool_adapters || []).forEach((adapter) => {
      const card = el("article", "adapter-card");
      card.append(el("span", "adapter-icon", icons[adapter.id] || "·"));
      card.append(el("h3", "", adapter.label));
      const detail = adapter.status === "manual_reference_only"
        ? "Manual reference only; no live trend fetch."
        : adapter.status === "configured" && adapter.execution_enabled
          ? "Configured adapter metadata; visual dispatch still requires an executor."
          : "Provider / endpoint not supplied; execution disabled.";
      card.append(el("p", "", detail));
      card.append(el("span", "adapter-state", adapterStatusLabel(adapter)));
      grid.append(card);
    });
  }

  function renderConfigurations() {
    const audit = state.config.existing_configuration_audit || {};
    const grid = $("#configuration-grid");
    grid.replaceChildren();
    const systems = [
      { id: "vyomaraj", label: "Vyomaraj", data: audit.vyomaraj },
      { id: "jarvis", label: "Jarvis", data: audit.jarvis }
    ];
    systems.forEach((system) => {
      const card = el("article", "configuration-card");
      card.append(el("p", "micro-label", `${system.id.toUpperCase()} · EXISTING REPOSITORY CONFIG`));
      card.append(el("h3", "", system.label));
      const list = el("ul", "configuration-list");
      const data = system.data || {};
      if (system.id === "vyomaraj") {
        list.append(configListItem("Canonical agent registry", data.canonical_registry));
        (data.bootstrap_scripts || []).forEach((item) => {
          list.append(configListItem(item.layout, `${item.path} · ${item.status}`));
        });
        list.append(configListItem("Bootstrap execution", data.bootstrap_execution_status));
      } else {
        Object.entries(data).forEach(([key, item]) => {
          if (key === "review_note") return;
          const label = key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
          if (item && typeof item === "object") list.append(configListItem(label, `${item.path} · ${item.status}`));
          else list.append(configListItem(label, item));
        });
      }
      card.append(list);
      const note = system.data && system.data.review_note;
      if (note) card.append(el("p", "configuration-note", note));
      grid.append(card);
    });
    const sync = el("article", "configuration-card sync-card");
    sync.append(el("p", "micro-label", "CROSS-SYSTEM · CONNECTIVITY"));
    sync.append(el("h3", "", "No live bridge claimed"));
    sync.append(el("p", "configuration-note", audit.remote_agent_rpc_or_sync || "Remote agent RPC or sync status not configured."));
    if (audit.review_note) sync.append(el("p", "configuration-note", audit.review_note));
    grid.append(sync);
  }

  function configListItem(label, value) {
    const item = el("li", "");
    const key = el("strong", "", label);
    item.append(key, document.createTextNode(value === undefined || value === null ? "Not stated" : String(value)));
    return item;
  }

  function adapterStatusLabel(adapter) {
    if (adapter.status === "manual_reference_only") return "MANUAL ONLY";
    if (adapter.status === "configured" && adapter.execution_enabled) return "READY";
    if (adapter.status === "configured") return "DISPATCH DISABLED";
    return String(adapter.status || "not_configured").replaceAll("_", " ").toUpperCase();
  }

  function adapterLabel(id) {
    const found = (state.config.tool_adapters || []).find((item) => item.id === id);
    return found ? found.label : id;
  }

  function bindForm() {
    $("#experience-mode").addEventListener("change", applyModeDefaults);
    $("#job-domain").addEventListener("change", applyRecommendedPacks);
    $("#job-form").addEventListener("submit", (event) => {
      event.preventDefault();
      try {
        const input = readForm();
        const plan = buildPlan(input);
        state.currentPlan = plan;
        renderPlan(plan);
        $("#form-message").textContent = "Route plan built locally. No external tool or LLM was called.";
        $("#form-message").classList.remove("error-text");
      } catch (error) {
        $("#form-message").textContent = error.message || "Could not build the plan.";
        $("#form-message").classList.add("error-text");
      }
    });
    $("#download-plan").addEventListener("click", downloadPlan);
  }

  function readForm() {
    const title = $("#job-title").value.trim();
    const brief = $("#job-brief").value.trim();
    if (!title) throw new Error("Add a project title.");
    if (!brief) throw new Error("Add a short creative brief.");
    const requestedOutputs = $$("input[name='requested_outputs']:checked").map((input) => input.value);
    if (!requestedOutputs.length) throw new Error("Choose at least one output lane.");
    const trendSource = $("#trend-source").value.trim();
    if (trendSource && !validReferenceUrl(trendSource)) throw new Error("Trend reference must be an HTTP or HTTPS URL without credentials, query, or fragment; it will not be fetched.");
    return {
      title,
      brief,
      audience: $("#job-audience").value.trim(),
      domain_id: $("#job-domain").value,
      experience_mode: $("#experience-mode").value,
      trend_source: trendSource,
      trend_observed_at: $("#trend-date").value,
      publish_target: $("#publish-target").value.trim(),
      requested_outputs: requestedOutputs,
      content_pack_ids: $$("input[name='content_pack_ids']:checked").map((input) => input.value)
    };
  }

  function validReferenceUrl(value) {
    try {
      const parsed = new URL(value);
      return ["http:", "https:"].includes(parsed.protocol) && Boolean(parsed.hostname) && !parsed.username && !parsed.password && !parsed.search && !parsed.hash;
    } catch (_error) {
      return false;
    }
  }

  function buildPlan(job) {
    const domains = state.config.domain_routes || [];
    const domain = domains.find((item) => item.id === job.domain_id);
    if (!domain) throw new Error("Choose a listed experience domain.");
    const mode = state.config.experience_modes[job.experience_mode];
    if (!mode) throw new Error("Choose 3D, 4D, 5D, or AR.");

    const categoryIndex = new Map((state.registry.categories || []).map((category) => [category.id, category]));
    const categories = (domain.category_ids || []).map((id) => {
      const category = categoryIndex.get(id);
      if (!category) throw new Error(`Route references an unknown registry category: ${id}`);
      const roster = (state.registry.rosters || {})[id];
      return {
        id,
        description: category.description,
        sub_agents: category.sub_agents,
        products: category.products,
        named_roster_status: category.named_roster_status || "not stated",
        roster_detail: roster === undefined ? null : wrapRoster(id, roster)
      };
    });

    const outputs = state.config.outputs || {};
    const required = [];
    job.requested_outputs.forEach((outputId) => {
      const output = outputs[outputId];
      if (!output) throw new Error(`Unknown output lane: ${outputId}`);
      (output.required_adapters || []).forEach((adapterId) => { if (!required.includes(adapterId)) required.push(adapterId); });
    });
    (domain.required_adapter_ids || []).forEach((adapterId) => { if (!required.includes(adapterId)) required.push(adapterId); });
    if (job.trend_source && !required.includes("trend_source")) required.push("trend_source");
    if (job.publish_target && !required.includes("publisher")) required.push("publisher");

    const adapterIndex = new Map((state.config.tool_adapters || []).map((adapter) => [adapter.id, adapter]));
    const toolRoutes = required.map((id) => {
      const adapter = adapterIndex.get(id);
      if (!adapter) return { id, status: "unregistered", provider: null, execution_enabled: false };
      return { id, label: adapter.label, status: adapter.status, provider: adapter.provider ?? null, execution_enabled: Boolean(adapter.execution_enabled) };
    });

    const packIndex = new Map((state.catalog.packs || []).map((pack) => [pack.id, pack]));
    const selectedPacks = job.content_pack_ids.map((id) => {
      const pack = packIndex.get(id);
      if (!pack) throw new Error(`Unknown content pack: ${id}`);
      return {
        id,
        label: pack.label,
        path: pack.path,
        category_ids: pack.category_ids || [],
        files: pack.files || [],
        ingestion_mode: pack.ingestion_mode || "metadata_only_by_default",
        source_contents_loaded: false,
        review_before_external_use: pack.review_before_external_use !== false
      };
    });

    const adaptersReady = toolRoutes.length > 0 && toolRoutes.every((adapter) => adapter.execution_enabled && adapter.status === "configured");
    const policyStatus = state.policy.status || state.config.release_gates.policy_status;
    const riskTags = [...(domain.risk_tags || [])];
    const approvalGates = [
      "Owner/human review required before any public release.",
      "The source content-safety policy is a proposal, not a deployed moderation filter."
    ];
    if ((domain.mapping_status || "").includes("restricted_scope")) {
      approvalGates.push("Keep all war/arms content historical or fictional and non-operational; no functional weapon design or use instructions.");
    }
    if (riskTags.length) approvalGates.push(`Review applicable risk tags before creating or releasing assets: ${riskTags.join(", ")}.`);
    if (job.publish_target) approvalGates.push("Publishing requires a configured channel adapter and explicit owner approval; neither is granted by this plan.");

    const warnings = [];
    if (["owner_mapping_required", "provisional_composite_owner_review", "partial_roster_owner_review"].includes(domain.mapping_status)) warnings.push(domain.route_note);
    if (!job.trend_source) warnings.push("No trend source supplied; no live trend discovery or freshness claim is available.");
    else warnings.push("Trend reference is user-supplied and unverified; the planner does not fetch or validate it.");
    if (!adaptersReady) warnings.push("One or more required visual/tool adapters are not configured; this is a route plan, not generated media.");
    warnings.push("No visual-tool dispatch executor is implemented; this orchestrator emits plans only, even if an adapter is later configured.");
    if (policyStatus !== "deployed") warnings.push("Safety policy is not an operating filter; human review remains necessary.");
    if (!categories.length) warnings.push("No canonical specialist category is mapped; owner mapping is required before specialist assignment.");

    const readiness = state.registry.content_readiness || {};
    const totals = state.registry.totals || {};
    return {
      schema_version: 1,
      plan_id: randomId(),
      created_at_utc: new Date().toISOString(),
      status: "PLAN_ONLY_REQUIRES_HUMAN_REVIEW",
      execution_enabled: false,
      job: {
        title: job.title,
        domain_id: job.domain_id,
        domain_label: domain.label,
        experience_mode: job.experience_mode,
        experience_label: mode.label,
        brief: job.brief,
        audience: job.audience,
        requested_outputs: job.requested_outputs.map((id) => ({ id, label: outputs[id].label })),
        publish_target: job.publish_target
      },
      experience_definition: mode.definition,
      system_configuration_status: state.config.existing_configuration_audit || {},
      agent_route: {
        orchestrators: state.config.orchestrators || [],
        flow: state.config.agent_hierarchy.flow || [],
        mapping_status: domain.mapping_status,
        route_note: domain.route_note,
        categories,
        unknown_names_policy: state.config.agent_hierarchy.unknown_names_policy,
        execution_note: state.config.agent_hierarchy.execution_note
      },
      content_route: {
        catalog_scope: state.catalog.scope,
        selected_packs: selectedPacks,
        source_contents_loaded: false,
        source_contents_sent_to_llm_or_tools: false
      },
      trend: {
        source: job.trend_source || null,
        observed_at: job.trend_observed_at || null,
        verification_status: job.trend_source ? "owner_supplied_unverified" : "not_supplied",
        live_discovery_enabled: false,
        adaptation_rule: "Use as inspiration for new work; rights-check and do not copy protected source assets."
      },
      tool_routes: toolRoutes,
      adapter_configuration_status: adaptersReady ? "ready" : "incomplete",
      required_adapters_ready: adaptersReady,
      execution_status: "PLAN_ONLY_NO_VISUAL_TOOL_DISPATCH_EXECUTOR",
      llm: {
        status: state.config.llm.status || "provider_unconfigured",
        automatic_calls: false,
        provider_call_made: false,
        note: state.config.llm.note
      },
      safety: {
        source_policy_status: policyStatus,
        requires_human_review: true,
        risk_tags: riskTags,
        approval_gates: approvalGates,
        weapon_scope: state.config.release_gates.weapon_scope
      },
      publication: {
        requested: Boolean(job.publish_target),
        target: job.publish_target || null,
        status: job.publish_target ? "blocked_adapter_unconfigured_and_owner_approval_required" : "disabled_not_requested",
        publisher_configured: false,
        auto_publish: false
      },
      registry_snapshot: {
        release: state.registry.release,
        totals,
        content_readiness: readiness,
        content_readiness_reconciliation_status: readiness.reconciliation_status
      },
      warnings
    };
  }

  function wrapRoster(categoryId, roster) {
    if (Array.isArray(roster)) return { shape: "named_list_as_supplied", items: roster };
    if (roster && typeof roster === "object") {
      if (Array.isArray(roster.entries)) return { shape: "partial_entries_as_supplied", ...roster };
      if (Array.isArray(roster.groups)) return { shape: "grouped_roster_as_supplied", ...roster };
      if (Array.isArray(roster.lanes)) return { shape: "partial_lanes_as_supplied", ...roster };
      return { shape: "source_object_as_supplied", ...roster };
    }
    return { shape: "unknown", category_id: categoryId };
  }

  function randomId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
    return `plan-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
  }

  function renderPlan(plan) {
    $("#plan-empty").hidden = true;
    $("#plan-result").hidden = false;
    $("#plan-state").textContent = "PLAN READY · REVIEW REQUIRED";
    $("#plan-state").classList.add("ready");
    const summary = $("#plan-summary");
    summary.replaceChildren(
      el("strong", "", plan.job.title),
      el("p", "", `${plan.job.domain_label} · ${plan.job.experience_label} · PLAN ONLY · ${plan.publication.requested ? "PUBLISH BLOCKED" : "PUBLISH OFF"}`)
    );
    const warningList = $("#plan-warnings");
    warningList.replaceChildren();
    plan.warnings.forEach((warning) => warningList.append(el("li", "", warning)));

    const chain = $("#route-chain");
    chain.replaceChildren();
    const names = ["Vyomaraj", "Jarvis"];
    plan.agent_route.categories.forEach((category) => names.push(category.id));
    if (!plan.agent_route.categories.length) names.push("OWNER MAPPING REQUIRED");
    names.push("HUMAN REVIEW");
    names.forEach((name, index) => {
      if (index) chain.append(el("span", "route-arrow", "→"));
      const node = el("span", `route-node${name.includes("MAPPING") ? " route-unmapped" : ""}`, name);
      chain.append(node);
    });

    const tools = $("#plan-tools");
    tools.replaceChildren();
    if (!plan.tool_routes.length) tools.append(el("p", "muted-copy", "No output adapters requested."));
    plan.tool_routes.forEach((tool) => {
      const row = el("div", "plan-tool");
      row.append(el("span", "", tool.label || tool.id));
      row.append(el("span", "", adapterStatusLabel(tool)));
      tools.append(row);
    });
    $("#plan-gate").textContent = plan.safety.approval_gates.join(" ");
    $("#plan-json").textContent = JSON.stringify(plan, null, 2);
    $("#plan-panel")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function downloadPlan() {
    if (!state.currentPlan) return;
    const blob = new Blob([JSON.stringify(state.currentPlan, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${slug(state.currentPlan.job.title)}-route-plan.json`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  function slug(value) {
    return String(value).toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 48) || "experience";
  }

  document.addEventListener("DOMContentLoaded", init);
})();
