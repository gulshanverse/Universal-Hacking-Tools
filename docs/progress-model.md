# Phase 8 Progress Model

Progress is private application state keyed by a stable repository entity ID and the generated knowledge version observed at update time. A progress record can move from `not-started` to `in-progress` to `completed`. The API does not accept direct client assignment of `mastered`; mastery is derived only when defined prerequisites, relevant completion evidence, and a passing safe lab outcome are present.

Learning-path progress is computed from existing path relationships and completed required entities or labs rather than accepting an arbitrary percentage. Historical progress is retained when knowledge becomes deprecated, but new recommendation output avoids deprecated content. If knowledge relationships change, the stored entity ID and knowledge version allow the application to explain that a prior completion is historical rather than silently rewriting learner history.

The service records meaningful updates, such as a deliberate completion or lab assessment result, rather than indefinitely storing page-view telemetry. Progress APIs are authenticated and derive the user scope from the server-side session.
