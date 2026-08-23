import { chromium } from "playwright-core";
import assert from "node:assert/strict";

const base = process.env.UHT_WEB_URL || "http://127.0.0.1:3001";
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || "/usr/bin/chromium", headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
const page = await browser.newPage({ viewport: { width: 1280, height: 820 } });
const issues = [];
page.on("pageerror", error => issues.push(error.message));
page.on("response", response => {
  const url = response.url();
  if (response.status() >= 400 && !url.includes("/manus-storage/") && !url.endsWith("/favicon.ico")) issues.push(`${response.status()} ${url}`);
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
  await mobile.close();
  assert.deepEqual(issues, [], `browser console errors: ${issues.join(" | ")}`);
  console.log("Phase 7 browser E2E checks passed.");
} finally {
  await browser.close();
}

async function assertVisible(text) {
  await page.getByText(text, { exact: false }).first().waitFor({ state: "visible", timeout: 10000 });
}
