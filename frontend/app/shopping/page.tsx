"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { ShoppingItem } from "@/lib/types";
import PageHeader from "@/components/PageHeader";

const SOURCE_LABEL: Record<string, string> = {
  auto_low_stock: "Auto · low stock",
  auto_out: "Auto · out of stock",
  manual: "Added manually",
};

export default function ShoppingPage() {
  const [items, setItems] = useState<ShoppingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [qty, setQty] = useState(1);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setItems((await api.shopping()).data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    await api.addShopping(name.trim(), qty);
    setName("");
    setQty(1);
    load();
  }

  async function togglePurchased(item: ShoppingItem) {
    await api.updateShopping(item.id, {
      status: item.status === "needed" ? "purchased" : "needed",
    });
    load();
  }

  async function remove(id: number) {
    await api.deleteShopping(id);
    load();
  }

  const groups = useMemo(() => {
    const needed = items.filter((i) => i.status === "needed");
    return {
      auto: needed.filter((i) => i.source !== "manual"),
      manual: needed.filter((i) => i.source === "manual"),
      purchased: items.filter((i) => i.status === "purchased"),
    };
  }, [items]);

  const row = (item: ShoppingItem) => (
    <div
      key={item.id}
      className="flex items-center gap-3 rounded-lg border border-slate-100 px-4 py-2.5"
    >
      <input
        type="checkbox"
        checked={item.status === "purchased"}
        onChange={() => togglePurchased(item)}
        className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
      />
      <div className="flex-1">
        <div
          className={`text-sm font-medium ${
            item.status === "purchased" ? "text-slate-400 line-through" : "text-slate-900"
          }`}
        >
          {item.name}
        </div>
        <div className="text-xs text-slate-400">
          {item.quantity} {item.unit} · {SOURCE_LABEL[item.source]}
        </div>
      </div>
      <button
        onClick={() => remove(item.id)}
        className="text-xs text-slate-400 hover:text-rose-600"
      >
        Remove
      </button>
    </div>
  );

  return (
    <div>
      <PageHeader
        title="Shopping List"
        subtitle="Auto-filled as items run low or out — plus anything you add yourself."
      />

      <form onSubmit={add} className="card mb-6 flex flex-wrap items-center gap-2 p-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Add an item…"
          className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
        />
        <input
          type="number"
          min={1}
          value={qty}
          onChange={(e) => setQty(Math.max(1, Number(e.target.value)))}
          className="w-20 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
        />
        <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
          Add
        </button>
      </form>

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : items.length === 0 ? (
        <div className="card p-10 text-center text-sm text-slate-500">
          Your shopping list is empty.
        </div>
      ) : (
        <div className="space-y-6">
          <Section title={`Auto-added (${groups.auto.length})`}>
            {groups.auto.length ? groups.auto.map(row) : <Empty />}
          </Section>
          <Section title={`Manual (${groups.manual.length})`}>
            {groups.manual.length ? groups.manual.map(row) : <Empty />}
          </Section>
          {groups.purchased.length > 0 && (
            <Section title={`Purchased (${groups.purchased.length})`}>
              {groups.purchased.map(row)}
            </Section>
          )}
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">{title}</h2>
      {children}
    </section>
  );
}

function Empty() {
  return <p className="text-sm text-slate-400">Nothing here.</p>;
}
