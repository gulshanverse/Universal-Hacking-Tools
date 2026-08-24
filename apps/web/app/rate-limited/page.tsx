import Link from "next/link";

export const metadata = { title: "Please retry shortly | Universal Hacking Tools", robots: { index: false, follow: false } };

export default function RateLimitedPage() {
  return <section className="mx-auto max-w-3xl px-6 py-24"><p className="font-mono text-sm uppercase tracking-[0.2em] text-amber-700">429 · Request limit</p><h1 className="mt-4 text-4xl font-bold text-slate-950">Please wait before trying again.</h1><p className="mt-4 max-w-xl text-slate-700">The service has temporarily limited repeated requests to protect availability. No account activity or enforcement detail is disclosed.</p><Link className="mt-8 inline-flex rounded-md bg-slate-950 px-5 py-3 font-semibold text-white" href="/">Return to the knowledge archive</Link></section>;
}
