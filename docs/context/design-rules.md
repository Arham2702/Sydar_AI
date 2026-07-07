# Design Rules & Conventions

> **Purpose of this doc:** Reference for building the PMF landing page (and future product UI) so
> design decisions stay consistent and intentional rather than defaulting to generic templates.
> Read this alongside `brand-voice.md` (copy) and `pmf-landing-page.md` (content structure).

---

## 1. Design philosophy

This page should feel like a **considered kitchen tool**, not a generic SaaS/AI startup template.
Avoid the current "AI-generated look" defaults:

- ❌ Warm cream background + high-contrast serif + terracotta accent (an overused AI-startup look)
- ❌ Near-black background + single acid-green or vermilion accent
- ❌ Broadsheet/newspaper layout with hairline rules and dense columns, used just as a default

These aren't off-limits forever — but they shouldn't be the *unconsidered* default. Ground the
palette, type, and layout in the actual subject: fridges, fresh food, kitchens, the specific
relief of not wasting food. Take one real, justifiable aesthetic risk rather than playing it
generic-safe.

**The hero should open with the most characteristic thing in this product's world** — not a big
number + small label + gradient (the template answer). Consider: a live-feeling freshness alert,
an actual fridge shelf visual, a before/after (forgotten food vs. tracked food) — something
grounded in the real object.

---

## 2. Color

- Define a **4–6 color token system** with named hex values, not ad hoc colors scattered through
  code. e.g.:
  ```
  --color-bg:        #...
  --color-surface:   #...
  --color-text:      #...
  --color-accent:    #...
  --color-warn:      #...   /* used for "going bad" alerts — should read as urgent but not alarming */
  --color-success:   #...   /* used for "fresh" states */
  ```
- Reserve the accent color for one clear purpose (primary CTA + key highlights). Don't spread it
  everywhere or it stops meaning anything.
- Freshness/alert colors need real semantic meaning (fresh vs. use-soon vs. expired) — this is
  functional color, not just brand color. Make sure it's distinguishable without relying on color
  alone (add icon/label) for accessibility.

---

## 3. Typography

- Pick **2–3 typefaces with distinct roles**: a display face with real character (used with
  restraint — headlines only), a body face optimized for readability, and optionally a utility
  face for data/labels (prices, counts, timestamps).
- Don't reach for the same pairing every project would use by default (e.g. generic
  geometric-sans + generic serif). Choose something that fits a "practical kitchen tool with a bit
  of warmth" feel.
- Set a clear type scale (e.g. a defined ramp of sizes/weights) and use it consistently —
  headline, subhead, body, caption, button — rather than ad hoc font-sizes per section.
- Sentence case throughout (see brand-voice.md) — avoid Title Case or ALL CAPS headlines.

---

## 4. Layout & structure

- Structure should **encode real information**, not decorate. Only use numbered steps (01/02/03)
  if the content is a genuine sequence (e.g. "How it works" flow) — don't add numbering just for
  visual rhythm.
- Standard section order for this page (see `pmf-landing-page.md` §3 for content):
  1. Hero
  2. Problem/agitation
  3. How it works (flow, not bullet list)
  4. Differentiation
  5. Founding member / scarcity mechanics
  6. Social proof (omit if none real yet)
  7. Risk reversal / FAQ
  8. Final CTA
- Keep consistent vertical rhythm (spacing scale) between sections — pick a base unit (e.g. 8px)
  and derive all spacing from it rather than one-off margins.
- Mobile-first: most waitlist traffic will be from social/mobile. Design and test mobile layout
  first, not as an afterthought.

---

## 5. Motion & interaction

- Use motion **deliberately, not decoratively**. One orchestrated moment (e.g. a page-load
  sequence showing an alert firing, or a scroll-triggered reveal of the "how it works" flow) lands
  harder than scattered hover animations everywhere.
- Good candidates for motion: hero load-in, "how it works" flow reveal on scroll, live spot-counter
  ticking up.
- Avoid: bouncing icons, gratuitous parallax, animating every element on scroll — this reads as
  templated/AI-generated rather than intentional.
- Always respect `prefers-reduced-motion`.

---

## 6. Signature element

Every strong page has **one memorable thing** it's remembered by. For this page, candidates worth
considering (pick one, execute it well, keep everything else quiet):
- A live/interactive freshness-alert demo embedded in the hero
- A real-feeling "fridge shelf" visual that updates as you scroll (items appearing/aging)
- The live founding-spots counter as a genuinely well-designed, prominent element rather than a
  small badge

Spend the design "boldness budget" on this one element. Keep the rest of the page quiet and
disciplined around it.

---

## 7. Accessibility & quality floor (non-negotiable, don't announce it — just do it)

- Responsive down to small mobile widths
- Visible keyboard focus states on all interactive elements
- Sufficient color contrast, especially for freshness/alert states (don't rely on color alone —
  pair with icon or text label)
- `prefers-reduced-motion` respected
- Alt text on all meaningful images
- Form fields (Stripe checkout, email capture) have real labels, not just placeholder text

---

## 8. Component patterns to define early

As the codebase grows, these should get their own consistent pattern (documented here once
decided, or split into a `component-patterns.md` if this section grows large):

- Primary CTA button (state, hover, disabled/loading during Stripe checkout)
- Live counter component ("X spots claimed")
- FAQ accordion pattern
- Section wrapper (consistent max-width, padding, background handling)
- Alert/badge component (for freshness states — reused later in actual product UI, so worth
  designing with that reuse in mind now)

---

## 9. Before shipping any section — quick self-check

- Does this look like it was built for *this* product, or would it look the same on any
  AI-startup landing page? If the latter, revise.
- Is there exactly one bold/signature moment, with everything else quiet around it?
- Does every structural device (numbers, dividers, labels) encode something true about the
  content?
- Mobile check: does it still feel intentional, not just "shrunk desktop"?
