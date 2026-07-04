"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { InventoryItem } from "@/lib/types";
import PageHeader from "@/components/PageHeader";
import IngestPanel from "@/components/IngestPanel";
import { FreshnessBadge, FreshnessMeter } from "@/components/FreshnessBadge";

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("all");
  const [sortByFreshness, setSortByFreshness] = useState(true);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.inventory();
      setItems(res.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Release the previous object URL when the preview changes or on unmount.
  useEffect(() => {
    return () => {
      if (photoUrl) URL.revokeObjectURL(photoUrl);
    };
  }, [photoUrl]);

  const categories = useMemo(
    () => ["all", ...Array.from(new Set(items.map((i) => i.category))).sort()],
    [items]
  );

  const visible = useMemo(() => {
    let list = category === "all" ? items : items.filter((i) => i.category === category);
    list = [...list].sort((a, b) =>
      sortByFreshness
        ? b.freshness.score - a.freshness.score // highest freshness first
        : a.name.localeCompare(b.name)
    );
    return list;
  }, [items, category, sortByFreshness]);

  async function adjust(item: InventoryItem, delta: number) {
    const next = Math.max(0, item.quantity + delta);
    await api.adjustItem(item.id, next);
    load();
  }

  return (
    <div>
      <PageHeader
        title="Fridge Inventory"
        subtitle="Live view of what's inside, with per-item freshness."
      />

      <div className="mb-6">
        <IngestPanel onIngested={load} onImage={setPhotoUrl} />
      </div>

      {photoUrl && (
        <div className="card mb-6 overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-2">
            <span className="text-xs font-semibold text-slate-500">Uploaded image</span>
            <button
              onClick={() => setPhotoUrl(null)}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              Hide
            </button>
          </div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={photoUrl}
            alt="Uploaded fridge photo"
            className="max-h-80 w-full bg-slate-50 object-contain"
          />
        </div>
      )}

      {items.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-2">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition ${
                category === c
                  ? "bg-brand-600 text-white"
                  : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-100"
              }`}
            >
              {c}
            </button>
          ))}
          <button
            onClick={() => setSortByFreshness((v) => !v)}
            className="ml-auto rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200 hover:bg-slate-100"
          >
            Sort: {sortByFreshness ? "Freshness" : "Name"}
          </button>
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : items.length === 0 ? (
        <div className="card p-10 text-center text-sm text-slate-500">
          No items tracked yet. Ingest a sample scene above to get started.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visible.map((item) => (
            <div key={item.id} className="card flex flex-col gap-3 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-medium text-slate-900">{item.name}</div>
                  <div className="text-xs capitalize text-slate-400">{item.category}</div>
                </div>
                <FreshnessBadge freshness={item.freshness} />
              </div>

              <FreshnessMeter freshness={item.freshness} />

              <div className="mt-1 flex items-center justify-between">
                <div className="text-sm text-slate-500">
                  <span className="text-lg font-semibold text-slate-900">{item.quantity}</span>{" "}
                  {item.unit}
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => adjust(item, -1)}
                    className="h-7 w-7 rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200"
                    aria-label="decrease"
                  >
                    −
                  </button>
                  <button
                    onClick={() => adjust(item, 1)}
                    className="h-7 w-7 rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200"
                    aria-label="increase"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
