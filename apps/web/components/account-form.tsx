/* Signal Archive: short, plain-language account forms; no credential or token is stored in browser state. */
"use client";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { clientApi } from "../lib/api";

type Mode = "login" | "register" | "verify" | "forgot" | "reset";
const copy: Record<Mode, { title: string; intro: string; action: string }> = {
  login: { title: "Return to your learning record", intro: "Your session is held in secure, server-side state. This archive does not create a public profile.", action: "Sign in" },
  register: { title: "Create a private learning record", intro: "Use an email you control. Verification instructions are delivered only through the configured account channel.", action: "Create account" },
  verify: { title: "Verify your email", intro: "Paste the one-time verification token from your delivery channel. Tokens expire and cannot be reused.", action: "Verify email" },
  forgot: { title: "Request a password reset", intro: "For privacy, the response is the same whether or not an account is eligible.", action: "Request reset" },
  reset: { title: "Choose a new password", intro: "Use your one-time reset token. Resetting a password revokes existing sessions.", action: "Reset password" }
};

export function AccountForm({ mode }: { mode: Mode }) {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const content = copy[mode];
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setBusy(true); setError(""); setMessage("");
    const form = new FormData(event.currentTarget);
    try {
      if (mode === "login") {
        await clientApi("/auth/login", { method: "POST", body: JSON.stringify({ email: form.get("email"), password: form.get("password") }) });
        window.location.assign("/dashboard"); return;
      }
      const paths: Record<Exclude<Mode, "login">, string> = { register: "/auth/register", verify: "/auth/verify-email", forgot: "/auth/request-password-reset", reset: "/auth/reset-password" };
      const body = mode === "register" ? { email: form.get("email"), password: form.get("password") } : mode === "verify" ? { token: form.get("token") } : mode === "forgot" ? { email: form.get("email") } : { token: form.get("token"), password: form.get("password") };
      const response = await clientApi<{ message?: string }>(paths[mode], { method: "POST", body: JSON.stringify(body) });
      setMessage(response.message || "Request completed.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The request could not be completed."); }
    finally { setBusy(false); }
  };
  const email = mode === "login" || mode === "register" || mode === "forgot";
  const password = mode === "login" || mode === "register" || mode === "reset";
  const token = mode === "verify" || mode === "reset";
  return <section className="mx-auto grid min-h-[62vh] max-w-7xl items-start gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[.9fr_1.1fr]"><div className="border-l-4 border-[var(--copper)] pl-5"><p className="mono text-xs uppercase tracking-[.18em] text-[var(--teal)]">Private application state</p><h1 className="serif mt-3 text-4xl text-[var(--ink)]">{content.title}</h1><p className="mt-4 max-w-md text-[var(--slate)]">{content.intro}</p></div><form onSubmit={submit} className="border border-[var(--line)] bg-white p-6 shadow-sm" aria-describedby="account-policy"><div className="space-y-5">{email && <label className="block text-sm font-semibold text-[var(--ink)]">Email address<input className="mt-2 block w-full border border-[var(--line)] px-3 py-2 text-base" required name="email" type="email" autoComplete={mode === "login" ? "username" : "email"}/></label>}{password && <label className="block text-sm font-semibold text-[var(--ink)]">Password<input className="mt-2 block w-full border border-[var(--line)] px-3 py-2 text-base" required minLength={12} name="password" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"}/></label>}{token && <label className="block text-sm font-semibold text-[var(--ink)]">One-time token<input className="mt-2 block w-full border border-[var(--line)] px-3 py-2 font-mono text-sm" required name="token" type="text" autoComplete="one-time-code"/></label>}<p id="account-policy" className="text-xs leading-5 text-[var(--slate)]">Passwords must be at least 12 characters. Do not reuse a password from another service. Verification and reset tokens are never stored in your browser.</p>{error && <p className="border-l-4 border-red-700 bg-red-50 px-3 py-2 text-sm text-red-900" role="alert">{error}</p>}{message && <p className="border-l-4 border-[var(--teal)] bg-[var(--paper-dark)] px-3 py-2 text-sm text-[var(--ink)]" role="status">{message}</p>}<button disabled={busy} className="w-full bg-[var(--ink)] px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">{busy ? "Working…" : content.action}</button></div><p className="mt-5 text-sm text-[var(--slate)]">{mode === "login" ? <><Link className="text-[var(--teal)] underline" href="/register">Create an account</Link><span> · </span><Link className="text-[var(--teal)] underline" href="/forgot-password">Forgot password?</Link></> : <Link className="text-[var(--teal)] underline" href="/login">Return to sign in</Link>}</p></form></section>;
}
