# IntellectualAmpitheater design recursion ledger

Canonical artifact: `docs/superpowers/specs/2026-09-15-intellectualampitheater-design.md`

This is serial refinement, not independent voting. Each pass reviewed the artifact produced by the preceding pass.

## Recovery note

The first Node-governed transport attempt truncated the large base64 payload and produced a 7,754-byte incomplete file. Raw RDC file write was used as an out-of-band recovery transport to restore the complete non-secret design artifact. The restored bytes were then read and hashed through CAPT Node before recursion began. The incomplete write is not part of the accepted lineage.

## Pass 0 — restored baseline

SHA-256: `9b3461ddb5172dca820e8fee4fee67a447f21e70ddcd3dc5f2c2d5831ab62259`

Review objective: freeze architecture A and make the product contract explicit.

## Pass 1 — product contract / license / authority

Input SHA-256: `9b3461ddb5172dca820e8fee4fee67a447f21e70ddcd3dc5f2c2d5831ab62259`
Output SHA-256: `3fc468006e67ff3c55bfc00bd22b9fbaa5098f3a49b109f1f6af8a83d1991af6`

Accepted findings:
- "Best of both worlds" was underspecified as a useful subset rather than an exhaustive capability ledger.
- Added an evidence-driven paid-tier parity ledger contract with explicit states.
- Preserved the Open WebUI / MIT ChatHub / GPL ChatHub boundaries and the CAPT authority separation.

Rejected finding:
- Do not claim paid-tier parity at design time; the ledger tracks the target and witnesses later implementation state.

## Pass 2 — failure / recovery / queue semantics

Input SHA-256: `3fc468006e67ff3c55bfc00bd22b9fbaa5098f3a49b109f1f6af8a83d1991af6`
Output SHA-256: `22fdf8e5e722408afd6a632a5081d9f1254e0749dd4c431c3cd96536d7ec8623`

Accepted findings:
- Streaming reliability needed an explicit sequence/backpressure/reconnect contract.
- Added durable per-run sequence semantics, visible queueing, bounded buffers, gap handling, and retry lineage.
- Reaffirmed that transport concurrency does not establish epistemic independence.

## Pass 3 — device/resource completeness

Input SHA-256: `22fdf8e5e722408afd6a632a5081d9f1254e0749dd4c431c3cd96536d7ec8623`
Output SHA-256: `c0f8d0164da7b712d3c513c61f7f582616e71445690edd4b82aecf4dd3634d8f`

Accepted findings:
- Responsive behavior needed to cover low-end and high-end hardware, not only viewport width.
- Added equal-capability resource profiles, transcript virtualization/batched rendering, a no-WebGL core requirement, and constrained-browser acceptance testing.
- Mobile six-seat behavior is now explicit: one full seat plus compact status/selection, never six unreadable columns.

## Final consistency gate

CAPT Node read-back observed final spec SHA-256 `c0f8d0164da7b712d3c513c61f7f582616e71445690edd4b82aecf4dd3634d8f` across 933 lines. Checks passed for placeholder absence, truncation-marker absence, architecture-A identity, exhaustive parity-ledger language, CAPT seat/vessel boundary, qualitative false-consensus contract, local llama.cpp acceptance requirement, device/resource profile, and the written-spec approval gate.

Local commit witness is recorded after the commit is created; this ledger does not pre-claim it.
