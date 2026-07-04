"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { RecipeSuggestion } from "@/lib/types";
import PageHeader from "@/components/PageHeader";

function MatchRing({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = pct === 100 ? "text-emerald-600" : pct >= 50 ? "text-amber-600" : "text-slate-400";
  return <span className={`text-sm font-semibold ${color}`}>{pct}%</span>;
}

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<RecipeSuggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .suggestions()
      .then((r) => setRecipes(r.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="Recipe Suggestions"
        subtitle="Ranked by what you already have — recipes using expiring items float to the top."
      />

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {recipes.map((r) => (
            <Link
              key={r.id}
              href={`/recipes/${r.id}`}
              className="card flex flex-col gap-3 p-4 transition hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-medium text-slate-900">{r.name}</div>
                  <div className="text-xs text-slate-400">
                    {r.cuisine} · {r.prep_minutes} min
                  </div>
                </div>
                <MatchRing score={r.match_score} />
              </div>
              <p className="text-sm text-slate-500 line-clamp-2">{r.description}</p>
              <div className="mt-auto flex items-center justify-between">
                <span className="text-xs text-slate-500">
                  You have {r.owned_count}/{r.required_count} ingredients
                </span>
                {r.uses_expiring && (
                  <span className="rounded-full bg-orange-50 px-2 py-0.5 text-[11px] font-medium text-orange-700">
                    Uses expiring
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
