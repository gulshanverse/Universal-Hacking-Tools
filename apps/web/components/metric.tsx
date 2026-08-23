/* Signal Archive: compact metric blocks make generated limits visible instead of promotional. */
export function Metric({ label, value, detail }: { label: string; value: string | number; detail?: string }) {
  return <article className="border-l-2 border-[var(--copper)] bg-white/50 px-4 py-3"><p className="mono text-[10px] uppercase tracking-[.14em] text-muted">{label}</p><p className="display mt-1 text-3xl font-bold">{value}</p>{detail && <p className="mt-1 text-xs text-muted">{detail}</p>}</article>;
}
