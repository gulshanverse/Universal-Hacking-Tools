/* Signal Archive: public knowledge routes may be indexed; internal API/review and local instance surfaces are excluded. */
import type { MetadataRoute } from "next";
import { siteUrl } from "../lib/metadata";
export default function robots(): MetadataRoute.Robots { return { rules:[{ userAgent:"*", allow:["/"], disallow:["/api/","/review/","/lab-instances/"] }], sitemap:`${siteUrl}/sitemap.xml` }; }
