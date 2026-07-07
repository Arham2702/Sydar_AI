"use client";

import { useId, useState } from "react";
import { Button } from "./Button";

const RESERVE_PRICE_LABEL = "AUD $16.99";

export default function WaitlistForm() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const emailId = useId();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong");
      window.location.href = data.url;
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md">
      <label htmlFor={emailId} className="sr-only">
        Email address
      </label>
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          id={emailId}
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@email.com"
          className="w-full flex-1 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-text outline-none focus-visible:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        />
        <Button type="submit" busy={busy}>
          {busy ? "Redirecting…" : `Reserve my spot — ${RESERVE_PRICE_LABEL}`}
        </Button>
      </div>
      {error && <p className="mt-2 text-sm text-warn">{error}</p>}
      <p className="mt-2 text-xs text-text-muted">
        Locks in 50% off for life. Fully refundable any time before launch.
      </p>
    </form>
  );
}
