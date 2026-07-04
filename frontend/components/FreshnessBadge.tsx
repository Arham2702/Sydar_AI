import type { Freshness, FreshnessLevel } from "@/lib/types";

const STYLES: Record<FreshnessLevel, { label: string; cls: string; bar: string }> = {
  fresh: { label: "Fresh", cls: "bg-emerald-50 text-emerald-700", bar: "bg-emerald-500" },
  aging: { label: "Aging", cls: "bg-amber-50 text-amber-700", bar: "bg-amber-500" },
  expiring: { label: "Expiring", cls: "bg-orange-50 text-orange-700", bar: "bg-orange-500" },
  expired: { label: "Expired", cls: "bg-rose-50 text-rose-700", bar: "bg-rose-500" },
};

export function FreshnessBadge({ freshness }: { freshness: Freshness }) {
  const s = STYLES[freshness.level];
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${s.cls}`}>
      {s.label}
    </span>
  );
}

export function FreshnessMeter({ freshness }: { freshness: Freshness }) {
  const s = STYLES[freshness.level];
  return (
    <div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full ${s.bar}`}
          style={{ width: `${Math.max(4, freshness.score)}%` }}
        />
      </div>
      <div className="mt-1 flex items-center justify-between text-xs text-slate-400">
        <span className="font-medium text-slate-500">{freshness.score}% fresh</span>
        <span>
          {freshness.days_remaining > 0
            ? `~${freshness.days_remaining}d left`
            : `${Math.abs(freshness.days_remaining)}d past best`}
        </span>
      </div>
    </div>
  );
}
