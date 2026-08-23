/* Signal Archive: one collection implementation for conventional entity types, never duplicated per entity category. */
import { notFound } from "next/navigation";
import { api, collectionPaths, type Entity, type ListResponse } from "../../lib/api";
import { EntityCard } from "../../components/entity-card";
import { pageMetadata } from "../../lib/metadata";

export const dynamic = "force-dynamic";
const valid: Record<string,string> = { tool:"tools", tools:"tools", vulnerability:"vulnerabilities", vulnerabilities:"vulnerabilities", concept:"concepts", concepts:"concepts", technique:"techniques", techniques:"techniques", technology:"technologies", technologies:"technologies", "defensive-control":"defensive-controls", "defensive-controls":"defensive-controls" };
export async function generateMetadata({ params }: {params:Promise<{type:string}>}) { const {type} = await params; const title = valid[type]?.replaceAll("-"," ") || "Knowledge"; return pageMetadata(title, `Browse generated ${title} entries.`, `/${type}`); }
export default async function CollectionPage({ params, searchParams }: {params:Promise<{type:string}>; searchParams:Promise<{page?:string}>}) {
  const {type} = await params; const {page} = await searchParams; if (!valid[type]) notFound(); const current=Math.max(1,Number(page||"1")); const limit=24; const endpoint=valid[type]; const data=await api<ListResponse<Entity>>(`/${endpoint}`,{limit,offset:(current-1)*limit}).catch(()=>({total:0,items:[],limit,offset:0}));
  const title=endpoint.replaceAll("-"," "); return <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6"><p className="mono text-[10px] tracking-[.16em] text-[var(--copper)]">GENERATED COLLECTION</p><h1 className="display mt-2 capitalize text-5xl font-bold">{title}</h1><div className="mt-4 flex flex-wrap gap-3 text-sm text-muted"><span>{data.total} indexed records</span><span aria-hidden>•</span><span>page {current}</span><span aria-hidden>•</span><span>API-backed pagination</span></div><div className="mt-9 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{data.items.map(item=><EntityCard entity={item} key={item.id}/>)}</div></section>;
}
