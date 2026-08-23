# Phase 6 Evidence and Assessment

A lab records structured evidence instead of returning only a binary success message. Each record is associated with an instance, task, evidence definition, type, timestamp, and JSON value. The local store is ephemeral and is deleted on reset or destroy unless a future reviewed workflow explicitly retains educational output.

## Supported evidence types

The definition may use `observation`, `artifact`, `finding`, `configuration`, `log-entry`, `request-response`, `screenshot-reference`, or `answer`. The reference runner records fixture observations only. Values are screened for obvious private-key, access-key, token, password, and secret-like patterns before storage.

## Deterministic rubric

Assessment criteria reference known evidence IDs and use one of three operations: `evidence-present`, `field-nonempty`, or `field-equals`. The result includes every criterion, its pass/fail state, feedback, and aggregate status. The aggregate statuses are `not-started`, `failed`, `partial`, and `passed`; partial credit is produced only when the definition contains multiple criteria and some, but not all, pass.

The engine does not use an LLM, external API, embeddings, network retrieval, or probabilistic scoring. It cannot infer that a learner’s unsupported statement is correct. A successful fixture inspection proves only that the defined local observation was recorded.

## Hints

Tasks may include levelled hints. Hints should point the learner toward the relevant fixture fields and defensive interpretation without revealing unrestricted real-world exploitation instructions. Hints are stored in definitions and do not affect the score.

## Example lifecycle

```text
create → start → run task → evidence → assess → stop → reset or destroy
```

Use `evidence` to inspect records and `assess` to evaluate the current rubric. Reset clears evidence and returns the instance to a clean ready state. Destroy removes the temporary manifest, audit stream, and evidence while retaining only a minimal state tombstone to reject later transitions.
