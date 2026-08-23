/* Signal Archive: small static route map; individual knowledge records remain API-backed dynamic pages. */
import type { MetadataRoute } from "next";
import { siteUrl } from "../lib/metadata";
export default function sitemap(): MetadataRoute.Sitemap { return ["","/explore","/tools","/vulnerabilities","/concepts","/techniques","/technologies","/defensive-controls","/labs","/learning-paths","/search","/about","/about/health","/contribute"].map(url=>({url:`${siteUrl}${url}`,lastModified:new Date("2026-08-23")})); }
