# `docs/context/` — Project Context Reference

This folder holds the reference docs that ground any content, copy, or design work on this
project — for human contributors and for Claude (or any AI assistant) working in this codebase.
When writing code or copy for a page/feature, check the relevant file(s) below first rather than
guessing at tone, structure, or conventions.

## Files in this folder

| File | Use it when you're... | Status |
|---|---|---|
| `pmf-landing-page.md` | Writing or reviewing content/structure for the PMF waitlist landing page | Active |
| `brand-voice.md` | Writing any copy — landing page, emails, UI text, error states, alerts | Active |
| `design-rules.md` | Building or reviewing any UI — layout, color, type, motion, components | Active |
| `product-spec.md` | Referencing the 6 core product features, data model, or roadmap status | Planned — not yet created |
| `stripe-integration.md` | Working on checkout flow, pricing, refunds, or webhook logic | Planned — not yet created |

## How to use this folder

- **Before writing copy** for any new page or feature → read `brand-voice.md` first.
- **Before building or restyling UI** → read `design-rules.md` first.
- **Before touching the waitlist page specifically** → read `pmf-landing-page.md` for required
  sections and content strategy, in addition to the two above.
- If a new recurring topic comes up (e.g. onboarding flow, analytics plan, notification copy
  rules), add a new file here rather than letting conventions live only in code comments or
  Slack threads.

## Conventions for this folder

- One file per concern — keep files focused so they can be referenced individually instead of
  requiring a full read of everything.
- Mark files as `Active` or `Planned` in the table above so it's clear what's authoritative vs.
  still to be written.
- Keep "living" open questions (e.g. TODOs, unconfirmed pricing) inside the relevant file's own
  "Open Items" section rather than in this README — this README should stay stable as an index.
- When a file materially changes (e.g. brand voice shifts, new design direction chosen), update
  it in place — don't create `brand-voice-v2.md`. Git history is the changelog.

## Suggested next files to add

- `product-spec.md` — the 6 core features (inventory, freshness, alerts, recipes, detailed
  recipes, shopping list), data model, and current build status of each
- `stripe-integration.md` — price IDs, checkout flow, refund policy as implemented in code,
  webhook handling notes
- `component-patterns.md` — split out from `design-rules.md` §8 once component patterns are
  finalized and it grows too large for one section
