/* Signal Archive community: restrictive editorial review workspace; proposal state stays non-canonical and Git outcomes are reported exactly as returned by the server. */
"use client";

import { useEffect, useState } from "react";
import { CommunityContribution, clientApi } from "../lib/api";
import { useAuth } from "./auth-provider";

function Notice({ text, kind = "info" }: { text: string; kind?: "info" | "error" | "success" }) {
  const tone = kind === "error" ? "border-red-700 bg-red-50 text-red-900" : kind === "success" ? "border-[var(--teal)] bg-[var(--paper-dark)] text-[var(--ink)]" : "border-[var(--copper)] bg-[var(--paper-dark)] text-[var(--slate)]";
  return <p role={kind === "error" ? "alert" : "status"} className={`mt-3 border-l-2 px-3 py-2 text-sm ${tone}`}>{text}</p>;
}

function humanStatus(value: string) { return value.replaceAll("-", " "); }

export function RestrictedReviewWorkspace() {
  const { session } = useAuth();
  const role = session.user?.role;
  const allowed = role === "reviewer" || role === "maintainer" || role === "administrator";
  const canMaintain = role === "maintainer" || role === "administrator";
  const [items, setItems] = useState<CommunityContribution[]>([]);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const response = await clientApi<{ items: CommunityContribution[] }>("/community/review/contributions", { cache: "no-store" });
    setItems(response.items);
  };

  useEffect(() => { if (allowed) void load().catch(() => setError("Review queue is temporarily unavailable.")); }, [allowed]);

  const reasonFor = (prompt: string) => window.prompt(prompt)?.trim() || "";
  const update = (next: CommunityContribution) => setItems(current => current.map(item => item.id === next.id ? next : item));

  const review = async (id: string, action: "changes-requested" | "reviewer-approved" | "rejected") => {
    const reason = reasonFor("Give a specific plain-text review reason.");
    if (!reason) return;
    setBusy(true); setError("");
    try {
      update(await clientApi<CommunityContribution>(`/community/review/contributions/${id}/actions`, { method: "POST", body: JSON.stringify({ action, reason }) }, undefined, true));
      setNotice("Review action recorded in the audit trail.");
    } catch (err) { setError(err instanceof Error ? err.message : "Review action could not be recorded."); }
    finally { setBusy(false); }
  };

  const maintain = async (id: string) => {
    const reason = reasonFor("Give a specific plain-text maintainer reason.");
    if (!reason) return;
    setBusy(true); setError("");
    try {
      update(await clientApi<CommunityContribution>(`/community/maintain/contributions/${id}/actions`, { method: "POST", body: JSON.stringify({ action: "maintainer-approved", reason }) }, undefined, true));
      setNotice("Maintainer decision recorded in the audit trail. Repository knowledge remains unchanged.");
    } catch (err) { setError(err instanceof Error ? err.message : "Maintainer decision could not be recorded."); }
    finally { setBusy(false); }
  };

  const handoff = async (id: string) => {
    const reason = reasonFor("Record a specific plain-text handoff reason.");
    if (!reason) return;
    setBusy(true); setError("");
    try {
      const result = await clientApi<{ status: string; message: string }>(`/community/maintain/contributions/${id}/github-handoff`, { method: "POST", body: JSON.stringify({ confirmation: true, reason }) }, undefined, true);
      await load();
      setNotice(`Git handoff result: ${result.status}. ${result.message}`);
    } catch (err) { setError(err instanceof Error ? err.message : "Git handoff could not be recorded."); }
    finally { setBusy(false); }
  };

  if (!allowed) return <Notice text="Reviewer authorization is required for this private queue." kind="error" />;

  return <section>
    <p className="mono text-xs uppercase tracking-[.16em] text-[var(--teal)]">Restricted review queue</p>
    <h1 className="display mt-2 text-4xl">Review proposals, not canonical knowledge.</h1>
    <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--slate)]">Validation assists review but never publishes, verifies, or assigns authority automatically. Do not approve your own work. Maintainers may record a controlled server-side handoff; an unavailable provider remains a truthful failed handoff with a documented manual pull-request path.</p>
    {notice && <Notice text={notice} kind="success" />}
    {error && <Notice text={error} kind="error" />}
    {items.length === 0 && <p className="mt-7 text-sm text-[var(--slate)]">No eligible proposals are waiting in this restricted queue.</p>}
    <ol className="mt-7 grid gap-4">{items.map(item => <li className="border border-[var(--line)] bg-white p-5" key={item.id}>
      <p className="mono text-[10px] uppercase tracking-[.15em] text-[var(--copper)]">{item.type} / {humanStatus(item.status)}</p>
      <h2 className="display mt-2 text-2xl">{item.title}</h2>
      <p className="mt-2 text-sm text-[var(--slate)]">{item.description}</p>
      <p className="mt-3 text-xs text-[var(--slate)]">{item.validation?.errors?.join(" ") || item.validation?.warnings?.join(" ") || "Validation reports no blocking finding."}</p>
      {item.assigned_reviewer_id && <p className="mt-3 text-xs text-[var(--slate)]">A reviewer assignment is recorded for this proposal.</p>}
      <div className="mt-4 flex flex-wrap gap-2">
        <button disabled={busy} onClick={() => void review(item.id, "changes-requested")} className="border border-[var(--copper)] px-3 py-1.5 text-sm text-[var(--ink)] disabled:opacity-50">Request changes</button>
        <button disabled={busy} onClick={() => void review(item.id, "reviewer-approved")} className="border border-[var(--teal)] px-3 py-1.5 text-sm text-[var(--teal)] disabled:opacity-50">Recommend approval</button>
        <button disabled={busy} onClick={() => void review(item.id, "rejected")} className="border border-[var(--line)] px-3 py-1.5 text-sm text-[var(--slate)] disabled:opacity-50">Reject</button>
        {canMaintain && item.status === "under-review" && <button disabled={busy} onClick={() => void maintain(item.id)} className="border border-[var(--ink)] bg-[var(--ink)] px-3 py-1.5 text-sm text-white disabled:opacity-50">Approve for handoff</button>}
        {canMaintain && item.status === "approved" && <button disabled={busy} onClick={() => void handoff(item.id)} className="border border-[var(--ink)] bg-[var(--ink)] px-3 py-1.5 text-sm text-white disabled:opacity-50">Request controlled Git handoff</button>}
      </div>
      {item.github_handoff_status && <p className="mt-3 text-xs font-semibold text-[var(--teal)]">Recorded handoff state: {item.github_handoff_status}</p>}
    </li>)}</ol>
  </section>;
}
