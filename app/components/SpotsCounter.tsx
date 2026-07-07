const COHORT_CAP = 250;
// Manually updated for now — there's no order database yet, only Stripe.
// Follow-up: back this with a count of completed checkout sessions.
const SPOTS_RESERVED = 41;

export default function SpotsCounter() {
  const pct = Math.round((SPOTS_RESERVED / COHORT_CAP) * 100);

  return (
    <div className="w-full max-w-xs">
      <div className="flex items-baseline justify-between font-mono text-sm">
        <span className="font-semibold text-text">
          {SPOTS_RESERVED} of {COHORT_CAP}
        </span>
        <span className="text-text-muted">reserved</span>
      </div>
      <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-border">
        <div
          className="h-full rounded-full bg-accent"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
