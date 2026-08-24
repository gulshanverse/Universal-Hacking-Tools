/* Signal Archive Phase 9: an atlas-like bounded SVG enhancement with a first-class accessible relationship table. */
"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { clientApi, entityHref, graphHref, type GraphNeighborhood, type GraphNode, type GraphPath, type GraphRelationship, type SearchResult } from "../lib/api";

const TYPE_OPTIONS = ["all", "tool", "vulnerability", "concept", "technique", "technology", "defensive-control", "lab", "learning-path"];
const TRUST_OPTIONS = ["all", "verified", "partially-verified", "needs-review", "unverified"];
const RELATIONSHIP_OPTIONS = ["all", "requires-prerequisite-required", "requires-prerequisite-recommended", "uses-tool", "uses-technology", "mitigated-by", "demonstrates-vulnerability", "teaches-concept", "belongs-to-learning-path", "related-to-concept"];
const TYPE_MARK: Record<string, string> = { tool: "◆", vulnerability: "▲", concept: "●", technique: "■", technology: "⬡", "defensive-control": "✚", lab: "▣", "learning-path": "▤" };

function query(values: Record<string, string | number | undefined>) {
  return new URLSearchParams(Object.entries(values).filter(([, value]) => value !== undefined && value !== "").map(([key, value]) => [key, String(value)])).toString();
}

function nodePosition(index: number, total: number) {
  if (!index) return { x: 50, y: 50 };
  const angle = ((index - 1) / Math.max(1, total - 1)) * Math.PI * 2 - Math.PI / 2;
  return { x: 50 + Math.cos(angle) * 34, y: 50 + Math.sin(angle) * 34 };
}

export function GraphExplorer({ initialEntity = "nmap", privateMode = false }: { initialEntity?: string; privateMode?: boolean }) {
  const [entity, setEntity] = useState(initialEntity);
  const [search, setSearch] = useState(initialEntity);
  const [depth, setDepth] = useState(1);
  const [type, setType] = useState("all");
  const [trust, setTrust] = useState("all");
  const [relationship, setRelationship] = useState("all");
  const [suggestions, setSuggestions] = useState<(SearchResult & { match_type?: string; graph_reason?: string })[]>([]);
  const [data, setData] = useState<GraphNeighborhood | null>(null);
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [pathTarget, setPathTarget] = useState("");
  const [path, setPath] = useState<GraphPath | null>(null);
  const [status, setStatus] = useState("Choose a generated knowledge entity to inspect a bounded neighborhood.");
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  useEffect(() => {
    let active = true;
    setStatus("Loading bounded graph neighborhood…");
    clientApi<GraphNeighborhood>(`/graph/neighborhood?${query({ entity, depth, limit: 100, edge_limit: 200, entity_type: type === "all" ? undefined : type, relationship_type: relationship === "all" ? undefined : relationship, trust_status: trust === "all" ? undefined : trust })}`)
      .then((payload) => { if (active) { setData(payload); setSelected(payload.center); setStatus(`Selected ${payload.center.name}. ${payload.nodes.length} bounded graph nodes loaded.`); } })
      .catch((error: Error) => { if (active) { setData(null); setSelected(null); setStatus(error.message); } });
    return () => { active = false; };
  }, [entity, depth, type, trust, relationship, privateMode]);

  useEffect(() => {
    const value = search.trim();
    if (value.length < 2) { setSuggestions([]); return; }
    let active = true;
    const timer = window.setTimeout(() => clientApi<{ results: (SearchResult & { match_type?: string; graph_reason?: string })[] }>(`/search?${query({ q: value, graph_context: "true", limit: 5 })}`).then((payload) => { if (active) setSuggestions(payload.results); }).catch(() => { if (active) setSuggestions([]); }), 180);
    return () => { active = false; window.clearTimeout(timer); };
  }, [search]);

  const positions = useMemo(() => Object.fromEntries((data?.nodes || []).map((node, index, nodes) => [node.key, nodePosition(index, nodes.length)])), [data]);
  const selectedEdges = useMemo(() => (data?.relationships || []).filter((edge) => edge.source === selected?.key || edge.target === selected?.key), [data, selected]);

  function submitSearch(event: FormEvent) {
    event.preventDefault();
    const next = search.trim();
    if (next) { setEntity(next); setSuggestions([]); setPath(null); setPan({ x: 0, y: 0 }); setZoom(1); }
  }

  function findPath(event: FormEvent) {
    event.preventDefault();
    if (!pathTarget.trim()) return;
    clientApi<GraphPath>(`/graph/path?${query({ from: entity, to: pathTarget.trim(), max_length: 25 })}`)
      .then((payload) => { setPath(payload); setStatus(payload.found ? `Path found with ${payload.relationships.length} relationships.` : "No bounded directed path was found."); })
      .catch((error: Error) => setStatus(error.message));
  }

  const reset = () => { setDepth(1); setType("all"); setTrust("all"); setRelationship("all"); setPath(null); setPan({ x: 0, y: 0 }); setZoom(1); setStatus("Graph controls reset to the default bounded view."); };

  return <section className="space-y-5" aria-labelledby="graph-explorer-title">
    <div className="border hairline bg-[var(--ink)] p-5 text-[var(--paper)]">
      <p className="mono text-[10px] tracking-[.16em] text-[var(--copper)]">DETERMINISTIC KNOWLEDGE ATLAS</p>
      <div className="mt-2 flex flex-wrap items-end justify-between gap-4"><div><h1 id="graph-explorer-title" className="display text-3xl sm:text-4xl">Bounded graph explorer</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--mist)]">The atlas reads the committed generated graph. It expands at most four hops and 100 nodes; it never scans systems, triggers labs, or changes repository knowledge.</p></div>{data && <dl className="mono grid grid-cols-2 gap-x-5 gap-y-1 text-[10px] text-[var(--mist)]"><div><dt>GRAPH</dt><dd className="text-[var(--paper)]">{data.graph_version}</dd></div><div><dt>KNOWLEDGE</dt><dd className="text-[var(--paper)]">{data.knowledge_version}</dd></div></dl>}</div>
    </div>
    <div className="grid gap-4 border hairline bg-white p-4 lg:grid-cols-[1.5fr_.8fr]">
      <form onSubmit={submitSearch} className="relative flex flex-wrap items-end gap-3"><label className="min-w-52 flex-1 text-sm font-medium">Search graph<input value={search} onChange={(event) => setSearch(event.target.value)} className="mt-1 w-full border border-[var(--line)] bg-[var(--paper)] px-3 py-2 text-[var(--ink)]" placeholder="Search graph…" aria-label="Search graph by generated entity name or identifier" aria-controls="graph-search-results" /></label><button className="border border-[var(--teal)] bg-[var(--teal)] px-4 py-2 text-sm font-semibold text-white transition motion-reduce:transition-none hover:bg-[var(--ink)]" type="submit">Focus graph</button>{suggestions.length > 0 && <ul id="graph-search-results" className="absolute left-0 top-full z-10 mt-1 max-h-56 w-full overflow-auto border border-[var(--line)] bg-white shadow-lg" aria-label="Graph search results">{suggestions.map((item) => <li key={`${item.type}:${item.id}`}><button type="button" className="block w-full px-3 py-2 text-left text-sm hover:bg-[var(--paper-dark)]" onClick={() => { setEntity(item.id); setSearch(item.name); setSuggestions([]); setStatus(`Focused graph on ${item.name}.`); }}><span className="mono mr-2 text-[10px] text-[var(--teal)]">{item.match_type || "direct"}</span>{item.name}<span className="ml-2 text-xs text-[var(--slate)]">{item.type}</span></button></li>)}</ul>}</form>
      <form onSubmit={findPath} className="flex items-end gap-2"><label className="min-w-0 flex-1 text-sm font-medium">Path target<input value={pathTarget} onChange={(event) => setPathTarget(event.target.value)} className="mt-1 w-full border border-[var(--line)] bg-[var(--paper)] px-3 py-2 text-[var(--ink)]" placeholder="e.g. firewall" /></label><button className="border border-[var(--copper)] px-3 py-2 text-sm font-semibold text-[var(--ink)] transition motion-reduce:transition-none hover:bg-[var(--copper)] hover:text-white" type="submit">Find path</button></form>
      <div className="flex flex-wrap items-end gap-3 lg:col-span-2"><label className="text-sm font-medium">Depth<select value={depth} onChange={(event) => setDepth(Number(event.target.value))} className="ml-2 border border-[var(--line)] bg-white px-2 py-2 text-[var(--ink)]">{[1, 2, 3, 4].map((value) => <option value={value} key={value}>Depth {value}</option>)}</select></label><label className="text-sm font-medium">Type<select value={type} onChange={(event) => setType(event.target.value)} className="ml-2 border border-[var(--line)] bg-white px-2 py-2 text-[var(--ink)]">{TYPE_OPTIONS.map((value) => <option value={value} key={value}>{value === "all" ? "All types" : value}</option>)}</select></label><label className="text-sm font-medium">Relationship<select value={relationship} onChange={(event) => setRelationship(event.target.value)} className="ml-2 border border-[var(--line)] bg-white px-2 py-2 text-[var(--ink)]">{RELATIONSHIP_OPTIONS.map((value) => <option value={value} key={value}>{value === "all" ? "All relationships" : value}</option>)}</select></label><label className="text-sm font-medium">Trust<select value={trust} onChange={(event) => setTrust(event.target.value)} className="ml-2 border border-[var(--line)] bg-white px-2 py-2 text-[var(--ink)]">{TRUST_OPTIONS.map((value) => <option value={value} key={value}>{value === "all" ? "All states" : value}</option>)}</select></label><div className="ml-auto flex gap-2"><button className="border border-[var(--line)] px-3 py-2 text-sm" type="button" onClick={() => setZoom((value) => Math.min(1.4, Number((value + .1).toFixed(1))))}>Zoom in</button><button className="border border-[var(--line)] px-3 py-2 text-sm" type="button" onClick={() => setZoom((value) => Math.max(.7, Number((value - .1).toFixed(1))))}>Zoom out</button><button className="border border-[var(--line)] px-3 py-2 text-sm" type="button" onClick={reset}>Reset</button></div></div>
    </div>
    <p className="sr-only" aria-live="polite">{status}</p>
    {data?.truncated && <p className="border-l-4 border-[var(--copper)] bg-[var(--paper-dark)] px-4 py-3 text-sm text-[var(--ink)]" role="status">Showing a bounded subset of potentially more related entities. Refine filters or choose a smaller depth.</p>}
    <div className="grid gap-5 xl:grid-cols-[1.55fr_.75fr]">
      <div className="overflow-hidden border hairline bg-[var(--ink)] p-3 text-[var(--paper)]"><div className="mb-2 flex items-center justify-between"><p className="mono text-[10px] tracking-[.14em] text-[var(--mist)]">VISUAL MAP — POINTER SELECTION; TABLE BELOW FOR KEYBOARD</p><div className="grid grid-cols-3 gap-1"><span /><button type="button" aria-label="Pan graph up" className="border border-white/20 px-2 py-1 text-xs" onClick={() => setPan((value) => ({ ...value, y: value.y - 3 }))}>↑</button><span /><button type="button" aria-label="Pan graph left" className="border border-white/20 px-2 py-1 text-xs" onClick={() => setPan((value) => ({ ...value, x: value.x - 3 }))}>←</button><span /><button type="button" aria-label="Pan graph right" className="border border-white/20 px-2 py-1 text-xs" onClick={() => setPan((value) => ({ ...value, x: value.x + 3 }))}>→</button><span /><button type="button" aria-label="Pan graph down" className="border border-white/20 px-2 py-1 text-xs" onClick={() => setPan((value) => ({ ...value, y: value.y + 3 }))}>↓</button><span /></div></div><svg viewBox="0 0 100 100" className="atlas-grid h-[25rem] w-full touch-pan-y" aria-hidden="true"><g transform={`translate(${pan.x} ${pan.y}) scale(${zoom})`} className="transition-transform duration-200 motion-reduce:transition-none">{(data?.relationships || []).map((edge, index) => { const from = positions[edge.source], to = positions[edge.target]; return from && to ? <line key={`${edge.source}-${edge.relationship}-${edge.target}-${index}`} x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke="rgba(239,230,213,.28)" strokeWidth=".38" /> : null; })}{(data?.nodes || []).map((node) => { const pos = positions[node.key]; const active = node.key === selected?.key; return <g key={node.key} transform={`translate(${pos.x} ${pos.y})`} onClick={() => { setSelected(node); setStatus(`Selected ${node.name}, ${node.type}.`); }} className="cursor-pointer"><circle r={active ? 5.5 : 4.2} fill={active ? "#c7794a" : "#176b6b"} stroke="#f4efe6" strokeWidth=".4" /><text y="1.25" textAnchor="middle" fontSize="5" fill="#f4efe6">{TYPE_MARK[node.type] || "•"}</text><text y="8" textAnchor="middle" fontSize="2.7" fill="#f4efe6">{node.name.slice(0, 16)}</text></g>; })}</g></svg></div>
      <aside className="border hairline bg-white p-5" aria-labelledby="node-panel-title"><p className="mono text-[10px] tracking-[.15em] text-[var(--teal)]">SELECTED NODE</p>{selected ? <><h2 id="node-panel-title" className="display mt-2 text-3xl text-[var(--ink)]">{selected.name}</h2><p className="mt-1 text-sm text-[var(--slate)]"><span aria-hidden="true">{TYPE_MARK[selected.type]}</span> {selected.type} · {selected.difficulty || "difficulty not classified"}</p><p className="mt-4 text-sm leading-6 text-[var(--slate)]">{selected.description || "No generated description is available."}</p><dl className="mt-5 border-y border-[var(--line)] py-3 text-sm"><div className="flex justify-between gap-3"><dt className="text-[var(--slate)]">Verification</dt><dd>{selected.verification?.status || "unknown"}</dd></div><div className="mt-2 flex justify-between gap-3"><dt className="text-[var(--slate)]">Learning state</dt><dd>{selected.learning_state || "knowledge-only"}</dd></div></dl><div className="mt-5 flex flex-wrap gap-2"><Link className="border border-[var(--teal)] bg-[var(--teal)] px-3 py-2 text-sm font-semibold text-white" href={entityHref(selected)}>Open entity</Link><Link className="border border-[var(--line)] px-3 py-2 text-sm font-semibold text-[var(--ink)]" href={graphHref(selected, depth)}>Share explorer</Link></div><h3 className="mono mt-6 text-[10px] tracking-[.14em] text-[var(--slate)]">DIRECT RELATIONSHIPS</h3><ul className="mt-2 space-y-2 text-sm">{selectedEdges.slice(0, 8).map((edge: GraphRelationship) => <li key={`${edge.source}-${edge.relationship}-${edge.target}`} className="border-l-2 border-[var(--copper)] pl-2"><span className="font-medium">{edge.relationship}</span><br /><span className="text-xs text-[var(--slate)]">{edge.explanation?.why || "Explanation unavailable; relationship requires human review."}</span></li>)}</ul></> : <p id="node-panel-title" className="mt-4 text-sm text-[var(--slate)]">Select a node from the map or accessible table.</p>}</aside>
    </div>
    {path && <section className="border hairline bg-[var(--paper-dark)] p-5" aria-labelledby="path-title"><p className="mono text-[10px] tracking-[.15em] text-[var(--copper)]">PATH MODE</p><h2 id="path-title" className="display mt-1 text-2xl">{path.found ? "Shortest generated relationship path" : "No bounded path found"}</h2>{path.found && <ol className="mt-4 grid gap-3 md:grid-cols-2">{path.path.map((node, index) => <li className="border border-[var(--line)] bg-white p-3" key={node.key}><span className="mono text-[10px] text-[var(--teal)]">{index + 1} · {node.type}</span><strong className="mt-1 block">{node.name}</strong><span className="mt-2 block text-xs text-[var(--slate)]">{index ? path.relationships[index - 1]?.why : "Selected path origin."}</span></li>)}</ol>}</section>}
    <section className="border hairline bg-white p-5" aria-labelledby="accessible-graph-title"><p className="mono text-[10px] tracking-[.15em] text-[var(--teal)]">ACCESSIBLE RELATIONSHIP EXPLORER</p><h2 id="accessible-graph-title" className="display mt-1 text-2xl text-[var(--ink)]">Structured graph list</h2><p className="mt-2 text-sm text-[var(--slate)]">Use these conventional controls for every core graph action. The visual map is supplementary.</p><div className="mt-4 overflow-x-auto"><table className="w-full min-w-[42rem] text-left text-sm"><caption className="sr-only">Bounded graph entities and their relationship distance</caption><thead className="mono text-[10px] uppercase tracking-[.12em] text-[var(--slate)]"><tr><th className="pb-2">Select</th><th className="pb-2">Entity</th><th className="pb-2">Type</th><th className="pb-2">Trust</th><th className="pb-2">Distance</th><th className="pb-2">Open</th></tr></thead><tbody>{(data?.nodes || []).map((node) => <tr className="border-t border-[var(--line)]" key={`table-${node.key}`}><td className="py-3"><button className="border border-[var(--line)] px-2 py-1 text-xs hover:border-[var(--teal)]" onClick={() => { setSelected(node); setStatus(`Selected ${node.name}, ${node.type}.`); }}>Select</button></td><td className="py-3 font-medium">{node.name}</td><td className="py-3"><span aria-hidden="true">{TYPE_MARK[node.type]}</span> {node.type}</td><td className="py-3">{node.verification?.status || "unknown"}</td><td className="py-3">{node.distance ?? 0}</td><td className="py-3"><Link className="text-[var(--teal)] underline underline-offset-2" href={entityHref(node)}>Entity</Link></td></tr>)}</tbody></table></div></section>
  </section>;
}
