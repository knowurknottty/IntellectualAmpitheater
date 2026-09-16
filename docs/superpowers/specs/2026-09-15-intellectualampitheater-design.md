# IntellectualAmpitheater — Architecture and Product Design

**Status:** design approved in-chat as architecture A; implementation not yet authorized by the written-spec review gate  
**Product name:** IntellectualAmpitheater  
**Short name:** IntelAMP  
**Owner:** Inversion Labs  
**Date:** 2026-09-15 (US Central)  
**Design decision:** Inversion-native shell with clean upstream adapters

## 1. Mission

IntellectualAmpitheater is a local-first, internally hosted multi-model workbench that combines the strongest interaction patterns of multi-chat products with the extensibility of self-hosted AI platforms, while adding explicit context topology, provider-capability transparency, provenance, replay, and independence-aware consensus.

The user goal is simple:

> Put the right models, context, tools, and evidence in the same room, see exactly what each seat saw and did, compare them without laundering correlated answers into false certainty, and keep control of every consequential action.

The product is not an Open WebUI skin, not a ChatHub fork, and not a generic provider router. Upstream projects are reference implementations or separately identified services. IntelAMP owns its shell, data model, interaction model, and product identity.

## 2. Success criteria

A first production-grade internal release is successful when all of the following are true:

1. One prompt can be dispatched to at least six independently configured seats without coupling the UI to any one provider.
2. Each seat can bind a local or remote model, its own context view, tool policy, and response settings.
3. A user can add/remove/reorder seats without restarting the app.
4. Streaming responses remain isolated: one provider failure does not destroy successful sibling results.
5. Every dispatch yields a durable receipt that records model/provider identity, context/evidence lineage, timing, token/cost data when available, and terminal state.
6. The UI reveals provider capability loss before dispatch instead of silently degrading unsupported controls.
7. A conversation can branch and later be compared or merged without copy/paste.
8. A frozen run can be replayed against another model or configuration and produce a structured diff.
9. Tool Shadow Mode can collect proposed tool calls without executing side effects.
10. CAPT can remain the authority boundary for governed execution; IntelAMP never manufactures approval.
11. The False-Consensus Firewall can explain why apparent agreement may be less independent than the pane count suggests.
12. The core application remains useful with no cloud provider configured.
13. No required capability is hidden behind a paywall inside the Inversion Labs deployment.
14. Accessibility, responsive behavior, cancellation, export, deletion, and provider replacement are first-class acceptance criteria, not polish.
15. A maintained parity ledger accounts for every documented paid-tier capability in the reference products as `native`, `adapted`, `superior_replacement`, `intentionally_excluded`, or `unverified`; no parity claim is inferred from resemblance.

## 3. Explicit non-goals for the first implementation tranche

- Reimplement every Open WebUI subsystem before a usable IntelAMP exists.
- Copy GPL ChatHub source into the proprietary/independently licensed IntelAMP core.
- Remove or alter Open WebUI branding inside an Open WebUI deployment in violation of its license.
- Promise numerical "independent vote equivalents" as scientific truth before a validated estimator exists.
- Let an LLM decide execution authority.
- Auto-fallback to a different model after provider failure unless the user explicitly configured that behavior.
- Build a social feed, engagement loop, streak system, or telemetry-driven retention layer.
- Treat provider-specific reasoning controls as interchangeable when they are not.
- Make the browser extension the primary product surface.
- Require a cloud account for local llama.cpp/MLX use.

## 4. Frozen upstream references

The initial architecture review froze these upstream default-branch references:

- `open-webui/open-webui` at `0a7c15832fb30b1903753e83f81dc7d27e5b0944`
- `grokify/chathub` at `bba9ae9fa631aaed1fa19fbc7bbd454aeffdc8d2`
- `chathub-dev/chathub` at `a7a2bd6e12050d6a39fcaf30868bdfd7ccf78f22`

License boundary at that review point:

- `grokify/chathub`: MIT.
- `chathub-dev/chathub`: GPLv3.
- Open WebUI: current project license includes an Open WebUI branding condition, with its stated exception for deployments/distributions at or below fifty end users in a rolling thirty-day period, plus permission/enterprise-license alternatives.

These facts are design inputs, not legal advice. The implementation must preserve upstream notices and re-check license state before any public distribution.

## 5. Architecture decision

### 5.1 Chosen approach

**Inversion-native shell + protocol adapters.**

IntelAMP owns:

- web shell and seat-grid interaction model;
- provider capability schema;
- conversation/thread DAG;
- context topology model;
- run receipts and replay format;
- independence ledger and consensus presentation;
- artifact/notebook UX;
- local persistence and export format;
- CAPT integration surface.

Upstream services integrate through explicit adapters. No upstream is treated as the product root.

### 5.2 Why this wins

Compared with forking Open WebUI, this costs more initial engineering but avoids inheriting a foreign information architecture and branding/license constraints as the center of the product.

Compared with a total clean-room reimplementation of everything, adapters retain mature capabilities where that is rational: Open WebUI can remain a separately identified service, and the MIT ChatHub MCP server can serve as a conversation transport/backend without becoming IntelAMP's canonical data model.

Compared with merging repositories, this preserves provenance and prevents incompatible licenses and architectural assumptions from becoming inseparable.

## 6. System topology

```text
┌────────────────────────────────────────────────────────────────────────┐
│                         IntellectualAmpitheater                        │
│                                                                        │
│  Seat Grid  Thread Graph  Notebook  Artifacts  Replay  Evidence       │
└───────────────────────────────┬────────────────────────────────────────┘
                                │ typed local API / streaming
┌───────────────────────────────▼────────────────────────────────────────┐
│                           IntelAMP Gateway                             │
│                                                                        │
│ Provider Registry       Capability Compiler       Dispatch Engine      │
│ Context Topology        Conversation DAG          Run Receipt Store    │
│ Tool Shadow             Replay Engine             Independence Ledger  │
│ Artifact Store          Usage Ledger              Export/Import        │
└──────────────┬────────────────┬────────────────┬───────────────────────┘
               │                │                │
        ┌──────▼─────┐   ┌──────▼─────┐   ┌─────▼────────────────┐
        │ Providers  │   │ CAPT       │   │ Sidecars / MCP       │
        │ local/cloud│   │ authority  │   │ Open WebUI, ChatHub  │
        └────────────┘   └────────────┘   └──────────────────────┘
```

The gateway is the product's semantic center. The browser is not allowed to hold provider secrets, perform privileged tool execution, or become the source of truth for receipts.

## 7. Proposed implementation stack

### Web application

- React + TypeScript + Vite.
- Tailwind CSS v4 for semantic-token styling.
- Radix primitives where accessible behavior saves real work; never ship default component styling.
- TanStack Router for explicit route ownership.
- Native `fetch` + event-stream/WebSocket client abstractions; avoid a second state framework until real complexity requires one.
- Component-level container queries for the seat grid and inspector panels.
- No SSR dependency in the first internal release: IntelAMP is primarily a local/hosted application, not a content site.

### Gateway

- Python 3.12+ with FastAPI/Starlette-style ASGI streaming.
- Pydantic models for provider, seat, receipt, replay, tool-plan, and capsule contracts.
- SQLite in WAL mode for structured local metadata and conversation/run state.
- Content-addressed artifact directory for binary/large outputs.
- OS keychain or existing secure provider credential store for secrets; no provider key is stored in the conversation database.
- Explicit migration system from day one.

### Why this split

CAPT and much of the local AI tooling are already Python-native, while the UI benefits from a focused React/TypeScript component model. The API boundary keeps either side replaceable and prevents frontend framework decisions from owning orchestration semantics.

## 8. Core domain model

### 8.1 Workspace

A workspace contains threads, provider definitions, seat presets, artifacts, and policy defaults. It does not contain raw provider secrets.

### 8.2 Thread and turn DAG

A thread is a directed acyclic graph of turns, not a flat transcript. A turn has:

- `turn_id`
- parent turn identity or identities
- author/seat identity
- content blocks
- attachment/artifact references
- context snapshot reference
- evidence roots
- timestamps
- optional run receipt

Branching creates a new child lineage. Merging creates an explicit merge turn with both parents. The UI never pretends a merge was part of the original history.

### 8.3 Seat

A seat is a user-visible model/work lane:

```text
seat_id
display_name
provider_id
model_id
provider_family
context_view_id
tool_policy_id
system_instruction_ref
generation_config
independence_mode
visibility_policy
```

A seat is not a CAPT vessel by default. It becomes a governed vessel only when CAPT's cohort/scheduler contract actually establishes that identity and evidence.

### 8.4 Context view

A context view is a deterministic selection rule over:

- thread history;
- user-selected notes/files;
- retrieval evidence;
- sibling outputs;
- tool results;
- branch ancestry;
- fixed system instructions.

The context topology matrix shows, per seat, exactly which classes are visible.

### 8.5 Run receipt

Every seat dispatch writes a receipt:

```text
run_id
thread_id
turn_parent
seat_id
provider_id
model_id
provider_family
request_digest
context_view_digest
evidence_root_digest
tool_policy_digest
started_at
first_token_at
completed_at
terminal_state
input_tokens?
output_tokens?
estimated_cost?
provider_request_id?
output_digest?
failure_class?
```

Unknown provider fields remain null. IntelAMP never fabricates token counts, cost, or model IDs.

## 9. Provider Registry and Capability Compiler

Provider interchangeability is a contract, not a UI dropdown.

Each adapter publishes a normalized capability record:

```text
streaming
system_messages
multimodal_input
image_output
tool_calling
parallel_tool_calls
structured_output
reasoning_control
temperature
top_p
seed
max_output_tokens
citations
web_search
file_upload
native_memory
context_window
usage_reporting
cancellation
```

Values are typed as `supported`, `unsupported`, `provider_default`, or `unknown`, with provider-specific metadata where necessary.

Before dispatch, the Capability Compiler compares requested behavior with actual adapter capabilities and emits:

- exact request mapping;
- lost/ignored controls;
- provider-native substitutions;
- hard incompatibilities;
- user-visible warnings.

No unsupported slider is silently accepted.

Initial real adapters should prioritize:

1. generic OpenAI-compatible HTTP/SSE;
2. llama.cpp OpenAI-compatible server;
3. CAPT RuntimeService adapter for governed model runs;
4. Open WebUI sidecar adapter where a capability is worth delegating;
5. MCP tool/server adapter.

Provider-specific adapters are added only when native features cannot be expressed faithfully through the generic protocol.

## 10. Multi-seat dispatch

The UI can request N seats, but the gateway owns request lifecycle.

Each run has:

- immutable dispatch snapshot;
- one cancellation token per seat;
- seat-isolated streaming state;
- terminal state per seat;
- durable partial output for interrupted runs;
- explicit retry lineage.

A failed seat does not erase successful siblings. A retry produces a new attempt linked to the same logical seat/run objective.

No automatic model substitution occurs unless a user-authored policy explicitly permits it.

CAPT cohorts are separate from ordinary seat dispatch. If a task claims vessel independence, CAPT's governed scheduler/council surface must provide the required identity and capacity evidence. IntelAMP does not fake that contract by parallel HTTP calls.

### 10.1 Backpressure, disconnect, and resume

Every streamed event carries a monotonically increasing per-run sequence number. The gateway durably records stream chunks before presenting a terminal `completed` state.

- A slow or disconnected browser must not force successful provider streams to be discarded.
- Browser reconnect requests resume from the last acknowledged sequence.
- If the durable event sequence contains a gap, the UI marks the run `stream_interrupted` or `indeterminate`; it never invents missing text or silently seals the run as complete.
- Per-seat buffers are bounded. When a provider can outpace persistence, backpressure is applied at the adapter boundary rather than allowing unbounded memory growth.
- Provider rate-limit and concurrency ceilings are adapter inputs to dispatch. Waiting seats remain visibly queued; they are not silently dropped.
- If a provider exposes no safe resume/reconcile mechanism, the receipt says so and a retry becomes a new attempt with lineage to the interrupted run.

These mechanics are transport reliability only. They do not establish epistemic independence between seats.

## 11. Context Topology Matrix

This is a first-class screen, not an advanced setting buried in JSON.

For each seat, the user can inspect and edit visibility of:

- system instruction;
- entire thread or selected branch;
- last N turns;
- user notebook;
- attached files;
- retrieved sources;
- sibling outputs;
- tool plans;
- tool results;
- prior synthesis.

Matrix cells have explicit states: `visible`, `hidden`, `summary_only`, `post_harvest`, `not_applicable`.

Blind comparison uses `post_harvest` for sibling output. The gateway enforces the rule when assembling prompts; the UI alone is not the guard.

Every compiled context view has a digest so later results can prove which topology generated them.

## 12. False-Consensus Firewall

### 12.1 Problem

Several panes agreeing is not equivalent to several independent confirmations. Model families, shared training lineages, identical evidence roots, shared system instructions, and sibling-output leakage can produce correlated answers.

### 12.2 V1 objective

V1 is an explainable structural independence audit, not a probability model.

It computes and displays a **correlation-risk profile** from observable lineage:

- same provider/model/family;
- identical context-view digest;
- evidence-source overlap;
- copied/reused prompt lineage;
- sibling-output visibility before harvest;
- shared tool-result roots;
- replay ancestry;
- explicit perspective-axis overlap.

Output examples:

```text
Agreement: 5 of 6 seats cluster on hypothesis A
Independence warning: HIGH
Reasons:
- 4 seats used the same evidence root
- 3 seats are the same model family
- 2 seats saw sibling output before finalizing
Independent dissent preserved: seat_05
```

V1 must not claim "2.3 independent votes" unless a separately validated estimator is later implemented. The structural ledger can expose a bounded qualitative status such as `LOW / MEDIUM / HIGH correlation risk` with reasons.

### 12.3 Decontamination actions

From the warning panel the user can request:

- rerun a seat blind to sibling answers;
- switch model family;
- change evidence root;
- remove a shared source;
- invert the leading assumption;
- assign an explicit falsification perspective;
- replay from the same frozen prompt with altered topology.

The decontamination action creates a new run; it never rewrites the original evidence.

## 13. Conversation Git

The product borrows Git's mental model without storing chat as Git objects.

User-visible actions:

- branch from any turn;
- name a branch;
- compare two branches;
- cherry-pick a turn/artifact into another branch;
- merge two branches through an explicit synthesis turn;
- inspect merge conflicts when instructions/evidence disagree;
- tag a checkpoint;
- export a branch as a ThreadCapsule.

The branch graph is visualized only when useful; normal chat remains simple.

## 14. Counterfactual Replay Lab

A replay snapshot freezes:

- user prompt;
- selected history/context view;
- evidence roots;
- tool policy;
- provider/model binding;
- generation controls;
- relevant adapter version.

A replay can change selected variables while retaining the rest.

Comparison output separates:

- wording-only changes;
- claim additions/removals;
- citation/evidence changes;
- proposed tool-call changes;
- latency/cost changes;
- terminal-state changes.

Replay never mutates the original run receipt.

## 15. Tool Shadow Mode

Tool Shadow Mode lets models propose actions without causing external effects.

Flow:

1. Adapter receives model tool-call proposal.
2. Gateway normalizes the call to a typed `ToolPlan`.
3. Policy marks it `shadow`.
4. Arguments, target, expected consequence class, and permission requirements are displayed.
5. Multiple seats may propose competing plans.
6. The user or CAPT chooses whether any plan proceeds to execution.
7. Execution receives a new receipt; the shadow proposal remains immutable.

A simulation is only shown when the tool itself has a real dry-run/read-only capability. IntelAMP must never fabricate a successful simulation.

## 16. CAPT integration

CAPT is an authority adapter, not just another provider.

IntelAMP may request governed CAPT operations, display approvals, and render resulting receipts, but it must preserve these distinctions:

`model request != human approval != model run != verification != task completion`

When CAPT requires an explicit human approval, IntelAMP surfaces the exact normalized prompt/request identity before approval.

IntelAMP cannot widen a CAPT workspace root, fabricate a capability, or fall back to raw execution when the governed route refuses the action.

CAPT cohort/vessel terminology appears in the UI only when the live RuntimeService contract proves a governed cohort exists.

## 17. Upstream integration boundaries

### Open WebUI

Treat Open WebUI as a separately identified service when used. Integration may consume stable documented APIs/protocols. Do not transplant source merely for convenience. Preserve attribution and re-check license/branding conditions before distribution.

Potential delegated capabilities:

- mature RAG connectors;
- web search providers;
- image/audio subsystems;
- enterprise auth if a future deployment needs it.

IntelAMP remains usable without Open WebUI.

### grokify/chathub

The MIT MCP server is a good interoperability backend. IntelAMP can implement a ChatHub adapter for save/read/search/append/delete conversation exchange while keeping ThreadCapsule as its richer canonical format.

### chathub-dev/chathub

Use as behavioral/UI prior art only in the core architecture. Do not copy GPL source into IntelAMP core. If a GPL-compatible distribution is intentionally created later, that is a separate product/legal decision.

## 18. ThreadCapsule format

ThreadCapsule is a portable, provider-neutral export.

Minimum contents:

```text
manifest.json
thread.jsonl
artifacts/
receipts/
evidence/
checksums.sha256
```

Manifest records schema version, export time, workspace/thread identity, branch root, and included artifact/receipt IDs.

Secrets are never included. Provider request IDs may be redacted by export policy.

A later optional signing layer can bind the checksum manifest, but signing is not required for the first tranche.

## 19. Notebook and artifact model

The notebook is not a second chat history. It contains user-curated durable material:

- notes;
- pinned model outputs;
- synthesized decisions;
- file references;
- reusable context snippets.

Artifacts are immutable blobs or versioned text outputs referenced by ID/digest. Editing a text artifact creates a new version.

Any artifact used in a run can be traced from the run receipt.

## 20. Privacy and sovereignty

Defaults:

- local database;
- local artifact store;
- no analytics or third-party telemetry;
- cloud providers opt in per seat/provider;
- secret values kept outside conversation storage;
- export and delete available directly from the current workspace;
- no retention mechanic designed to increase session frequency.

The UI exposes six verbs in one action from the main shell:

`inspect · refuse · leave · delete · export · replace`

"Replace" means change provider/model/tool without losing the thread.

## 21. UI/UX direction

### Design read

**Surface:** expert multi-model operating environment  
**Audience:** technically capable users who still need instant legibility  
**Mode:** OPERATE  
**CAPTURE:** 2/10  
**EXTRACTION:** 0  
**Arousal channel:** luminance only  
**Palette direction:** NIGHT TABLE

The application should feel like an instrument panel in a research theater, not a casino and not a generic AI dashboard.

### Core layout

Desktop:

- left rail: Workspaces, Threads, Arena, Notebook, Artifacts, Providers;
- top status strip: workspace, privacy/network state, active seats, total running jobs;
- center: adaptive seat grid;
- bottom: shared composer with target selector;
- right inspector: Context, Evidence, Receipts, Capability Loss, Replay.

Seat grid layouts: 1, 2, 3, 4, 6, and adaptive custom. The user can focus one seat without destroying the group.

Mobile:

- one focused seat at a time;
- explicit seat tab/selector with terminal-state summary;
- composer remains reachable;
- inspector becomes a sheet;
- no information is available only through hover or swipe.

### Visual system

Use NIGHT TABLE roles as a starting point:

- field `#0B0A0C`
- quiet `#1A1A1F`
- ink `#EDE7DD`
- dominant oxblood `#B3123A` as fill-only
- accent brass `#C9A227`
- reward `#46E0A0`
- alert `#FF5A36`

Max chroma belongs to the user's own current action, not a provider upsell.

Avoid purple/indigo AI gradients, glassmorphism, equal-card triads, decorative status dots, fake live counters, and motion without state meaning.

### Motion

- transform/opacity only for animated transitions;
- no looped attention recapture;
- reduced-motion path required;
- cancellation/stop is visually at least as prominent as start while a run is active.

## 22. Responsive and performance constraints

- Break where content breaks; do not force device-preset geometry.
- Seat cards use container queries.
- Use `100dvh`, never `100vh`, for full-height mobile shells.
- 44 px minimum touch targets on web.
- Input text remains at least 16 px on mobile.
- Virtualize long transcripts and artifact lists.
- Do not rerender all seats when one seat emits a token.
- Streaming state is partitioned per seat/run.
- AbortController/cancellation must propagate to adapters that support cancellation.
- Large artifacts never live only in React state.
- No barrel imports in performance-sensitive UI code.
- No global scroll listener for layout effects.

### 22.1 Device and resource profiles

High-end and low-end devices receive the same product capabilities. Only rendering strategy and optional visual richness may adapt.

- Core operation must not require WebGL, canvas particle systems, or GPU-heavy decorative effects.
- Offscreen transcripts are virtualized; an unfocused seat may batch Markdown re-rendering while streaming and performs a full render when it becomes focused or the run settles.
- Adaptive batching thresholds come from measured frame time and memory pressure, not hard-coded device marketing labels.
- Low-resource mode can be selected explicitly and is never framed as a lesser product tier.
- The app must remain fully keyboard-operable and readable when motion and decorative texture are disabled.
- Resource observations stay local and are reported as measured/derived values; they are not behavioral telemetry.
- Six-seat mode on a phone means one full seat plus a compact seat selector/status surface, not six unreadable columns.

The acceptance suite must include one constrained-browser run with CPU throttling and reduced viewport/memory pressure in addition to the primary desktop run.

## 23. Failure model

Failures are explicit typed states:

```text
provider_unavailable
provider_rate_limited
provider_timeout
provider_protocol_error
context_too_large
capability_mismatch
cancelled_by_user
tool_plan_refused
tool_execution_failed
capt_authority_refused
capt_approval_required
storage_error
stream_interrupted
unknown
```

Rules:

- preserve partial output;
- do not relabel timeout as model failure until reconciled where the provider/runtime supports reconciliation;
- no silent fallback;
- retries append lineage;
- provider credentials are never printed in failure diagnostics;
- one seat failure never invalidates successful sibling receipts.

## 24. Observability

IntelAMP records local operational telemetry necessary to explain its own behavior:

- run timings;
- queue time;
- TTFT;
- terminal state;
- token/cost fields when reported by provider;
- local resource observations when explicitly measured;
- adapter version;
- capability compile warnings.

This is product evidence, not behavioral analytics. It remains local unless the user exports it.

A status surface must distinguish `reported by provider`, `measured locally`, `derived`, and `unknown`.

## 25. Testing and verification strategy

### Contract tests

- schema validation for provider capability records;
- normalized request mapping;
- stream event parsing;
- cancellation semantics;
- error-class mapping;
- ThreadCapsule round-trip;
- receipt hashing/digest stability;
- conversation DAG branch/merge invariants;
- context-view digest stability;
- independence-ledger explanations.

### Real integration tests

The implementation must use real available providers for integration evidence rather than claiming success from fake provider stubs.

Initial acceptance matrix should include:

- local llama.cpp OpenAI-compatible server;
- at least one configured remote OpenAI-compatible provider;
- CAPT RuntimeService path when human approval is available;
- ChatHub MCP adapter if enabled.

If an integration cannot be run, it stays `UNVERIFIED`.

### UI verification

- desktop narrow/wide and phone widths;
- keyboard-only flow;
- visible focus;
- reduced motion;
- contrast;
- stream cancellation;
- one-seat and six-seat layouts;
- seat failure while siblings succeed;
- very long model names and translated strings;
- offline/local-only mode.

Before any UI is called shippable, run the project anti-slop firewall and the attention/safety gate from the active skill pack.

## 26. Licensing and provenance guard

The repository should maintain `THIRD_PARTY.md` and an upstream ledger.

CI must reject accidental imports/copies from the GPL ChatHub reference path into the IntelAMP core unless a separately approved GPL distribution plan exists.

Any direct use of MIT ChatHub code retains its copyright/license notice.

Open WebUI integration is treated as external/sidecar by default. Re-check its then-current license before public deployment or rebranding.

## 27. Security boundaries

- Browser never receives stored provider secrets.
- Gateway validates tool names and arguments before any execution path.
- Artifact paths are content-addressed or validated against workspace roots.
- Imported ThreadCapsules reject path traversal, symlinks, duplicate manifest members, and checksum mismatch.
- Markdown/HTML output is sanitized before rendering.
- Model-supplied URLs are not automatically fetched with ambient credentials.
- Tool Shadow Mode cannot mutate external state.
- CAPT authority errors are terminal for the governed route.
- No plugin obtains broader filesystem/network authority merely because another plugin has it.

## 28. Product feature matrix

### Baseline parity targets

IntelAMP maintains a capability-by-capability parity ledger against the documented Plus/Pro or equivalent paid feature envelopes of the reference products. The ledger is evidence-driven: each capability is classified as `native`, `adapted`, `superior_replacement`, `intentionally_excluded`, or `unverified`, with a witness for any state above `unverified`. Delivery is staged, but the ledger is exhaustive so "best of both worlds" cannot silently decay into a hand-picked subset.

The implementation target includes:

- multi-model simultaneous chat;
- local and remote providers;
- prompt library/presets;
- searchable local history;
- file/image inputs;
- Markdown/code/math rendering;
- web/RAG adapters;
- model/tool presets;
- MCP/OpenAPI-style tools;
- notes/notebook;
- persistent memory only when explicitly enabled;
- image/media adapters;
- usage/cost visibility;
- export/import/share;
- responsive mobile web;
- local-first self hosting.

### Inversion-native differentiators

1. Context Topology Matrix.
2. Provider Capability Compiler with visible loss analysis.
3. Conversation Git.
4. Counterfactual Replay Lab.
5. Tool Shadow Mode.
6. Compute Frontier and measured run receipts.
7. ThreadCapsules.
8. Epistemic Independence Ledger / False-Consensus Firewall.

The eighth is the flagship differentiator, but novelty claims remain research claims until a dedicated prior-art review is complete.

## 29. Compute Frontier

The app should help a user choose a dispatch strategy from measured constraints rather than pane count.

Per seat/run it can display:

- provider-reported price metadata when available;
- measured latency/TTFT;
- context headroom;
- local wall-clock/resource measurements when available;
- capability compatibility.

A future planner may answer requests such as "three distinct families under this cost ceiling," but it must use measured/provider-declared data and must label stale/unknown pricing.

## 30. Data migration and durability

Every persisted record includes a schema version.

Migrations are forward-only in normal operation and create a local backup/checkpoint before changing durable state.

Thread and artifact IDs are stable across export/import. Provider config IDs may be remapped on import because credentials are never exported.

Crash recovery should restore:

- completed receipts;
- partial stream content;
- thread branch state;
- user notebook state.

It must not invent a `completed` terminal state for an interrupted run.

## 31. Delivery tranches

### Tranche 0 — contract and shell

- repository/bootstrap;
- typed contracts;
- database migrations;
- semantic design tokens;
- provider registry;
- one real OpenAI-compatible adapter;
- local llama.cpp integration;
- one-seat and multi-seat streaming shell;
- durable run receipts.

### Tranche 1 — topology and comparison

- context topology matrix;
- seat presets;
- six-seat grid;
- capability compiler;
- failure isolation;
- branchable thread DAG;
- structured answer comparison.

### Tranche 2 — signature intelligence

- independence ledger;
- false-consensus warning/explanation;
- blind-harvest enforcement;
- decontamination reruns;
- counterfactual replay.

### Tranche 3 — governed action

- Tool Shadow Mode;
- CAPT authority adapter;
- approval rendering;
- selected plan execution with receipts;
- MCP tool/server integration.

### Tranche 4 — ecosystem parity

- ChatHub MCP interoperability;
- Open WebUI sidecar capabilities selected by measured value;
- notebook/artifact expansion;
- search/RAG/media integrations;
- broader import/export.

Each tranche must be independently usable. Later tranches cannot be used to excuse a broken earlier contract.

## 32. Acceptance evidence for the first internal release

A release candidate is not "done" until there is evidence for:

- exact source commit;
- clean intended diff;
- frontend typecheck/lint/build;
- backend tests;
- database migration test;
- real local-provider transcript;
- real remote-provider transcript if configured;
- six-seat mixed success/failure run;
- cancel-in-flight run;
- capability-loss warning example;
- branch/replay example;
- ThreadCapsule export/import round trip;
- false-consensus explanation example with preserved dissent;
- keyboard/accessibility pass;
- anti-slop firewall counts;
- attention/safety gate;
- residual `UNVERIFIED` list.

## 33. Key risks and mitigations

### Risk: scope explosion from "best of both worlds"

Mitigation: parity is a tracked capability matrix. IntelAMP builds the semantic core and signature differentiators first, then adapters expand breadth.

### Risk: false scientific precision in consensus scoring

Mitigation: V1 reports structural correlation risk and reasons. Numeric effective-vote claims are prohibited until validated.

### Risk: provider abstraction erases useful native features

Mitigation: capability compiler exposes provider-specific extensions and warns on loss rather than flattening everything to the lowest common denominator.

### Risk: license contamination

Mitigation: sidecar/adapter boundary, frozen upstream refs, `THIRD_PARTY.md`, no GPL source copied into core.

### Risk: multi-seat UI becomes unreadable on small devices

Mitigation: focused-seat mobile mode, explicit seat selector, inspector sheet, no six-column shrink-to-fit.

### Risk: CAPT gets reduced to decorative branding

Mitigation: CAPT owns governed authority where invoked. IntelAMP never calls ordinary parallel HTTP dispatch a CAPT cohort.

### Risk: local-first becomes "local UI, cloud brain"

Mitigation: local llama.cpp integration is a first-tranche acceptance requirement and the app remains usable with cloud credentials absent.

## 34. Open design decisions intentionally deferred to implementation planning

These are not ambiguous product requirements; they are implementation choices to benchmark or resolve during planning:

- exact migration library for SQLite;
- SSE versus WebSocket for the browser stream transport;
- exact local embedding/index implementation for semantic comparison;
- which Open WebUI capabilities provide enough value to justify sidecar integration first;
- whether ThreadCapsule signing belongs in the first public release or a later proof layer.

## 35. Design self-review checklist

Before implementation planning, confirm:

- no placeholder/TBD requirements;
- upstream boundaries and licenses are explicit;
- CAPT authority language is not blurred;
- ordinary seats are not called vessels;
- every novel feature has a testable behavior;
- false-consensus language avoids unsupported numerical precision;
- local-only operation is a real acceptance requirement;
- mobile behavior is specified;
- error states do not silently retry/substitute;
- UI doctrine uses EXTRACTION 0 and OPERATE CAPTURE 2;
- implementation can be decomposed into independently testable tranches.

## 36. Approval gate

This document captures the architecture-A decision. Per the active project workflow, implementation planning begins only after the human reviews this written specification and confirms it accurately represents the intended product.
