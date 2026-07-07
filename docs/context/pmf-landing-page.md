# PMF Landing Page — Content & Strategy Context

> **Purpose of this doc:** Reference context for Claude (or any contributor) when writing copy,
> building components, or reviewing content for the Product-Market-Fit waitlist landing page.
> This is a **paid waitlist** test ($16.99 charge via Stripe) — the goal is to validate real
> willingness-to-pay before building the hardware/software platform further.

---

## 1. Product Summary

A Hardware-as-a-Service device that lives in the user's fridge, powered by a software platform
that uses image capture / video feed to provide:

1. **Fridge Inventory + Count** — what's in the fridge, how much
2. **Food Freshness Levels** — condition/freshness scoring per item
3. **Alerts** — food losing freshness or going bad
4. **Recipe Page** — suggestions based on current fridge contents
5. **Detailed Recipe Page** — existing vs. missing ingredients per recipe
6. **Shopping List Page** — auto-suggested + auto-logged when items run low/out

**Positioning:** Not "a smart fridge gadget." It solves food waste, decision fatigue ("what's for
dinner"), forgotten leftovers, and grocery overspend.

---

## 2. Core Strategic Principles (apply to all copy)

- **Lead with pain, not features.** Name the problem before describing the product.
- **FOMO must come from real mechanics**, not adjectives — scarcity, price lock-in, live social
  proof. Never use fake countdown timers or fabricated stats/logos.
- **The $16.99 is a founding-member deposit / price-lock fee**, not a payment for nothing. Always
  frame it this way in copy — never as a vague "join waitlist" ask.
- **Trust and transparency are conversion levers here**, not just legal boxes — because we're
  charging real money pre-launch, ambiguity about refunds/timeline directly hurts conversion.
- **Honesty over hype.** No fake social proof, no invented press mentions, no misleading claims
  about what's built vs. planned.

---

## 3. Required Page Sections

### 3.1 Hero
- Headline: names the pain, not the category (e.g. "Stop throwing away $1,500 of food a year" >
  "Smart Fridge Inventory AI")
- Subheadline: one sentence describing the flow — capture → track → alert → recipe → reorder
- Primary CTA: explicit action + price, e.g. **"Reserve My Spot — $16.99"** (never vague "Join
  Waitlist" button copy — the price must be visible before click)
- Visual: device/app mockup or short concept clip showing an alert firing

### 3.2 Problem / Agitation
- 2–3 relatable pain points or stats (food waste cost, "mystery Tupperware" moment, last-minute
  grocery runs for stuff already owned)
- Goal: visitor nods in agreement before any pitch

### 3.3 How It Works
- Present the 6 outputs as a **journey/flow**, not a feature bullet list:
  Capture → Inventory & Count → Freshness Scoring → Alerts → Recipes from what you have → Shopping
  list that fills itself
- Visual flow diagram preferred over bullet dump

### 3.4 Differentiation
- Contrast with the real alternative (manual tracking, memory, notes app) — not a competitor
  feature-matrix
- One clear "unlike X, we Y" line > five adjective-driven bullets
- Only state technical edges that are true (e.g. no manual barcode scanning, works with any fridge)

### 3.5 Founding Member / Scarcity Mechanics (the FOMO engine)
- Capped cohort size (real number, e.g. "Only 500 founding spots")
- Price lock-in messaging: "$16.99 today locks founding pricing — price rises to $X at launch"
- Live counter: "X spots claimed" (real data only)
- Founding perks: first hardware batch, lifetime subscription discount, roadmap input, private
  community access

### 3.6 Social Proof
- Only real testers, press, or credentials — if none exist yet, omit this section or lean on
  founder credibility/vision instead of fabricating logos or quotes

### 3.7 Risk Reversal / FAQ
- Explicit statement of what $16.99 covers (refundable deposit vs. reservation fee — pick one and
  be consistent everywhere)
- Refund policy stated plainly
- Expected timeline, with honest caveat that dates may shift
- FAQ: cancellation, what happens if launch slips, what ships first

### 3.8 Final CTA
- Repeat scarcity/price-lock hook once more directly above the final button

---

## 4. Copy Rules / Tone Guardrails

- No fake urgency (countdown timers not tied to a real deadline, fabricated "X people viewing
  this")
- No fabricated social proof, press logos, or testimonials
- Price and what-it-covers must be unambiguous and consistent across hero, CTA, and FAQ
- Avoid generic SaaS-template phrasing ("revolutionize," "game-changing," "AI-powered synergy")
- Prefer concrete numbers and specific scenarios over vague superlatives

---

## 5. Open Items to Fill In Before Launch

- [ ] Confirm refund policy wording (refundable deposit vs. non-refundable reservation fee)
- [ ] Confirm founding cohort cap number
- [ ] Confirm price at public launch (for the "locks in $16.99 vs $X later" claim)
- [ ] Confirm expected device/timeline language legal is comfortable with
- [ ] Add any real beta tester quotes or press mentions once available (do not fabricate placeholders)

---

## 6. Related Docs

- `docs/context/design-system.md` — visual design tokens, component patterns (if applicable)
- `docs/context/brand-voice.md` — tone of voice / writing style guide
- `docs/context/stripe-integration.md` — checkout flow, pricing logic, webhook handling notes
