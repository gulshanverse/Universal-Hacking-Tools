import Link from "next/link";

export const metadata = { title: "Access limited | Universal Hacking Tools", robots: { index: false, follow: false } };

export default function AccessDeniedPage() {
  return <section className="mx-auto max-w-3xl px-6 py-24"><p className="font-mono text-sm uppercase tracking-[0.2em] text-rose-700">403 · Access limited</p><h1 className="mt-4 text-4xl font-bold text-slate-950">This action is not available to this session.</h1><p className="mt-4 max-w-xl text-slate-700">Sign in with an authorized account or return to public knowledge. The page does not reveal role, account, or resource details.</p><Link className="mt-8 inline-flex rounded-md bg-slate-950 px-5 py-3 font-semibold text-white" href="/">Return to the knowledge archive</Link></section>;
}
