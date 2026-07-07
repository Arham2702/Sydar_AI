"use client";

import { useId, useState } from "react";

export default function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();

  return (
    <div className="border-b border-border py-4 first:pt-0 last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={panelId}
        className="flex w-full items-center justify-between gap-4 text-left font-semibold text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        {q}
        <span className="shrink-0 font-mono text-lg text-text-muted" aria-hidden="true">
          {open ? "–" : "+"}
        </span>
      </button>
      {open && (
        <p id={panelId} className="mt-2 text-sm text-text-muted">
          {a}
        </p>
      )}
    </div>
  );
}
