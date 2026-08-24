import Link from "next/link";

export const metadata = { title: "Page not found | Universal Hacking Tools", robots: { index: false, follow: false } };

export default function NotFound() {
  return <section className="mx-auto max-w-3xl px-6 py-24"><p className="font-mono text-sm uppercase tracking-[0.2em] text-cyan-700">404 · Archive route unavailable</p><h1 className="mt-4 text-4xl font-bold text-slate-950">This page is not available.</h1><p className="mt-4 max-w-xl text-slate-700">The address may be outdated, or the requested resource may not be public. No account or system details are disclosed here.</p><Link className="mt-8 inline-flex rounded-md bg-slate-950 px-5 py-3 font-semibold text-white" href="/">Return to the knowledge archive</Link></section>;
}
