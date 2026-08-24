import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = new URL("..", import.meta.url).pathname;
const required = ["app/page.tsx", "app/search/page.tsx", "app/explore/page.tsx", "app/[type]/page.tsx", "app/[type]/[id]/page.tsx", "app/labs/page.tsx", "app/labs/[id]/page.tsx", "app/learning-paths/page.tsx", "app/learning-paths/[id]/page.tsx", "app/about/health/page.tsx", "app/contribute/page.tsx", "app/community/page.tsx", "app/community/[username]/page.tsx", "app/community/contributions/[id]/page.tsx"];
const privateRoutes = ["app/login/page.tsx", "app/register/page.tsx", "app/verify-email/page.tsx", "app/forgot-password/page.tsx", "app/reset-password/page.tsx", "app/dashboard/page.tsx", "app/dashboard/skills/page.tsx", "app/dashboard/learning/page.tsx", "app/dashboard/knowledge-map/page.tsx", "app/dashboard/contributions/page.tsx", "app/dashboard/reputation/page.tsx", "app/dashboard/reports/page.tsx", "app/dashboard/labs/page.tsx", "app/dashboard/bookmarks/page.tsx", "app/dashboard/notes/page.tsx", "app/dashboard/settings/page.tsx", "app/review/page.tsx", "app/admin/community/page.tsx"];
const graphRoutes = ["app/explore/[entity_id]/page.tsx", "app/explore/orphans/page.tsx", "components/graph-explorer.tsx", "components/orphan-explorer.tsx"];

test("required public Phase 7 pages exist", () => required.forEach(file => assert.equal(existsSync(join(root,file)), true, file)));
test("required private Phase 8 account and dashboard routes exist", () => privateRoutes.forEach(file => assert.equal(existsSync(join(root,file)), true, file)));
test("required Phase 9 graph explorer and reviewer routes exist", () => graphRoutes.forEach(file => assert.equal(existsSync(join(root,file)), true, file)));
test("web client consumes the versioned API rather than hardcoded entity collections", () => {
  const api = readFileSync(join(root,"lib/api.ts"),"utf8");
  assert.match(api,/api\/v1|NEXT_PUBLIC_API_URL/);
  assert.doesNotMatch(api,/const tools\s*=\s*\[/);
});
test("safe lab interface contains no terminal, arbitrary command, or target input", () => {
  const workspace = readFileSync(join(root,"components/lab-workspace.tsx"),"utf8");
  assert.doesNotMatch(workspace,/\/execute(?:["'`/]|$)|input[^>]+name=["'](?:command|target)/);
  assert.match(workspace,/local-fixture/);
});
test("private transport uses cookie credentials and CSRF headers without browser token storage", () => {
  const api = readFileSync(join(root,"lib/api.ts"),"utf8");
  const auth = readFileSync(join(root,"components/auth-provider.tsx"),"utf8");
  assert.match(api,/credentials:\s*"include"/);
  assert.match(api,/X-CSRF-Token/);
  assert.doesNotMatch(auth,/localStorage|sessionStorage/);
});
test("graph explorer has strict visual bounds and a nonvisual keyboard alternative", () => {
  const explorer = readFileSync(join(root,"components/graph-explorer.tsx"),"utf8");
  assert.match(explorer,/\[1, 2, 3, 4\]/);
  assert.match(explorer,/limit: 100, edge_limit: 200/);
  assert.match(explorer,/ACCESSIBLE RELATIONSHIP EXPLORER/);
  assert.match(explorer,/aria-live="polite"/);
  assert.match(explorer,/motion-reduce:transition-none/);
  assert.doesNotMatch(explorer,/dangerouslySetInnerHTML|terminal|remote execution|target input/);
});
test("community workspace preserves proposal-only, accessible, controlled-template boundaries", () => {
  const workspace = readFileSync(join(root,"components/community-workspaces.tsx"),"utf8");
  const contribute = readFileSync(join(root,"app/contribute/page.tsx"),"utf8");
  const review = readFileSync(join(root,"app/review/page.tsx"),"utf8");
  assert.match(workspace,/PROPOSED CONTENT — NOT CANONICAL KNOWLEDGE/);
  assert.match(workspace,/controlled template|Controlled .* fields/i);
  assert.match(workspace,/aria|<label|<fieldset/);
  assert.match(review,/index: false/);
  assert.match(contribute,/cannot directly mutate cybersecurity knowledge/);
  assert.doesNotMatch(workspace,/dangerouslySetInnerHTML|localStorage|sessionStorage|innerHTML|terminal|remote execution|target input|file upload/);
});
