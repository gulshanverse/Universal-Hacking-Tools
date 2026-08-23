import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = new URL("..", import.meta.url).pathname;
const required = ["app/page.tsx", "app/search/page.tsx", "app/explore/page.tsx", "app/[type]/page.tsx", "app/[type]/[id]/page.tsx", "app/labs/page.tsx", "app/labs/[id]/page.tsx", "app/learning-paths/page.tsx", "app/learning-paths/[id]/page.tsx", "app/about/health/page.tsx", "app/contribute/page.tsx"];

test("required public Phase 7 pages exist", () => required.forEach(file => assert.equal(existsSync(join(root,file)), true, file)));
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
