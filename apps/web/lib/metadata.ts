/* Signal Archive: centralized factual SEO metadata; no keyword-stuffed entity copies. */
import type { Metadata } from "next";

export const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export function pageMetadata(title: string, description: string, path = ""): Metadata {
  const canonical = `${siteUrl}${path}`;
  return {
    title: `${title} | Universal Hacking Tools`, description, alternates: { canonical },
    openGraph: { title: `${title} | Universal Hacking Tools`, description, url: canonical, type: "website" }
  };
}
