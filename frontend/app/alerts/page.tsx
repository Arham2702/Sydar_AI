"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Alert } from "@/lib/types";
import PageHeader from "@/components/PageHeader";

const SEVERITY: Record<string, string> = {
  critical: "border-l-rose-500 bg-rose-50",
  warning: "border-l-amber-500 bg-amber-50",
  info: "border-l-slate-400 bg-slate-50",
};

const TYPE_LABEL: Record<string, string> = {
  expiring: "Expiring soon",
  expired: "Expired",
  low_stock: "Low stock",
  out_of_stock: "Out of stock",
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setAlerts((await api.alerts()).data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function ack(id: number) {
    await api.ackAlert(id);
    load();
  }

  const active = alerts.filter((a) => !a.acknowledged);
  const done = alerts.filter((a) => a.acknowledged);

  return (
    <div>
      <PageHeader
        title="Alerts"
        subtitle="Items losing freshness or running low, derived from live inventory."
      />

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : alerts.length === 0 ? (
        <div className="card p-10 text-center text-sm text-slate-500">
          No alerts. Everything looks fresh and well-stocked. 🎉
        </div>
      ) : (
        <div className="space-y-6">
          <section className="space-y-2">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Needs attention ({active.length})
            </h2>
            {active.length === 0 && (
              <p className="text-sm text-slate-400">All caught up.</p>
            )}
            {active.map((a) => (
              <div
                key={a.id}
                className={`flex items-center justify-between rounded-lg border border-l-4 border-slate-200 px-4 py-3 ${
                  SEVERITY[a.severity]
                }`}
              >
                <div>
                  <div className="text-sm font-medium text-slate-900">{a.message}</div>
                  <div className="mt-0.5 text-xs text-slate-500">
                    {TYPE_LABEL[a.alert_type]} · {a.item_name}
                  </div>
                </div>
                <button
                  onClick={() => ack(a.id)}
                  className="rounded-md bg-white px-3 py-1.5 text-xs font-medium text-slate-600 ring-1 ring-slate-200 hover:bg-slate-100"
                >
                  Dismiss
                </button>
              </div>
            ))}
          </section>

          {done.length > 0 && (
            <section className="space-y-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Dismissed ({done.length})
              </h2>
              {done.map((a) => (
                <div
                  key={a.id}
                  className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 opacity-60"
                >
                  <div className="text-sm text-slate-500 line-through">{a.message}</div>
                  <span className="text-xs text-slate-400">dismissed</span>
                </div>
              ))}
            </section>
          )}
        </div>
      )}
    </div>
  );
}
