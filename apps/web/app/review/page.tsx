/* Signal Archive restricted reviewer route: calm, evidence-led proposal review separate from public generated review reports. */
import { RestrictedReviewWorkspace } from "../../components/review-workspace";
import { pageMetadata } from "../../lib/metadata";
export const metadata = { ...pageMetadata("Community review", "Restricted proposal-review queue for authorized community reviewers.", "/review"), robots: { index: false, follow: false } };
export default function ReviewPage() { return <main className="mx-auto max-w-6xl px-4 py-12 sm:px-6"><RestrictedReviewWorkspace /></main>; }
