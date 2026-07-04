export default function SuccessPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <span className="mb-4 text-5xl">🎉</span>
      <h1 className="text-3xl font-bold">You&apos;re on the list</h1>
      <p className="mt-3 max-w-md text-slate-600">
        Thanks for reserving your spot with SYDAR AI. We&apos;ll email you as we
        get closer to launch — your deposit is fully refundable any time before
        then.
      </p>
      <a
        href="/"
        className="mt-8 rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-700"
      >
        Back to homepage
      </a>
    </main>
  );
}
