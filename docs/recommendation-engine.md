# Phase 8 Deterministic Recommendation Engine

The Phase 8 recommendation engine consumes the authenticated learner’s goals, completed entities, progress status, safe-lab summaries, derived skills, and the existing generated knowledge graph. It returns a bounded list of next concepts, tools, labs, and learning-path steps with structured explanations.

| Rule | Result |
| --- | --- |
| A required prerequisite is incomplete | Recommend the prerequisite before its dependent entity |
| Entity is completed or mastered | Exclude it from normal next-step output |
| Entity is deprecated or structurally invalid | Exclude it |
| Lab is not a safe executable definition | Exclude it from executable recommendations |
| Goal/path mapping matches an available entity | Prefer the lowest-difficulty eligible candidate |
| Entity is needs-review or unverified | Include explicit verification-status context rather than presenting it as authoritative |

Every recommendation has `reason_type`, `reason_entity`, and human-readable `reason_text`. The engine has no LLM, embeddings, vector database, external model, opaque score, or behavioral tracking. Snapshots are optional private audit records and are removed with the account.
