import { LinkButton } from "../components/Button";

export default function SuccessPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-bg px-6 text-center">
      <span className="mb-4 text-5xl" aria-hidden="true">
        🎉
      </span>
      <h1 className="font-display text-3xl font-semibold text-text">You&apos;re reserved.</h1>
      <p className="mt-3 max-w-md text-text-muted">
        You&apos;ve got one of 250 founding spots and locked in 50% off for life
        for AUD $16.99 — fully refundable any time before launch. We&apos;ll
        email you as we get closer to shipping.
      </p>
      <LinkButton href="/" className="mt-8">
        Back to homepage
      </LinkButton>
    </main>
  );
}
