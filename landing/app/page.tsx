import WaitlistForm from "./components/WaitlistForm";

const FEATURES = [
  {
    title: "Live inventory, from your phone",
    desc: "See exactly what's in your fridge without opening the door — cameras keep your app in sync in real time.",
  },
  {
    title: "Freshness & spoilage alerts",
    desc: "Visual freshness scoring flags food before it goes off, so you use it in time instead of throwing it out.",
  },
  {
    title: "Recipes from what you already have",
    desc: "AI-generated recipe suggestions built from your actual current contents — no more \"what should I cook?\" fatigue.",
  },
  {
    title: "Auto-generated shopping lists",
    desc: "As items run low or expire, they're added to your list automatically — no manual tracking.",
  },
  {
    title: "One-click restock",
    desc: "Integrated with Coles, Woolworths and IGA so reordering what you need is a single tap.",
  },
  {
    title: "DIY install, no electrician",
    desc: "Retrofit kit works with any fridge you already own — plug in the camera, link the app, done.",
  },
];

const STEPS = [
  { n: "1", title: "Install", desc: "Clip the camera kit onto your existing fridge shelves. No tools required." },
  { n: "2", title: "Capture", desc: "The camera photographs your fridge contents automatically." },
  { n: "3", title: "Detect", desc: "Our AI identifies every item, estimates freshness, and updates your inventory." },
  { n: "4", title: "Act", desc: "Get alerts, recipes, and a shopping list built from what's actually in your fridge." },
];

const FAQS = [
  {
    q: "Is this a full smart fridge replacement?",
    a: "No — it's a low-cost retrofit kit that works with the fridge you already own. No need to buy new appliances.",
  },
  {
    q: "What happens to the photos of my fridge?",
    a: "Images are processed to detect food items and are not shared or sold. We're finalising our exact retention policy ahead of launch and will publish it in full before any device ships.",
  },
  {
    q: "What does the $16.90 reservation actually get me?",
    a: "It holds your place in line for early access at launch pricing, and is fully refundable any time before we ship if you change your mind.",
  },
  {
    q: "How much will the full product cost?",
    a: "We're targeting a subscription around $35/month (hardware bundled in), with a one-off retail kit option around $105 including a 3-month free trial.",
  },
  {
    q: "When will it ship?",
    a: "We're in active hardware development now. Reserving your spot puts you first in line as we move from prototype to pilot production.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-slate-900">
      {/* Nav */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="text-lg font-bold tracking-tight">SYDAR AI</span>
        <a
          href="#waitlist"
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
        >
          Join waitlist
        </a>
      </header>

      {/* Hero */}
      <section className="mx-auto flex max-w-6xl flex-col items-center px-6 pb-20 pt-12 text-center">
        <span className="mb-5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
          Now taking early reservations
        </span>
        <h1 className="max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">
          Turn any fridge into a{" "}
          <span className="text-emerald-600">smart fridge</span>
        </h1>
        <p className="mt-6 max-w-xl text-lg text-slate-600">
          SYDAR AI is a retrofit camera + AI app that tracks what&apos;s in your
          fridge, warns you before food spoils, and turns your leftovers into
          your next meal — automatically.
        </p>
        <div id="waitlist" className="mt-10 flex flex-col items-center gap-3">
          <WaitlistForm />
        </div>
        <p className="mt-6 text-sm text-slate-400">
          Australian households waste ~$2,500/year in food. Let&apos;s fix that.
        </p>
      </section>

      {/* Problem */}
      <section className="border-y border-slate-100 bg-slate-50">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="text-center text-2xl font-bold sm:text-3xl">
            You&apos;re not bad at managing your fridge. Nobody can.
          </h2>
          <div className="mt-10 grid gap-6 sm:grid-cols-3">
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <p className="text-3xl font-bold text-emerald-600">$36.6B</p>
              <p className="mt-2 text-sm text-slate-600">
                lost to food waste in Australia every year.
              </p>
            </div>
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <p className="text-3xl font-bold text-emerald-600">$2,500</p>
              <p className="mt-2 text-sm text-slate-600">
                wasted per household, per year, on food that spoiled unused.
              </p>
            </div>
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <p className="text-3xl font-bold text-emerald-600">Daily</p>
              <p className="mt-2 text-sm text-slate-600">
                decision fatigue from "what's in the fridge, what should I cook?"
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="text-center text-2xl font-bold sm:text-3xl">How it works</h2>
        <div className="mt-12 grid gap-8 sm:grid-cols-4">
          {STEPS.map((s) => (
            <div key={s.n} className="text-center">
              <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-emerald-600 text-sm font-bold text-white">
                {s.n}
              </div>
              <h3 className="mt-4 font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="border-y border-slate-100 bg-slate-50">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="text-center text-2xl font-bold sm:text-3xl">
            Everything your fridge should already do
          </h2>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <div key={f.title} className="rounded-xl bg-white p-6 shadow-sm">
                <h3 className="font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="text-center text-2xl font-bold sm:text-3xl">Pricing</h2>
        <p className="mx-auto mt-3 max-w-xl text-center text-slate-600">
          Simple, transparent, no lock-in contracts.
        </p>
        <div className="mx-auto mt-12 grid max-w-3xl gap-6 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 p-8">
            <h3 className="font-semibold text-slate-500">Subscription</h3>
            <p className="mt-2 text-4xl font-bold">
              $35<span className="text-base font-medium text-slate-500">/mo</span>
            </p>
            <p className="mt-2 text-sm text-slate-600">
              Camera kit bundled in at no extra cost. Full app access: inventory,
              freshness alerts, recipes, shopping lists.
            </p>
          </div>
          <div className="rounded-2xl border-2 border-emerald-600 p-8">
            <h3 className="font-semibold text-emerald-700">Retail kit</h3>
            <p className="mt-2 text-4xl font-bold">
              $105<span className="text-base font-medium text-slate-500"> one-off</span>
            </p>
            <p className="mt-2 text-sm text-slate-600">
              Buy the hardware outright, includes 3 months of the app subscription
              free. Extra cameras/sensors from $99 each.
            </p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-t border-slate-100 bg-slate-50">
        <div className="mx-auto max-w-3xl px-6 py-20">
          <h2 className="text-center text-2xl font-bold sm:text-3xl">FAQ</h2>
          <div className="mt-10 space-y-6">
            {FAQS.map((f) => (
              <div key={f.q}>
                <h3 className="font-semibold">{f.q}</h3>
                <p className="mt-1 text-sm text-slate-600">{f.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-6 py-20 text-center">
        <h2 className="text-2xl font-bold sm:text-3xl">
          Stop throwing away money.
        </h2>
        <p className="mx-auto mt-3 max-w-md text-slate-600">
          Reserve your spot for AUD $16.90, fully refundable, and be first in
          line when SYDAR AI ships.
        </p>
        <div className="mt-8 flex justify-center">
          <WaitlistForm />
        </div>
      </section>

      <footer className="border-t border-slate-100 py-10 text-center text-sm text-slate-400">
        © {new Date().getFullYear()} SYDAR AI. All rights reserved.
      </footer>
    </main>
  );
}
