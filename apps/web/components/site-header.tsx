/* Signal Archive: persistent atlas index, never a dashboard sidebar; all navigation stays keyboard reachable. */
"use client";
import Link from "next/link";
import { BookOpenCheck, LogOut, Menu, Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "./auth-provider";

const groups = [
  ["Explore", "/explore"], ["Tools", "/tools"], ["Vulnerabilities", "/vulnerabilities"], ["Concepts", "/concepts"],
  ["Techniques", "/techniques"], ["Technologies", "/technologies"], ["Defensive Controls", "/defensive-controls"],
  ["Labs", "/labs"], ["Learning Paths", "/learning-paths"], ["About", "/about"]
];

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const { state, logout } = useAuth();
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); document.getElementById("global-search")?.focus(); }
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handler); return () => window.removeEventListener("keydown", handler);
  }, []);
  return <header className="sticky top-0 z-40 border-b border-white/10 bg-[var(--ink)] text-[var(--paper)] shadow-lg shadow-black/10"><div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 sm:px-6"><Link href="/" className="flex min-w-0 items-center gap-3" aria-label="Universal Hacking Tools home"><img src="/manus-storage/uht-phase7-mark_d16515de.png" alt="" className="h-10 w-10 rounded-sm bg-[var(--paper)] object-contain p-1"/><span className="min-w-0"><strong className="block text-sm tracking-[.16em]">UNIVERSAL</strong><span className="mono block text-[10px] tracking-[.22em] text-[var(--mist)]">HACKING TOOLS</span></span></Link><nav className="hidden items-center gap-5 xl:flex" aria-label="Primary navigation">{groups.slice(0,6).map(([label, href]) => <Link className="text-xs text-[var(--mist)] transition hover:text-white" href={href} key={href}>{label}</Link>)}</nav><div className="flex items-center gap-2"><Link href="/search" className="inline-flex items-center gap-2 border border-white/20 px-3 py-2 text-xs font-semibold transition hover:border-[var(--copper)] hover:text-[var(--copper)]"><Search size={15}/><span className="hidden sm:inline">Search</span><kbd className="mono hidden border border-white/20 px-1 text-[9px] text-[var(--mist)] lg:inline">⌘K</kbd></Link>{state === "authenticated" ? <><Link href="/dashboard" className="inline-flex items-center gap-2 border border-[var(--teal)] bg-[var(--teal)] px-3 py-2 text-xs font-semibold text-[var(--ink)]"><BookOpenCheck size={15}/><span className="hidden sm:inline">Learning</span></Link><button onClick={() => void logout()} className="hidden border border-white/20 p-2 text-[var(--mist)] hover:text-white sm:inline-flex" aria-label="Sign out"><LogOut size={15}/></button></> : state === "anonymous" ? <Link href="/login" className="border border-[var(--copper)] px-3 py-2 text-xs font-semibold text-[var(--copper)] hover:bg-[var(--copper)] hover:text-[var(--ink)]">Account</Link> : null}<button className="inline-flex border border-white/20 p-2 xl:hidden" aria-label={open ? "Close navigation" : "Open navigation"} aria-expanded={open} onClick={() => setOpen(!open)}>{open ? <X size={18}/> : <Menu size={18}/>}</button></div></div>{open && <nav className="border-t border-white/10 bg-[var(--ink-2)] px-4 py-4 xl:hidden" aria-label="Mobile navigation"><div className="mx-auto grid max-w-7xl grid-cols-2 gap-2">{groups.map(([label, href]) => <Link key={href} className="border border-white/10 px-3 py-2 text-xs text-[var(--paper)]" onClick={() => setOpen(false)} href={href}>{label}</Link>)}<Link className="border border-[var(--teal)] px-3 py-2 text-xs text-[var(--paper)]" onClick={() => setOpen(false)} href={state === "authenticated" ? "/dashboard" : "/login"}>{state === "authenticated" ? "Learning dashboard" : "Account"}</Link></div></nav>}</header>;
}
