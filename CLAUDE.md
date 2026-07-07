# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page Next.js (App Router) marketing/waitlist site for SYDAR AI — a retrofit camera + AI kit that turns any fridge into a smart fridge (inventory tracking, spoilage alerts, recipe suggestions, auto shopping lists). The entire product pitch lives in `app/page.tsx`; there is no dashboard, auth, or app functionality beyond the landing page and a paid waitlist reservation flow.

## Commands

```bash
npm run dev     # start dev server (localhost:3000)
npm run build   # production build
npm run start   # run production build
npm run lint    # next lint
```

No test suite exists in this repo.

## Architecture

- **`app/page.tsx`** — the entire landing page (hero, problem stats, how-it-works, features, pricing, FAQ, CTA, footer). Content arrays (`FEATURES`, `STEPS`, `FAQS`) are defined at the top of the file and mapped over — edit copy there rather than the JSX below.
- **`app/components/WaitlistForm.tsx`** — client component (email input + submit) rendered twice on the page (hero and final CTA). On submit it POSTs to `/api/checkout` and redirects the browser to the returned Stripe Checkout URL.
- **`app/api/checkout/route.ts`** — server route that creates a Stripe Checkout session (mode: `payment`) for a fixed AUD $16.99 refundable waitlist deposit. Requires `STRIPE_SECRET_KEY` in the environment; returns a 500 JSON error if unset (there is no other backend/database — Stripe is the only external integration). Success redirects to `/success?session_id=...`; cancel redirects to `/?checkout=cancelled`.
- **`app/success/page.tsx`** — static confirmation page shown after a completed Stripe Checkout session (no session/order lookup is performed — it just displays a thank-you message).
- **`app/layout.tsx`** — root layout; loads local Geist fonts and sets page metadata (title/description) used for SEO/social previews.

## Conventions

- Styling is Tailwind utility classes inline in JSX — no separate stylesheet or component library beyond `app/globals.css` (Tailwind base/components/utilities).
- Pricing, deposit amount, and copy are business-facing constants embedded directly in `page.tsx`, `WaitlistForm.tsx`, and `api/checkout/route.ts` — if one changes (e.g. the $16.99 deposit or $35/mo price), check all three for consistency since they're not centralized.
