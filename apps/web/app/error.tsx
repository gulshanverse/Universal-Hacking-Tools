"use client";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <section className="mx-auto max-w-3xl px-6 py-24"><p className="font-mono text-sm uppercase tracking-[0.2em] text-amber-700">Request interrupted</p><h1 className="mt-4 text-4xl font-bold text-slate-950">The page could not be completed.</h1><p className="mt-4 max-w-xl text-slate-700">Please try again. If the problem continues, use the repository security and support guidance; this page intentionally does not display diagnostic details.</p><button className="mt-8 rounded-md bg-slate-950 px-5 py-3 font-semibold text-white" type="button" onClick={() => reset()}>Try again</button></section>;
}
