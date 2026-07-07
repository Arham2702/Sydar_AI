"use client";

import { useEffect, useState } from "react";
import FreshnessBadge, { type FreshnessState } from "./FreshnessBadge";

type Item = {
  name: string;
  qty: string;
  state: FreshnessState;
};

const STATIC_ITEMS: Item[] = [
  { name: "Milk", qty: "1 L", state: "fresh" },
  { name: "Leftover pasta", qty: "1 container", state: "use-soon" },
  { name: "Eggs", qty: "8", state: "fresh" },
  { name: "Berries", qty: "1 punnet", state: "going-bad" },
];

export default function FridgeShelf() {
  const [mounted, setMounted] = useState(false);
  const [spinachState, setSpinachState] = useState<FreshnessState>("fresh");

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduced) {
      setMounted(true);
      setSpinachState("use-soon");
      return;
    }

    const mountTimer = setTimeout(() => setMounted(true), 50);
    const alertTimer = setTimeout(() => setSpinachState("use-soon"), 1800);
    return () => {
      clearTimeout(mountTimer);
      clearTimeout(alertTimer);
    };
  }, []);

  const items: Item[] = [
    { name: "Spinach", qty: "1 bag", state: spinachState },
    ...STATIC_ITEMS,
  ];

  return (
    <div
      className="w-full max-w-sm rounded-2xl border border-border bg-surface p-4 shadow-[0_1px_2px_rgba(20,36,32,0.06),0_8px_24px_rgba(20,36,32,0.08)]"
      role="img"
      aria-label="Fridge shelf showing five tracked items with freshness alerts: spinach turning use-soon, milk fresh, leftover pasta use-soon, eggs fresh, and berries going bad."
    >
      <div className="mb-3 flex items-center justify-between">
        <span className="font-mono text-xs uppercase tracking-wide text-text-muted">
          Your fridge · live
        </span>
        <span className="h-1.5 w-1.5 rounded-full bg-success" aria-hidden="true" />
      </div>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li
            key={item.name}
            className={`flex items-center justify-between rounded-xl border border-border bg-bg px-3 py-2.5 transition-all duration-500 ${
              mounted ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"
            }`}
            style={{ transitionDelay: `${i * 90}ms` }}
          >
            <div>
              <p className="text-sm font-medium text-text">{item.name}</p>
              <p className="font-mono text-xs text-text-muted">{item.qty}</p>
            </div>
            <FreshnessBadge state={item.state} />
          </li>
        ))}
      </ul>
    </div>
  );
}
