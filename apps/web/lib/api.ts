/* Signal Archive: this client consumes only the versioned Phase 7 API; it never embeds knowledge data. */
export type Verification = { status?: string; confidence?: string; verification_method?: string; last_verified?: string };
export type Entity = {
  id: string; type: string; name: string; description?: string; category?: string; subcategory?: string;
  difficulty?: string; platforms?: string[]; security_domains?: string[]; path?: string;
  verification?: Verification; relationships?: { target: string; relationship: string }[]; sources?: Record<string, string>;
  execution_mode?: string; prerequisites?: { target: string; type: string }[];
};
export type SearchResult = Pick<Entity, "id" | "type" | "name" | "description" | "category" | "difficulty" | "path"> & { score: number; reasons: string[] };
export type GraphSearchResult = SearchResult & { match_type?: "direct" | "related"; graph_reason?: string };
export type ListResponse<T> = { total: number; items: T[]; limit: number; offset: number };
export type Lab = Entity & {
  execution_mode: "documentation-only" | "guided" | "executable"; safety_valid?: boolean;
  objectives?: string[]; tasks?: { id: string; description: string; evidence_id: string; hints?: { level: number; text: string }[] }[];
  evidence?: { id: string; description: string; type: string }[]; assessment_criteria?: unknown[]; safety?: Record<string, boolean | string>;
  allowed_actions?: string[]; knowledge_relationship_targets?: Record<string, string[]>;
};
export type ApiError = { error?: { code: string; message: string; details?: Record<string, unknown> } };
export type AuthSession = { authenticated: boolean; csrf_required?: boolean; user?: { id: string; status: string; role?: "contributor" | "reviewer" | "maintainer" | "administrator"; email_verified: boolean; created_at: string } };
export type CommunityProfile = { username: string; display_name?: string | null; bio?: string | null; avatar_url?: string | null; website_url?: string | null; github_username?: string | null; joined_at?: string; contribution_count?: number; contribution_categories?: Record<string, number>; approved_contributions?: number; reputation?: number; contributor_level?: string; expertise_areas?: string[]; badges?: string[]; reputation_note?: string; is_public?: boolean; is_hidden?: boolean; created_at?: string };
export type CommunityContribution = { id: string; type: string; title: string; description: string; status: string; created_at: string; updated_at?: string; submitted_at?: string | null; reviewed_at?: string | null; merged_at?: string | null; published_at?: string | null; author?: string | null; github_pr_url?: string | null; proposed_content_label?: string; proposed_data?: Record<string, unknown>; validation?: { valid?: boolean; quality_score?: number; missing_fields?: string[]; errors?: string[]; warnings?: string[] }; duplicate_candidates?: { entity_id: string; entity_type: string; name: string; reason: string }[]; impact?: Record<string, unknown>; versions?: { version: number; summary: string; description: string; proposed_data: Record<string, unknown>; created_at: string }[]; reviews?: { action: string; reason: string; created_at: string }[]; comments?: { body: string; created_at: string }[]; reviewer_recommendations?: { reviewer_id: string; role: string; expertise_matches: number; open_workload: number; score: number; reason: string }[]; assigned_reviewer_id?: string | null; github_handoff_status?: string | null };
export type CommunityOpportunity = { kind: string; entity_id?: string; entity_type?: string; title: string; priority: string; reason: string };
export type CommunityReport = { id: string; entity_id?: string | null; type: string; description: string; status: string; is_security_report: boolean; created_at: string; resolved_at?: string | null; resolution?: string | null };
export type Goal = { id: string; name: string; learning_path_id: string; description: string; is_primary: boolean };
export type Skill = { skill: string; level: "novice" | "beginner" | "intermediate" | "advanced"; completion: number; evidence: Record<string, number> };
export type PrivateNote = { id: string; entity_id?: string | null; body: string; created_at: string; updated_at: string };
export type GraphNode = Entity & { key: string; distance?: number; learning_state?: string };
export type GraphRelationship = { source: string; target: string; relationship: string; explanation?: { why: string; confidence: string; evidence: string } };
export type GraphNeighborhood = { knowledge_version: string; graph_version: string; generated_at: string; center: GraphNode; nodes: GraphNode[]; relationships: GraphRelationship[]; depth: number; limit: number; edge_limit: number; truncated: boolean; personalization?: { progress_overlay: boolean } };
export type GraphPath = { found: boolean; path: GraphNode[]; relationships: { source: string; target: string; relationship_type: string; why: string; confidence: string }[] };

const production = process.env.UHT_ENVIRONMENT === "production";
const base = process.env.NEXT_PUBLIC_API_URL || (production ? undefined : "http://127.0.0.1:8000/api/v1");

if (!base) throw new Error("NEXT_PUBLIC_API_URL must be configured for a production browser build");
const baseUrl = new URL(base);
if (baseUrl.username || baseUrl.password || (production && baseUrl.protocol !== "https:")) throw new Error("NEXT_PUBLIC_API_URL must be a credential-free public HTTPS URL in production");

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

export function graphHref(entity: Pick<Entity, "id">, depth = 1) {
  return `/explore/${entity.id}?depth=${depth}`;
}
