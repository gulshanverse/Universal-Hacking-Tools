---
id: graphql-schema-safety
type: lab
name: GraphQL Schema Safety Review
status: needs-review
prerequisites:
  - authorization
  - threat-modeling
sources:
  - https://owasp.org/www-project-web-security-testing-guide/
---

# GraphQL Schema Safety Review

> Controlled, authorized lab exercise.

## Objective

Review schema exposure, authorization, and query resource controls in a local GraphQL service.

## Difficulty

Intermediate

## Prerequisites

Permission to use every system and dataset, a disposable environment, and the ability to reset it. Local GraphQL application; synthetic identities.

## Environment

Local GraphQL application; synthetic identities. Keep it separate from production and unrelated networks.

## Setup

Read the relevant upstream documentation, create synthetic or intentionally vulnerable fixtures, record scope and expected observations, and take a snapshot before testing.

## Learning Goals

* Explain the concept and trust boundary.
* Record evidence, uncertainty, and provenance.
* Connect observations to detection and mitigation.

## Tasks

1. Define the smallest safe question and success criteria.
2. Perform the controlled exercise and preserve relevant output.
3. Compare results with the known fixture state.
4. Write a short finding and defensive recommendation.

## Expected Observations

Results should be reproducible inside the lab and include timestamps, configuration, and known fixture state. Unexpected results are a reason to inspect assumptions, not expand scope.

## Security Interpretation

Map observations to relevant controls, logs, ownership, and remediation verification. Do not treat an automated match as proof without review.

## Detection

Identify the application, network, endpoint, identity, cloud, or file telemetry that a defender could use to observe the exercise.

## Mitigation

Apply least privilege, secure configuration, protected logging, segmentation, patching, and explicit response procedures as appropriate.

## Cleanup

Stop services, delete temporary credentials and artifacts, reset snapshots, remove test data, and confirm that no secrets or personal data remain.

## Further Learning

Follow the linked tool and knowledge pages, then repeat the exercise with a changed fixture and explain the difference.
