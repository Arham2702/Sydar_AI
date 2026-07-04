"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Inventory", icon: "🧊" },
  { href: "/alerts", label: "Alerts", icon: "🔔" },
  { href: "/recipes", label: "Recipes", icon: "🍳" },
  { href: "/shopping", label: "Shopping", icon: "🛒" },
];

export default function Nav() {
  const pathname = usePathname();
  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <aside className="flex w-full shrink-0 flex-row gap-1 border-b border-slate-200 bg-white px-4 py-3 md:h-screen md:w-60 md:flex-col md:gap-2 md:border-b-0 md:border-r md:px-4 md:py-6">
      <div className="mb-0 hidden items-center gap-2 px-2 md:mb-6 md:flex">
        <span className="text-2xl">🧊</span>
        <div>
          <div className="text-sm font-semibold text-slate-900">FreshKeep</div>
          <div className="text-xs text-slate-400">Smart Fridge</div>
        </div>
      </div>
      {LINKS.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition md:flex-none md:justify-start ${
            isActive(l.href)
              ? "bg-brand-50 text-brand-700"
              : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <span aria-hidden>{l.icon}</span>
          <span className="hidden sm:inline">{l.label}</span>
        </Link>
      ))}
    </aside>
  );
}
