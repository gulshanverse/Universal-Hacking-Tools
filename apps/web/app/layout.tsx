/* Signal Archive shell: persistent, high-contrast orientation and concise provenance. */
import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "../components/site-header";
import { SiteFooter } from "../components/site-footer";
import { AuthProvider } from "../components/auth-provider";

export const metadata: Metadata = {
  title: "Universal Hacking Tools | Knowledge Archive",
  description: "A local-first, evidence-aware cybersecurity knowledge platform for authorized learning and defensive practice.",
  robots: { index:true, follow:true }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><AuthProvider><a className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:m-3 focus:bg-white focus:px-4 focus:py-2" href="#content">Skip to content</a><SiteHeader/><main id="content">{children}</main><SiteFooter/></AuthProvider></body></html>;
}
