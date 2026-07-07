export type FreshnessState = "fresh" | "use-soon" | "going-bad";

const CONFIG: Record<
  FreshnessState,
  { label: string; className: string; icon: React.ReactNode }
> = {
  fresh: {
    label: "Fresh",
    className: "bg-success/10 text-success",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" className="h-3.5 w-3.5" aria-hidden="true">
        <path
          d="M4 10.5 8 14l8-8"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  "use-soon": {
    label: "Use soon",
    className: "bg-warn/10 text-warn",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" className="h-3.5 w-3.5" aria-hidden="true">
        <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="2" />
        <path d="M10 6v4l3 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
  "going-bad": {
    label: "Going bad",
    className: "bg-warn text-white",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" className="h-3.5 w-3.5" aria-hidden="true">
        <path
          d="M10 3 2 17h16L10 3Z"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
        <path d="M10 8.5v3.2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        <circle cx="10" cy="14" r="0.9" fill="currentColor" />
      </svg>
    ),
  },
};

export default function FreshnessBadge({ state }: { state: FreshnessState }) {
  const { label, className, icon } = CONFIG[state];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 font-mono text-xs font-medium ${className}`}
    >
      {icon}
      {label}
    </span>
  );
}
