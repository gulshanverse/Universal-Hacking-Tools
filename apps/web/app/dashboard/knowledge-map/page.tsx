/* Signal Archive: private learning-state overlay over the same bounded public graph, never a second knowledge source. */
"use client";
import { DashboardShell } from "../../../components/dashboard-shell";
import { GraphExplorer } from "../../../components/graph-explorer";
export default function KnowledgeMapPage() { return <DashboardShell title="Knowledge map"><GraphExplorer initialEntity="web-security" privateMode /></DashboardShell>; }
