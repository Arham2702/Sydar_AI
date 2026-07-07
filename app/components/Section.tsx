import type { ReactNode } from "react";

export default function Section({
  children,
  id,
  bg = "default",
  className = "",
}: {
  children: ReactNode;
  id?: string;
  bg?: "default" | "muted";
  className?: string;
}) {
  return (
    <section
      id={id}
      className={bg === "muted" ? "border-y border-border bg-surface" : undefined}
    >
      <div className={`mx-auto max-w-6xl px-6 py-16 sm:py-24 ${className}`}>
        {children}
      </div>
    </section>
  );
}
