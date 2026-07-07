import WaitlistForm from "./components/WaitlistForm";
import Section from "./components/Section";
import { LinkButton } from "./components/Button";
import FridgeShelf from "./components/FridgeShelf";
import HowItWorksFlow from "./components/HowItWorksFlow";
import SpotsCounter from "./components/SpotsCounter";
import FaqItem from "./components/FaqItem";

const PERKS = [
  "First hardware batch off the line",
  "50% off, forever — locked the moment you reserve",
  "Direct input on the roadmap",
  "Early-access community with the founders",
];

const FAQS = [
  {
    q: "Is this a full smart fridge replacement?",
    a: "No — it's a low-cost retrofit kit that works with the fridge you already own. No need to buy new appliances.",
  },
  {
    q: "What does the AUD $16.99 actually get me?",
    a: "It reserves your spot in the founding 250 at the early-bird price, locks in 50% off for life, and is fully refundable any time before we ship.",
  },
  {
    q: "What if I change my mind?",
    a: "Cancel any time before launch for a full refund, no questions asked.",
  },
  {
    q: "What happens if the launch date slips?",
    a: "We're building hardware, so timelines can move. If it does, we'll tell you plainly — your reservation and refund option stay exactly as they are until we ship.",
  },
  {
    q: "What ships first?",
    a: "The camera kit and the core app: inventory, freshness scoring, and alerts. Recipes and the auto-filling shopping list follow shortly after, for everyone who's reserved.",
  },
  {
    q: "What happens to the photos of my fridge?",
    a: "Images are processed to detect food items and are not shared or sold. We're finalising our exact retention policy ahead of launch and will publish it in full before any device ships.",
  },
  {
    q: "How much will the full product cost?",
    a: "We're targeting a subscription around $35/month (hardware bundled in), or $105 for the kit outright. Founding members pay half.",
  },
  {
    q: "When will it ship?",
    a: "We're in active hardware development now. Reserving your spot puts you first in line as we move from prototype to pilot production.",
  },
];

export default function Home() {
  return (
    <main className="text-text">
      {/* Nav */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="font-display text-lg font-semibold tracking-tight">SYDAR AI</span>
        <LinkButton href="#waitlist" className="px-4 py-2">
          Reserve — $16.99
        </LinkButton>
      </header>

      {/* Hero */}
      <Section className="!py-12 sm:!py-16">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="flex flex-col items-start text-left">
            <span className="mb-5 inline-flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1 font-mono text-xs font-semibold text-accent">
              Founding cohort — 250 spots
            </span>
            <h1 className="font-display text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">
              Stop throwing away $2,500 a year in food you forgot you had.
            </h1>
            <p className="mt-6 max-w-xl text-lg text-text-muted">
              Clip a camera onto your shelves and SYDAR tracks what&apos;s
              inside, flags what&apos;s about to turn, turns your leftovers
              into dinner, and restocks your list before you run out.
            </p>
            <div id="waitlist" className="mt-10 w-full max-w-md">
              <WaitlistForm />
            </div>
          </div>
          <div className="flex justify-center lg:justify-end">
            <FridgeShelf />
          </div>
        </div>
      </Section>

      {/* Problem */}
      <Section bg="muted">
        <h2 className="text-center font-display text-2xl font-semibold sm:text-4xl">
          You&apos;re not bad at managing your fridge. Nobody can.
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          <div className="rounded-xl bg-bg p-6">
            <p className="font-mono text-3xl font-semibold text-accent">$36.6B</p>
            <p className="mt-2 text-sm text-text-muted">
              lost to food waste in Australia every year.
            </p>
          </div>
          <div className="rounded-xl bg-bg p-6">
            <p className="font-mono text-3xl font-semibold text-accent">$2,500</p>
            <p className="mt-2 text-sm text-text-muted">
              wasted per Australian household every year on food that went off
              before it got used.
            </p>
          </div>
          <div className="rounded-xl bg-bg p-6">
            <span className="text-2xl" aria-hidden="true">
              🫙
            </span>
            <p className="mt-2 text-sm text-text-muted">
              That container in the back of the fridge. You know the one.
              Nobody&apos;s opened it in weeks.
            </p>
          </div>
        </div>
      </Section>

      {/* How it works */}
      <Section>
        <h2 className="text-center font-display text-2xl font-semibold sm:text-4xl">
          How it works
        </h2>
        <p className="mt-3 text-center text-sm text-text-muted">
          Clips onto any shelf in under 5 minutes — no tools.
        </p>
        <HowItWorksFlow />
      </Section>

      {/* Differentiation */}
      <Section bg="muted">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-2xl font-semibold sm:text-4xl">
            Unlike a notes app, your fridge doesn&apos;t forget.
          </h2>
          <p className="mt-4 text-text-muted">
            Sticky notes and shopping apps only work if you remember to update
            them. SYDAR watches the shelf itself — no barcode scanning, no
            typing in what you bought. It works with the fridge you already
            have.
          </p>
        </div>
      </Section>

      {/* Founding member / scarcity */}
      <Section>
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="font-display text-2xl font-semibold sm:text-4xl">
            250 founding spots. That&apos;s it.
          </h2>
          <p className="mt-4 text-text-muted">
            Reserve one for AUD $16.99 — fully refundable any time before
            launch — and lock in 50% off for life.
          </p>
          <div className="mt-8 flex justify-center">
            <SpotsCounter />
          </div>
          <ul className="mx-auto mt-10 grid max-w-xl gap-3 text-left sm:grid-cols-2">
            {PERKS.map((perk) => (
              <li
                key={perk}
                className="rounded-xl border border-border bg-surface p-4 text-sm text-text"
              >
                {perk}
              </li>
            ))}
          </ul>
          <p className="mt-8 text-sm text-text-muted">
            $35/mo, or $105 for the kit outright — founding members pay half.
          </p>
        </div>
      </Section>

      {/* FAQ */}
      <Section bg="muted">
        <div className="mx-auto max-w-2xl">
          <h2 className="text-center font-display text-2xl font-semibold sm:text-4xl">
            FAQ
          </h2>
          <div className="mt-8">
            {FAQS.map((f) => (
              <FaqItem key={f.q} q={f.q} a={f.a} />
            ))}
          </div>
        </div>
      </Section>

      {/* Final CTA */}
      <Section className="text-center">
        <h2 className="font-display text-2xl font-semibold sm:text-4xl">
          250 spots. 50% off for life.
        </h2>
        <p className="mx-auto mt-3 max-w-md text-text-muted">
          Refundable if you change your mind. Reserve your spot for AUD
          $16.99 and be first in line when SYDAR AI ships.
        </p>
        <div className="mt-8 flex justify-center">
          <WaitlistForm />
        </div>
      </Section>

      <footer className="border-t border-border py-10 text-center text-sm text-text-muted">
        © {new Date().getFullYear()} SYDAR AI. All rights reserved.
      </footer>
    </main>
  );
}
