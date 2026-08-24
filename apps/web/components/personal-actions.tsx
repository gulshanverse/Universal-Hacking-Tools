/* Signal Archive: private actions reference public entity IDs; knowledge content remains generated and public. */
"use client";
import Link from "next/link";
import { useState } from "react";
import { clientApi } from "../lib/api";
import { useAuth } from "./auth-provider";

export function PersonalActions({ entityId }: { entityId: string }) {
  const { state } = useAuth(); const [message, setMessage] = useState("");
  if (state === "loading") return null;
  if (state === "anonymous") return <section className="border border-[var(--line)] bg-[var(--paper-dark)] p-4"><p className="mono text-[10px] tracking-[.14em] text-[var(--teal)]">PRIVATE LEARNING</p><p className="mt-2 text-sm text-[var(--slate)]"><Link className="underline" href="/login">Sign in</Link> to bookmark or record progress privately.</p></section>;
  const save = async (status: "in-progress" | "completed") => { try { await clientApi("/me/progress", { method: "PUT", body: JSON.stringify({ entity_id: entityId, status, confidence: "medium" }) }, undefined, true); setMessage(status === "completed" ? "Marked completed in your private record." : "Marked in progress in your private record."); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Private update unavailable."); } };
  return <section className="border border-[var(--line)] bg-[var(--paper-dark)] p-4"><p className="mono text-[10px] tracking-[.14em] text-[var(--teal)]">PRIVATE LEARNING</p><div className="mt-3 flex flex-wrap gap-2"><button onClick={async () => { try { await clientApi("/me/bookmarks", { method: "POST", body: JSON.stringify({ entity_id: entityId }) }, undefined, true); setMessage("Saved as a private bookmark."); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Bookmark unavailable."); } }} className="border border-[var(--ink)] px-3 py-2 text-xs font-semibold text-[var(--ink)]">Bookmark</button><button onClick={() => void save("in-progress")} className="border border-[var(--ink)] px-3 py-2 text-xs font-semibold text-[var(--ink)]">In progress</button><button onClick={() => void save("completed")} className="bg-[var(--ink)] px-3 py-2 text-xs font-semibold text-white">Completed</button></div>{message && <p className="mt-3 text-xs leading-5 text-[var(--slate)]" role="status">{message}</p>}<Link className="mt-3 inline-block text-xs text-[var(--teal)] underline" href="/dashboard/notes">Write a private note</Link></section>;
}
