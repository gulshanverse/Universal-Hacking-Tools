/* Signal Archive: private dashboards remain calm field notes, not gamified control panels. */
"use client";
import Link from "next/link";
import { useEffect } from "react";
import { useAuth } from "./auth-provider";

const links = [["Overview", "/dashboard"], ["Skills", "/dashboard/skills"], ["Learning", "/dashboard/learning"], ["Knowledge map", "/dashboard/knowledge-map"], ["Contributions", "/dashboard/contributions"], ["Reputation", "/dashboard/reputation"], ["Reports", "/dashboard/reports"], ["Lab history", "/dashboard/labs"], ["Bookmarks", "/dashboard/bookmarks"], ["Private notes", "/dashboard/notes"], ["Settings", "/dashboard/settings"]];

export function DashboardShell({ title, children }: { title: string; children: React.ReactNode }) {
  const { state, session } = useAuth();
  const role = session.user?.role;
  const visibleLinks = [...links, ...(role === "reviewer" || role === "maintainer" || role === "administrator" ? [["Review queue", "/review"] as [string, string]] : []), ...(role === "administrator" ? [["Community admin", "/admin/community"] as [string, string]] : [])];
  useEffect(() => { if (state === "anonymous") window.location.assign(`/login?next=${encodeURIComponent(window.location.pathname)}`); }, [state]);
  if (state === "loading" || state === "anonymous") return <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6"><p className="mono text-sm text-[var(--slate)]">Checking your private session…</p></section>;
  return <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6"><div className="mb-8 border-b border-[var(--line)] pb-5"><p className="mono text-xs uppercase tracking-[.18em] text-[var(--teal)]">Private learning and contribution record</p><h1 className="serif mt-2 text-4xl text-[var(--ink)]">{title}</h1></div><div className="grid gap-8 lg:grid-cols-[13rem_1fr]"><nav aria-label="Dashboard navigation" className="flex gap-2 overflow-x-auto border-b border-[var(--line)] pb-3 lg:block lg:border-b-0 lg:border-r lg:pb-0">{visibleLinks.map(([label, href]) => <Link className="block shrink-0 border-l-2 border-transparent px-3 py-2 text-sm text-[var(--slate)] transition hover:border-[var(--copper)] hover:bg-[var(--paper-dark)] hover:text-[var(--ink)]" href={href} key={href}>{label}</Link>)}</nav><div className="min-w-0">{children}</div></div></section>;
}
