# IntelAMP capability parity ledger

Allowed classifications are exactly: `native`, `adapted`, `superior_replacement`, `intentionally_excluded`, `unverified`. Any classification above `unverified` needs a concrete witness. This ledger describes the current Tranche 0 branch, not planned marketing scope.

## Baseline parity targets

| Capability | State | Witness / reason |
| --- | --- | --- |
| Multi-model simultaneous chat | `native` | `backend/tests/test_dispatch.py`; `frontend/tests/composer.test.tsx`; `evidence/task5-two-seat-dispatch.md` |
| Local providers | `native` | `config/providers.example.toml`; `evidence/task4-local-llama.md` |
| Remote providers | `unverified` | Generic OpenAI-compatible path exists, but no remote-provider acceptance is recorded in Tranche 0 |
| Prompt library / presets | `unverified` | Not implemented in Tranche 0 |
| Searchable local history | `unverified` | Durable run/event storage exists; search UI/API does not |
| File / image inputs | `unverified` | Not implemented in Tranche 0 |
| Markdown / code / math rendering | `unverified` | Tranche 0 seat output is plain text |
| Web / RAG adapters | `unverified` | Not implemented in Tranche 0 |
| Model / tool presets | `unverified` | Provider/model seats exist; preset system does not |
| MCP / OpenAPI-style tools | `unverified` | Not implemented in Tranche 0 |
| Notes / notebook | `unverified` | Not implemented in Tranche 0 |
| Explicit opt-in persistent memory | `unverified` | Not implemented in Tranche 0 |
| Image / media adapters | `unverified` | Not implemented in Tranche 0 |
| Usage / cost visibility | `unverified` | Token usage is persisted and visible; complete cost surface is not yet implemented |
| Export / import / share | `unverified` | Not implemented in Tranche 0 |
| Responsive mobile web | `native` | `frontend/tests/seat-grid.test.tsx`; responsive CSS in `frontend/src/styles.css`; browser acceptance still recorded separately |
| Local-first self hosting | `native` | Loopback gateway/UI architecture; `evidence/task6-http-gateway.md`; no cloud credential required for local provider |
| Multi-turn seat context (own thread history) | `native` | `backend/tests/test_dispatch.py` (`test_second_run_in_thread_receives_seat_history`, `test_other_seat_and_failed_runs_do_not_enter_context`); prompt persisted per run (migration `0003_run_prompt`); receipt `context_view_digest` covers the exact messages sent |

Receipt honesty note (2026-10-08): `provider_request_id` is now populated from the provider stream (chunk `id` or `x-request-id` header) when the provider supplies one. `estimated_cost` was removed from the receipt contract instead of remaining a permanently-null field; the dormant database column is retained for schema compatibility. Cost surfacing stays `unverified` above until real pricing data exists.

## Inversion-native differentiators

| Capability | State | Witness / reason |
| --- | --- | --- |
| Context Topology Matrix | `unverified` | Future tranche |
| Provider Capability Compiler with visible loss analysis | `native` | `backend/tests/test_capabilities.py`; `frontend/tests/composer.test.tsx` |
| Conversation Git | `unverified` | Future tranche |
| Counterfactual Replay Lab | `native` | Bounded slice: exactly-one-variable replay (`POST /api/runs/{id}/replay`); `backend/tests/test_routes.py` counterfactual tests; full lab (branching, batch sweeps) does not exist |
| Tool Shadow Mode | `unverified` | Future tranche |
| Compute Frontier | `unverified` | Receipts/timing primitives exist; frontier comparison/planner does not |
| ThreadCapsules | `unverified` | Future tranche |
| Epistemic Independence Ledger / False-Consensus Firewall | `unverified` | Full firewall does not exist; two advisory slices are `native` below (Effective Voices, Mirage Lint); novelty claim also remains unproven |
| "What it saw" (exact context inspection) | `native` | `GET /api/runs/{id}/context` serves the persisted message list; Inspector renders it verbatim; `backend/tests/test_routes.py::test_run_context_endpoint_returns_exact_messages_sent` |
| Effective Voices (independence-discounted counting) | `native` | `backend/src/intelamp/voices.py`; `backend/tests/test_voices.py` incl. the same-model-two-providers falsifier; header display in AppShell |
| Sealed Reveal + Anchoring Delta (exploratory) | `native` | `POST /api/dispatch/{id}/reveal`, `GET /api/dispatch/{id}/anchoring`; `backend/tests/test_anchoring.py`, reveal route tests; lexical movement only — not a correctness measure |
| Consensus Mirage Lint (exploratory, advisory) | `native` | `GET /api/threads/{id}/mirage`; `backend/tests/test_mirage.py`; never blocks or fuses |

## Tranche 0 evidence rule

A passing stub or protocol fixture does not promote an integration. Real-provider claims require sanitized acceptance evidence. A partial primitive does not promote a broader parity row: for example, persisted token usage does not make the complete usage/cost product surface verified.
