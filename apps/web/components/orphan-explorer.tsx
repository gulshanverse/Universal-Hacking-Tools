/* Signal Archive Phase 9: read-only reviewer context for graph gaps; suggestions never become web mutations. */
"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { clientApi, entityHref, type GraphNode } from "../lib/api";

type Row = { entity: GraphNode; reason: string; suggestions: { entity: GraphNode; shared_metadata: string[]; status: string }[] };
export function OrphanExplorer() {
  const [rows, setRows] = useState<Row[]>([]); const [message, setMessage] = useState("Loading reviewer-only graph gaps…");
  useEffect(() => { clientApi<{ items: Row[] }>("/graph/orphans?limit=100").then((value) => { setRows(value.items); setMessage(`${value.items.length} orphaned entities shown; suggestions require human review.`); }).catch((error: Error) => setMessage(error.message)); }, []);
  return <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6"><p className="mono text-[10px] tracking-[.16em] text-[var(--copper)]">READ-ONLY GRAPH GOVERNANCE</p><h1 className="display mt-2 text-4xl text-[var(--ink)]">Orphan explorer</h1><p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--slate)]">The graph has no relationship for these generated entities. Metadata overlap is only a review cue; this interface cannot create, edit, or approve a relationship.</p><p className="sr-only" aria-live="polite">{message}</p><div className="mt-8 grid gap-4">{rows.map((row) => <article className="border hairline bg-white p-5" key={row.entity.key}><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="mono text-[10px] tracking-[.14em] text-[var(--teal)]">{row.entity.type}</p><h2 className="display mt-1 text-2xl">{row.entity.name}</h2><p className="mt-2 text-sm text-[var(--slate)]">{row.reason}</p></div><Link className="border border-[var(--line)] px-3 py-2 text-sm" href={entityHref(row.entity)}>Open entity</Link></div><ul className="mt-4 grid gap-2 sm:grid-cols-2">{row.suggestions.map((item) => <li className="border-l-2 border-[var(--copper)] bg-[var(--paper-dark)] p-3 text-sm" key={item.entity.key}><strong>{item.entity.name}</strong><span className="mt-1 block text-xs text-[var(--slate)]">Shared: {item.shared_metadata.join(", ")} · {item.status}</span></li>)}</ul></article>)}</div></section>;
}
