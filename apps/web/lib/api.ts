/* Signal Archive: this client consumes only the versioned Phase 7 API; it never embeds knowledge data. */
export type Verification = { status?: string; confidence?: string; verification_method?: string; last_verified?: string };
export type Entity = {
  id: string; type: string; name: string; description?: string; category?: string; subcategory?: string;
  difficulty?: string; platforms?: string[]; security_domains?: string[]; path?: string;
  verification?: Verification; relationships?: { target: string; relationship: string }[]; sources?: Record<string, string>;
  execution_mode?: string; prerequisites?: { target: string; type: string }[];
};
export type SearchResult = Pick<Entity, "id" | "type" | "name" | "description" | "category" | "difficulty" | "path"> & { score: number; reasons: string[] };
export type ListResponse<T> = { total: number; items: T[]; limit: number; offset: number };
export type Lab = Entity & {
  execution_mode: "documentation-only" | "guided" | "executable"; safety_valid?: boolean;
  objectives?: string[]; tasks?: { id: string; description: string; evidence_id: string; hints?: { level: number; text: string }[] }[];
  evidence?: { id: string; description: string; type: string }[]; assessment_criteria?: unknown[]; safety?: Record<string, boolean | string>;
  allowed_actions?: string[]; knowledge_relationship_targets?: Record<string, string[]>;
};
export type ApiError = { error?: { code: string; message: string; details?: Record<string, unknown> } };
export type AuthSession = { authenticated: boolean; csrf_required?: boolean; user?: { id: string; status: string; email_verified: boolean; created_at: string } };
export type Goal = { id: string; name: string; learning_path_id: string; description: string; is_primary: boolean };
export type Skill = { skill: string; level: "novice" | "beginner" | "intermediate" | "advanced"; completion: number; evidence: Record<string, number> };
export type PrivateNote = { id: string; entity_id?: string | null; body: string; created_at: string; updated_at: string };

const base = process.env.NEXT_PUBLIC_API_URL || process.env.UHT_API_URL || "http://127.0.0.1:8000/api/v1";

export function apiUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(`${base}${path}`);
  for (const [key, value] of Object.entries(params || {})) if (value !== undefined && value !== "") url.searchParams.set(key, String(value));
  return url.toString();
}

export async function api<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const response = await fetch(apiUrl(path, params), { next: { revalidate: 60 } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as ApiError;
    throw new Error(body.error?.message || "The knowledge API is currently unavailable.");
  }
  return response.json() as Promise<T>;
}

function csrfToken() {
  if (typeof document === "undefined") return undefined;
  return document.cookie.split("; ").find(item => item.startsWith("uht_csrf="))?.split("=").slice(1).join("=");
}

export async function clientApi<T>(path: string, init?: RequestInit, session?: string, csrf = false): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body) headers.set("Content-Type", "application/json");
  if (session) headers.set("X-Lab-Session", session);
  if (csrf) {
    const token = csrfToken();
    if (token) headers.set("X-CSRF-Token", token);
  }
  const response = await fetch(apiUrl(path), { ...init, headers, credentials: "include" });
  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as ApiError;
    throw new Error(body.error?.message || "The requested action could not be completed.");
  }
  return response.json() as Promise<T>;
}

export const collectionPaths: Record<string, string> = {
  tool: "/tools", vulnerability: "/vulnerabilities", concept: "/concepts", technique: "/techniques",
  technology: "/technologies", "defensive-control": "/defensive-controls", lab: "/labs", "learning-path": "/learning-paths"
};

export function entityHref(entity: Pick<Entity, "id" | "type">) {
  if (entity.type === "lab") return `/labs/${entity.id}`;
  if (entity.type === "learning-path") return `/learning-paths/${entity.id}`;
  return `/${entity.type}/${entity.id}`;
}
