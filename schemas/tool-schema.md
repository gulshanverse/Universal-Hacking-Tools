# Tool Metadata Schema

Every tool page uses YAML front matter. The schema is intentionally small so that contributors can add pages without maintaining a separate database.

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | Yes | Official tool name; verify upstream. |
| `slug` | Yes | Lowercase filename-safe identifier, unique in the repository. |
| `category` | Yes | Repository category. |
| `subcategory` | Yes | More specific workflow or capability. |
| `difficulty` | Yes | `Beginner`, `Intermediate`, or `Advanced`. |
| `license` | Yes | Upstream license or an explicit verification note. |
| `platforms` | Yes | Supported platforms, using a YAML list or bracketed list. |
| `language` | Yes | Primary implementation language or `Platform independent`. |
| `repository` | Yes | Official source repository URL. |
| `official_website` | Yes | Official project website or repository when no separate site is verified. |
| `documentation` | Yes | Official documentation URL. |
| `security_domains` | Yes | One or more learning domains. |
| `dual_use` | Yes | Boolean indicating whether the page requires the legal notice. |
| `status` | Yes | Maintenance or verification note; never invent a current release. |

Do not add versions, capabilities, authors, benchmarks, or commands unless they are verified against an authoritative upstream source. Use `Not verified — check upstream documentation.` when a fact is not available.
