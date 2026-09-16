# Tranche 0 UI / attention audit

Observed on 2026-09-16 during the Tranche 0 acceptance pass. This file separates machine checks, static inspection, and items that remain unverified.

## Anti-slop firewall

Firewall: `/Users/knowurknot/.hermes/skills/inversion-captivation-craft/scripts/firewall.py`

Self-check: **PASS**.

Source scan: **11 files under `frontend/src`, 0 failing checks**.

| Fail check | Hits |
| --- | ---: |
| em dash | 0 |
| en dash as separator | 0 |
| `transition: all` | 0 |
| `h-screen` viewport | 0 |
| scroll event listener | 0 |
| AI violet-indigo hex | 0 |
| violet/indigo/purple utility | 0 |
| pure black/white | 0 |
| decorative gradient | 0 |
| glass blur | 0 |
| three equal columns | 0 |
| slop copy | 0 |
| placeholder person | 0 |
| fixed pixel type under 12px | 0 |
| `will-change: all` | 0 |
| fill-only color used as text | 0 |
| emoji | 0 |

Source presence checks: `prefers-reduced-motion` present in 1 file; `prefers-color-scheme`, tabular-number utility, and logical-property presence were warnings at 0 files, not fail checks.

The production bundle was copied out of `dist/` because the firewall intentionally skips directories named `dist`. The copied bundle scan covered 3 files and produced one `slop copy` hit for the token `seamless`. Context inspection located it inside React DOM's compiled HTML attribute switch (`case "seamless"`), not IntelAMP-authored UI copy. The source scan contains zero such hits. This bundle result is recorded as a dependency false positive, not silently rewritten or treated as a source pass.

## Accessibility / attention checks

Static inspection and automated tests verify:

- full-height shell uses `100dvh`;
- minimum 44 px control sizing is present;
- mobile prompt input uses 16 px type;
- visible `:focus-visible` treatment exists;
- reduced-motion handling exists;
- active Stop and Send are both full action controls; Stop uses the alert fill and is not visually subordinated while runs are active;
- no autoplay, interval-driven recapture, streak/countdown, or infinite-scroll tokens were found in frontend source;
- no analytics/behavioral-telemetry tokens were found in frontend source;
- optional capability loss is explicit and requires acknowledgement before dispatch;
- hard capability incompatibility disables dispatch rather than silently degrading;
- sibling failure does not erase successful sibling output;
- mobile layout focuses one seat at a time rather than compressing six seats into tiny columns.

WCAG contrast calculations for the current NIGHT TABLE token pairs:

- ink / field: **16.06:1**
- muted ink / field: **7.81:1**
- brass accent / field: **8.17:1**
- alert fill / dark ink: **6.37:1**
- ink / oxblood dominant fill: **5.57:1**

## Runtime smoke

`scripts/dev.sh` was exercised under CAPT Node. Vite served `http://127.0.0.1:5173/`, the `/api` proxy reached the loopback FastAPI gateway, and `/api/health` returned `{"status":"ok"}`. An initial smoke exposed a frontend/backend startup race; the script was hardened to wait for gateway health before starting Vite. The final smoke passed with `PROXY_RACE=NONE`. No external network endpoint was required.

## Unverified in this pass

The following are not promoted from static/code evidence: screen-reader behavior across browsers, CPU-throttled constrained-browser performance, OS-level high-contrast modes, translated-layout stress, and exhaustive keyboard traversal in a real browser. They remain **UNVERIFIED**, not assumed from source structure.

## Final verification rerun

The final pre-commit verification rerun recorded:

- backend: **39 passed**;
- frontend: **14 passed** across 3 files;
- TypeScript: `tsc --noEmit` **PASS**;
- Vite production build: **PASS**;
- Alembic fresh-database upgrade: `0001_initial` **PASS** with expected tables;
- provenance guard tests: **3 passed**;
- provenance source scan: **PASS, 0 issues**;
- anti-slop firewall self-check: **PASS**;
- anti-slop source scan: **0 failing checks** across 11 frontend source files;
- loopback dev smoke: frontend served, `/api` proxy returned `{"status":"ok"}`, and IntelAMP HTML loaded.

The real-provider acceptance witness remains `task10-local-acceptance.md`; it records the one-seat, six-seat, cancellation, and invalid-sibling cases against the live local llama.cpp model. No unit fixture is promoted to that status.
