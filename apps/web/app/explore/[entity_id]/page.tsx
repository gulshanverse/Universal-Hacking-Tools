/* Signal Archive: shareable entity-centered graph exploration remains public, bounded, and knowledge-only by default. */
import { GraphExplorer } from "../../../components/graph-explorer";
import { pageMetadata } from "../../../lib/metadata";

export const dynamic = "force-dynamic";
export const metadata = pageMetadata("Entity graph explorer", "Inspect a bounded generated relationship neighborhood.", "/explore");
export default async function EntityGraphPage({ params }: { params: Promise<{ entity_id: string }> }) {
  const { entity_id } = await params;
  return <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6"><GraphExplorer initialEntity={entity_id} /></section>;
}
