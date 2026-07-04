"use client";

import { useState } from "react";
import { api, SAMPLE_SCENES } from "@/lib/api";
import type { IngestResult } from "@/lib/types";

export default function IngestPanel({
  onIngested,
  onImage,
}: {
  onIngested: () => void;
  onImage?: (url: string | null) => void;
}) {
  const [busy, setBusy] = useState<string | null>(null);
  const [result, setResult] = useState<IngestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function ingest(sample: string) {
    setBusy(sample);
    setError(null);
    onImage?.(null); // sample scenes have no real photo to preview
    try {
      const res = await api.ingest(sample);
      setResult(res.data);
      onIngested();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  async function ingestFile(file: File) {
    setBusy("file");
    setError(null);
    try {
      const res = await api.ingestFile(file);
      setResult(res.data);
      onImage?.(URL.createObjectURL(file)); // show the uploaded photo
      onIngested();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="card p-4">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-semibold text-slate-900">Capture fridge contents</h2>
        <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700">
          Simulated feed
        </span>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        The physical device isn&apos;t connected yet. Ingest a labeled sample scene, or upload
        an image to run the vision pipeline.
      </p>

      <div className="mt-3 flex flex-wrap gap-2">
        {SAMPLE_SCENES.map((s) => (
          <button
            key={s.id}
            onClick={() => ingest(s.id)}
            disabled={busy !== null}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-brand-500 hover:text-brand-700 disabled:opacity-50"
          >
            {busy === s.id ? "Scanning…" : s.label}
          </button>
        ))}
        <label className="cursor-pointer rounded-lg border border-dashed border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-500 transition hover:border-brand-500 hover:text-brand-700">
          {busy === "file" ? "Uploading…" : "Upload image"}
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && ingestFile(e.target.files[0])}
          />
        </label>
      </div>

      {result && (
        <div className="mt-3 space-y-2">
          <div className="rounded-lg bg-brand-50 px-3 py-2 text-xs text-brand-700">
            Detected {result.detections} items · {result.items_created} new ·{" "}
            {result.items_updated} updated — via {result.source.replace("_", " ")}
          </div>
          {result.detected_items.length > 0 && (
            <div className="rounded-lg border border-slate-100 p-3">
              <div className="mb-2 text-xs font-semibold text-slate-500">
                Vision results
              </div>
              <div className="flex flex-wrap gap-1.5">
                {result.detected_items.map((d, i) => (
                  <span
                    key={`${d.name}-${i}`}
                    className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700"
                    title={`${Math.round(d.confidence * 100)}% confidence`}
                  >
                    <span className="font-medium">{d.name}</span>
                    <span className="text-slate-400">×{d.count}</span>
                    {d.freshness != null && (
                      <span
                        className={`text-[10px] font-medium ${
                          d.freshness >= 70
                            ? "text-emerald-600"
                            : d.freshness >= 40
                            ? "text-amber-600"
                            : "text-rose-600"
                        }`}
                        title="Visual freshness"
                      >
                        {d.freshness}% fresh
                      </span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      {error && (
        <div className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">{error}</div>
      )}
    </div>
  );
}
