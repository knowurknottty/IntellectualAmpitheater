# Third-party boundaries and provenance

This file records upstream projects used as architecture/reference inputs for IntelAMP Tranche 0. It is not legal advice and it is not a complete dependency-license inventory.

## Frozen reference points

| Project | Frozen revision | Observed license/boundary | IntelAMP use in Tranche 0 |
| --- | --- | --- | --- |
| `open-webui/open-webui` | `0a7c15832fb30b1903753e83f81dc7d27e5b0944` | Open WebUI project license with branding conditions | Reference / future separately identified sidecar only; no source transplanted into IntelAMP core |
| `grokify/chathub` | `bba9ae9...` | MIT | Reference for MCP conversation interoperability; no direct source import in Tranche 0 |
| `chathub-dev/chathub` | `a7a2bd6...` | GPLv3 | Behavioral/reference study only; GPL source is excluded from IntelAMP core |

Before public distribution, re-check current upstream license text and branding terms. Frozen revisions are evidence of what architecture review inspected, not a promise that upstream licensing remains unchanged.

## Provenance guard

`scripts/provenance_guard.py` scans configured source roots for a small set of GPL header markers and, when supplied, a configured GPL reference path. `backend/tests/test_provenance_guard.py` proves the guard rejects those cases.

This guard is deliberately described as a **tripwire**, not a clean-room certification. It cannot prove that ideas or code were independently authored, cannot identify every possible copied fragment, and does not replace human or legal review.

If MIT ChatHub code is ever imported directly, preserve its copyright and license notice. If a GPL distribution plan is ever intentionally adopted, make that a separate explicit distribution decision rather than weakening this guard silently.
