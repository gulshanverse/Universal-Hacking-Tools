/* Signal Archive: reusable source-backed entity preview; details always route through the API-backed page system. */
import Link from "next/link";
import type { Entity } from "../lib/api";
import { entityHref } from "../lib/api";
import { StatusBadge } from "./status-badge";

export function EntityCard({ entity, score }: { entity: Entity; score?: number }) {
  return <article className="rise group border hairline bg-white/70 p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--teal)] hover:shadow-md"><div className="flex items-start justify-between gap-3"><p className="mono text-[10px] uppercase tracking-[.14em] text-[var(--teal)]">{entity.type.replaceAll("-", " ")}</p>{score !== undefined && <span className="mono text-[10px] text-muted">score {score}</span>}</div><h3 className="display mt-3 text-xl font-bold group-hover:text-[var(--teal)]"><Link href={entityHref(entity)}>{entity.name}</Link></h3><p className="mt-2 line-clamp-3 text-sm leading-6 text-muted">{entity.description || "Generated repository metadata is available for this entry."}</p><div className="mt-4 flex flex-wrap items-center gap-2"><StatusBadge status={entity.verification?.status}/>{entity.category && <span className="mono text-[10px] text-muted">{entity.category}</span>}{entity.difficulty && <span className="mono text-[10px] text-muted">{entity.difficulty}</span>}</div></article>;
}
