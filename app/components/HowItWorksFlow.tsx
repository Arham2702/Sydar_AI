"use client";

import { useEffect, useRef, useState } from "react";

const STEPS = [
  {
    title: "Capture",
    desc: "Cameras quietly photograph your shelves throughout the day.",
  },
  {
    title: "Inventory & count",
    desc: "Every item gets logged — what it is, and how many you've got.",
  },
  {
    title: "Freshness scoring",
    desc: "Each item gets a freshness read, from fresh to going bad.",
  },
  {
    title: "Alerts",
    desc: "You get a heads-up before anything turns, not after.",
  },
  {
    title: "Recipes from what you have",
    desc: "Recipe ideas built from your actual shelf, not a generic list.",
  },
  {
    title: "Shopping list that fills itself",
    desc: "Running low or out? It's already on your list.",
  },
];

export default function HowItWorksFlow() {
  const ref = useRef<HTMLOListElement>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setRevealed(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setRevealed(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <ol
      ref={ref}
      className="relative mt-12 grid gap-8 sm:grid-cols-3 lg:grid-cols-6"
    >
      <div
        className="pointer-events-none absolute left-5 right-5 top-5 hidden h-px bg-border sm:block"
        aria-hidden="true"
      />
      {STEPS.map((step, i) => (
        <li
          key={step.title}
          className={`relative transition-all duration-500 ${
            revealed ? "translate-y-0 opacity-100" : "translate-y-3 opacity-0"
          }`}
          style={{ transitionDelay: `${i * 80}ms` }}
        >
          <div className="relative z-10 flex h-10 w-10 items-center justify-center rounded-full bg-accent font-mono text-sm font-semibold text-white">
            {i + 1}
          </div>
          <h3 className="mt-4 font-semibold text-text">{step.title}</h3>
          <p className="mt-2 text-sm text-text-muted">{step.desc}</p>
        </li>
      ))}
    </ol>
  );
}
