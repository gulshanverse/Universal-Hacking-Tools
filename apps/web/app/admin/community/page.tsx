/* Signal Archive restricted governance route: moderation controls remain bounded to application state and auditable. */
import { AdminCommunityWorkspace } from "../../../components/community-workspaces";
import { pageMetadata } from "../../../lib/metadata";
export const metadata = { ...pageMetadata("Community administration", "Restricted Phase 10 moderation and private report controls.", "/admin/community"), robots: { index: false, follow: false } };
export default function AdminCommunityPage() { return <main className="mx-auto max-w-6xl px-4 py-12 sm:px-6"><AdminCommunityWorkspace /></main>; }
