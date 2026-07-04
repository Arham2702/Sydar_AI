"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { RecipeDetail } from "@/lib/types";
import PageHeader from "@/components/PageHeader";

export default function RecipeDetailPage() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [addState, setAddState] = useState<"idle" | "adding" | "done">("idle");

  useEffect(() => {
    api
      .recipe(id)
      .then((r) => setRecipe(r.data))
      .finally(() => setLoading(false));
  }, [id]);

  async function addMissing() {
    setAddState("adding");
    await api.addMissing(id);
    setAddState("done");
  }

  if (loading) return <p className="text-sm text-slate-400">Loading…</p>;
  if (!recipe) return <p className="text-sm text-slate-400">Recipe not found.</p>;

  return (
    <div>
      <Link href="/recipes" className="text-sm text-brand-700 hover:underline">
        ← Back to recipes
      </Link>

      <PageHeader
        title={recipe.name}
        subtitle={`${recipe.cuisine} · ${recipe.prep_minutes} min · you have ${recipe.owned_count}/${recipe.required_count} core ingredients`}
      />

      <p className="mb-6 max-w-2xl text-sm text-slate-600">{recipe.description}</p>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-900">Ingredients</h2>
            {recipe.missing.length > 0 && (
              <button
                onClick={addMissing}
                disabled={addState !== "idle"}
                className="rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-brand-700 disabled:opacity-60"
              >
                {addState === "idle"
                  ? `Add ${recipe.missing.length} missing to list`
                  : addState === "adding"
                  ? "Adding…"
                  : "Added ✓"}
              </button>
            )}
          </div>
          <ul className="space-y-2">
            {recipe.ingredients.map((ing) => (
              <li
                key={ing.name}
                className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-block h-2 w-2 rounded-full ${
                      ing.owned ? "bg-emerald-500" : "bg-slate-300"
                    }`}
                  />
                  <span className={ing.owned ? "text-slate-900" : "text-slate-400"}>
                    {ing.name}
                  </span>
                  {ing.optional && (
                    <span className="text-[11px] text-slate-400">(optional)</span>
                  )}
                </div>
                <span className="text-xs text-slate-400">
                  {ing.quantity} {ing.unit}
                  {ing.owned ? ` · have ${ing.owned_quantity}` : " · missing"}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card p-5">
          <h2 className="mb-3 text-sm font-semibold text-slate-900">Steps</h2>
          <ol className="space-y-3">
            {recipe.steps.map((step, i) => (
              <li key={i} className="flex gap-3 text-sm text-slate-600">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand-700">
                  {i + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}
