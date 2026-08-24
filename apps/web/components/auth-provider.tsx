/* Signal Archive: browser state holds only display state; session authority remains HttpOnly server cookies. */
"use client";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { AuthSession, clientApi } from "../lib/api";

type AuthContextValue = { state: "loading" | "anonymous" | "authenticated"; session: AuthSession; refresh: () => Promise<void>; logout: () => Promise<void> };
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<AuthSession>({ authenticated: false });
  const [state, setState] = useState<AuthContextValue["state"]>("loading");
  const refresh = async () => {
    setState("loading");
    try { const next = await clientApi<AuthSession>("/auth/session", { method: "GET", cache: "no-store" }); setSession(next); setState(next.authenticated ? "authenticated" : "anonymous"); }
    catch { setSession({ authenticated: false }); setState("anonymous"); }
  };
  const logout = async () => { try { await clientApi("/auth/logout", { method: "POST" }, undefined, true); } finally { await refresh(); } };
  useEffect(() => { void refresh(); }, []);
  const value = useMemo(() => ({ state, session, refresh, logout }), [state, session]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("AuthProvider is required");
  return value;
}
