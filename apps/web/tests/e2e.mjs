import { chromium } from "playwright-core";
import assert from "node:assert/strict";

const base = process.env.UHT_WEB_URL || "http://127.0.0.1:3001";
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || "/usr/bin/chromium", headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
const page = await browser.newPage({ viewport: { width: 1280, height: 820 } });
const issues = [];
let expectingSignedOutDashboard = false;
page.on("pageerror", error => issues.push(error.message));
page.on("response", response => {
  const url = response.url();
  if (response.status() >= 400 && !url.includes("/manus-storage/") && !url.endsWith("/favicon.ico") && !(expectingSignedOutDashboard && response.status() === 401 && url.endsWith("/api/v1/me/dashboard"))) issues.push(`${response.status()} ${url}`);
});

try {
  await page.goto(base, { waitUntil: "networkidle" });
  await assertVisible("Trace the relationship");
  await page.locator("#global-search").fill("nmap");
  await page.locator("#global-search").press("Enter");
  await page.waitForURL(/\/search\?q=nmap/);
  await assertVisible("deterministic matches");
  await page.getByRole("link", { name: "Nmap" }).first().click();
  await page.waitForURL(/\/tool\/nmap/);
  await assertVisible("Related knowledge");
  await page.goto(`${base}/explore/nmap`, { waitUntil: "networkidle" });
  await assertVisible("Bounded graph explorer");
  await page.getByLabel("Depth").selectOption("2");
  await assertVisible("ACCESSIBLE RELATIONSHIP EXPLORER");
  await page.getByRole("button", { name: "Select" }).first().click();
  await page.getByLabel("Path target").fill("firewall");
  await page.getByRole("button", { name: "Find path" }).click();
  await assertVisible("Shortest generated relationship path");
  await page.goto(`${base}/learning-paths/network-security`, { waitUntil: "networkidle" });
  await assertVisible("BEGINNER");
  await page.goto(`${base}/labs/dns-resolution-inventory`, { waitUntil: "networkidle" });
  await assertVisible("Authorized execution only");
  await page.getByRole("button", { name: "Create lab" }).click();
  await assertVisible("ready");
  await page.getByRole("button", { name: "Start" }).click();
  await assertVisible("running");
  await page.getByRole("button", { name: "Submit structured evidence" }).click();
  await page.getByRole("button", { name: "Assess" }).click();
  await assertVisible("Assessment:");
  await page.getByRole("button", { name: "Destroy" }).click();
  await assertVisible("destroyed");
  await page.goto(base, { waitUntil: "networkidle" });
  await page.keyboard.press("Tab");
  assert.ok(await page.evaluate(() => document.activeElement?.getAttribute("href") === "#content"), "skip link receives keyboard focus first");
  const mobile = await browser.newPage({ viewport: { width: 375, height: 812 } });
  await mobile.goto(base, { waitUntil: "networkidle" });
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true, "mobile home page has no horizontal overflow");
  await mobile.goto(`${base}/explore/nmap`, { waitUntil: "networkidle" });
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true, "mobile graph has no horizontal overflow");
  await mobile.close();
  if (process.env.UHT_E2E_EMAIL && process.env.UHT_E2E_PASSWORD) {
    await runPrivateJourney();
  }
  assert.deepEqual(issues, [], `browser console errors: ${issues.join(" | ")}`);
  console.log("Phase 7–9 browser E2E checks passed." + (process.env.UHT_E2E_EMAIL ? " Phase 8–9 private journey passed." : ""));
} finally {
  await browser.close();
}

async function assertVisible(text) {
  await page.getByText(text, { exact: false }).first().waitFor({ state: "visible", timeout: 10000 });
}

async function runPrivateJourney() {
  await page.goto(`${base}/login`, { waitUntil: "networkidle" });
  await page.getByLabel("Email address").fill(process.env.UHT_E2E_EMAIL);
  await page.getByLabel("Password").fill(process.env.UHT_E2E_PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL(/\/dashboard/);
  await assertVisible("Learning field notes");
  await page.goto(`${base}/tool/nmap`, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Bookmark" }).click();
  await assertVisible("Saved as a private bookmark");
  await page.getByRole("button", { name: "Completed" }).click();
  await assertVisible("Marked completed");
  await page.goto(`${base}/dashboard/notes`, { waitUntil: "networkidle" });
  await page.getByLabel("Plain text only").fill("Synthetic browser E2E private note.");
  await page.getByRole("button", { name: "Save note" }).click();
  await assertVisible("Private note saved");
  await page.goto(`${base}/dashboard/bookmarks`, { waitUntil: "networkidle" });
  await assertVisible("Nmap");
  await page.goto(`${base}/dashboard/knowledge-map`, { waitUntil: "networkidle" });
  await assertVisible("Knowledge map");
  await assertVisible("ACCESSIBLE RELATIONSHIP EXPLORER");
  await page.goto(`${base}/labs/dns-resolution-inventory`, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Create lab" }).click();
  await page.getByRole("button", { name: "Start" }).click();
  await page.getByRole("button", { name: "Submit structured evidence" }).click();
  await page.getByRole("button", { name: "Assess" }).click();
  await page.getByRole("button", { name: "Save private summary" }).click();
  await assertVisible("Private summary saved");
  await page.getByRole("button", { name: "Destroy" }).click();
  await assertVisible("destroyed");
  await page.goto(`${base}/dashboard/labs`, { waitUntil: "networkidle" });
  await assertVisible("dns-resolution-inventory");
  await page.getByRole("button", { name: "Sign out" }).first().click();
  expectingSignedOutDashboard = true;
  await page.goto(`${base}/dashboard`, { waitUntil: "networkidle" }).catch(() => {});
  await page.waitForURL(/\/login/);
  expectingSignedOutDashboard = false;
}
