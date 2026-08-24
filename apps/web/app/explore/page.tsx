/* Signal Archive: the public graph atlas shows bounded generated relationships with a list-first accessible alternative. */
import { GraphExplorer } from "../../components/graph-explorer";
import { pageMetadata } from "../../lib/metadata";

export const dynamic = "force-dynamic";
export const metadata = pageMetadata("Knowledge graph explorer", "Inspect strictly bounded generated cybersecurity knowledge relationships.", "/explore");
export default async function ExplorePage() {
  return <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6"><GraphExplorer /></section>;
}
