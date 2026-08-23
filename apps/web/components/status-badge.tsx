/* Signal Archive: verification is always an explicit text label, never color alone. */
export function StatusBadge({ status }: { status?: string }) {
  const normalized = (status || "unverified").toLowerCase().replaceAll(" ", "-");
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold capitalize status-${normalized}`}>{(status || "unverified").replaceAll("-", " ")}</span>;
}
