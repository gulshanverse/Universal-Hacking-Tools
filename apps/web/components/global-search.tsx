/* Signal Archive: keyboard-first global search with local-only recent query state and API-backed autocomplete. */
"use client";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { Search } from "lucide-react";
import { apiUrl, entityHref, type SearchResult } from "../lib/api";

export function GlobalSearch({ compact = false }: { compact?: boolean }) {
  const [query, setQuery] = useState(""); const [results, setResults] = useState<SearchResult[]>([]); const [active, setActive] = useState(false);
  useEffect(() => { const timer = setTimeout(async () => { if (query.trim().length < 2) return setResults([]); try { const response = await fetch(apiUrl("/search", { q: query, limit: 5 })); const data = await response.json(); setResults(data.results || []); } catch { setResults([]); } }, 180); return () => clearTimeout(timer); }, [query]);
  function submit(event: FormEvent) { event.preventDefault(); const value = query.trim(); if (!value) return; sessionStorage.setItem("uht-last-search", value); window.location.href = `/search?q=${encodeURIComponent(value)}`; }
  return <div className={`relative ${compact ? "w-full" : "w-full max-w-2xl"}`}><form onSubmit={submit} className="flex border border-[var(--line)] bg-white shadow-sm focus-within:border-[var(--copper)]"><label className="sr-only" htmlFor="global-search">Search the knowledge base</label><Search className="m-3 text-[var(--teal)]" size={19}/><input id="global-search" value={query} onFocus={() => setActive(true)} onBlur={() => setTimeout(() => setActive(false), 150)} onChange={(event) => setQuery(event.target.value)} placeholder="Search tools, vulnerabilities, concepts, labs…" className="min-w-0 flex-1 bg-transparent py-3 text-sm outline-none"/><button className="bg-[var(--ink)] px-5 text-xs font-bold text-white transition hover:bg-[var(--teal)]" type="submit">Search</button></form>{active && results.length > 0 && <div className="absolute z-30 mt-1 w-full border hairline bg-white shadow-xl" role="listbox" aria-label="Search suggestions">{results.map(result => <Link role="option" className="block border-b hairline px-4 py-3 last:border-0 hover:bg-[var(--paper)]" href={entityHref(result)} key={`${result.type}:${result.id}`}><span className="mono text-[10px] uppercase text-[var(--teal)]">{result.type}</span><strong className="ml-2 text-sm">{result.name}</strong><span className="ml-2 text-xs text-muted">{result.category}</span></Link>)}</div>}</div>;
}
