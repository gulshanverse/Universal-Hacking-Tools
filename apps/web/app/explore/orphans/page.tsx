/* Signal Archive: reviewer-only orphan reference; intentionally noindex and no mutation controls. */
import type { Metadata } from "next";
import { OrphanExplorer } from "../../../components/orphan-explorer";
export const metadata: Metadata = { title: "Orphan graph review | Universal Hacking Tools", robots: { index: false, follow: false } };
export default function OrphansPage() { return <OrphanExplorer />; }
