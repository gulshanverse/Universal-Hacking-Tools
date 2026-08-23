/* Signal Archive: learning routes render only API-supplied progression metadata and do not record learner progress. */
import { api, type Entity, type ListResponse } from "../../lib/api";
import { EntityCard } from "../../components/entity-card";
import { pageMetadata } from "../../lib/metadata";

export const dynamic = "force-dynamic";
export const metadata = pageMetadata("Learning paths", "Explore explicit cybersecurity learning progression.", "/learning-paths");
export default async function LearningPathsPage() { const data=await api<ListResponse<Entity>>("/learning-paths",{limit:30}).catch(()=>({total:0,items:[],limit:30,offset:0})); return <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6"><p className="mono text-[10px] tracking-[.16em] text-[var(--copper)]">LEARNING PATHS</p><h1 className="display mt-2 text-5xl font-bold">Progress through explicit foundations.</h1><p className="mt-4 max-w-3xl text-muted">Learning path content is generated from repository sources. Progress is not stored, inferred, or associated with an account in Phase 7.</p><div className="mt-9 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{data.items.map(item=><EntityCard entity={item} key={item.id}/>)}</div></section>; }
