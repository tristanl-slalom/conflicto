---
mode: agent
description: "Bulk-generate GitHub issues from a structured Markdown source file (spec-driven backlog creation)"
---

# /createIssues - Bulk Issue Generation Workflow

Generates multiple GitHub issues from a single curated Markdown source file. Designed to accelerate backlog seeding and enforce consistent specification quality. Integrates with the GitHub MCP server for issue creation, labeling, dependency linking, and traceability.

## Instructions

High-level responsibilities of this command:

- Parse source Markdown and derive potential issues.
- ALWAYS apply the mandatory Feature Tag (see next section) to every generated issue.
- Use the GitHub MCP server to fetch existing issues and labels (reuse, avoid duplicates).
- Gate actual GitHub issue creation behind an explicit user approval step.
- Add heuristic labels (e.g., `backend`, `frontend`, `api`, `infrastructure`) in addition to, never instead of, the Feature Tag.

## Feature Tag Specification (MANDATORY)

The Feature Tag is a required label applied to every issue generated in a run. Extraction precedence:

1. File-level YAML front matter
2. Per-issue YAML block

If none provide a value, the issue is skipped (never created) and reported.

### 1. File-Level YAML Front Matter (Highest Precedence)

Top-of-file example:

```yaml
---
feature_tag: {value} 
---
```

Keys:

- `feature_tag`: REQUIRED – applied to all issues unless a per-issue override appears.

### 2. Per-Issue YAML Front Matter Override

Supported keys inside an issue YAML block:

- `title`
- `feature_tag`
- `labels`
- `depends_on`

Example:

```yaml
---
title: Phase 1: Domain and Certificates
feature_tag: infrastructure
labels: ["certificates", "terraform"]
depends_on: ["Phase 0: Bootstrap Remote State"]
---
```

### 4. Fallback & Error Handling

When no Feature Tag is found after steps 1–3:

1. Skip creating the issue.
2. Emit warning: `⚠ Missing Feature Tag → Skipped: <title or first 60 chars>`.
3. List all skipped items in final summary.

### 5. Label Creation Policy

1. Fetch existing repo labels.
2. Create the Feature Tag label if missing (description: `Feature Tag (auto-created by /createIssues)`).
3. Apply labels in order: Feature Tag → file default labels → per-issue labels → heuristic labels.

### 6. Validation Rules

| Check | Action |
|-------|--------|
| Empty `feature_tag` | Skip issue |
| Label creation failure | Abort run & report |
| Duplicate per-issue `feature_tag` keys | Use first; warn |

### 7. Summary Output Column

```text
#  Issue Title                               FeatureTag     Other Labels
-- ----------------------------------------  -------------  ----------------------
45 Phase 0: Bootstrap Remote State          infrastructure enhancement,infra
```

### 8. Mixed Source Example

```markdown
---
feature_tag: infrastructure
default_labels: ["enhancement"]
---

## Phase 0: Bootstrap Remote State
Description...

## Phase 1: Domain & Certificates
---
title: Phase 1: Domain & Certificates
feature_tag: infrastructure
labels: ["terraform", "certificates"]
---
Description...

## Phase 2: Networking
Feature Tag: infrastructure
Description...
```

All issues receive `infrastructure`; Phase 1 also adds `terraform`, `certificates`, and the file-level `enhancement`.

### 9. Implementation Pseudocode

```python
labels_existing = fetch_repo_labels()
file_meta = parse_yaml_front_matter(file_text)
global_feature_tag = file_meta.get('feature_tag')

for issue_block in split_issue_blocks(file_text):
      meta = parse_issue_block_yaml(issue_block)
      feature_tag = (meta.get('feature_tag') or
                           extract_inline_feature_tag(issue_block) or
                           global_feature_tag)
      if not feature_tag:
            warn_missing(issue_block)
            continue
      ensure_label_exists(feature_tag, labels_existing)
      labels = dedupe([
            feature_tag,
            *file_meta.get('default_labels', []),
            *as_list(meta.get('labels'))
      ])
      create_issue(meta.get('title') or derive_title(issue_block), build_body(issue_block), labels)
```

### 10. Rationale

Deterministic extraction guarantees the required label is always applied before any heuristic labeling.

---

## Usage

```bash
createIssues {path/to/source-file.md}
```

Parameter:

- `path/to/source-file.md` (required): A Markdown file containing one or more issue definitions in a structured format (see Parsing Strategy section below).

## Examples

```bash
createIssues ai-docs/requirements/backlog/session-framework-backlog.md
createIssues ai-docs/requirements/backlog/platform-observability-roadmap.md
```

## Enhanced Workflow Steps

### 1. Issue Creation

#### Issue formatting

##### Instructions (Formatting Guidance)

- Sections below are optional and may not be relevant based on the nature of the issue being created. If not relevant, keep the section
      and have its content only be "N/A" to explicitly indicate that it was considered and determined to not be applicable.
- The issue number should be sequential and be the next available issue number based on the list of issues retrieved from GitHub Issues.

##### Format

```markdown
# Technical Specification: [Issue Title]

**GitHub Issue:** [#X](link)
**Generated:** [timestamp]

## Problem Statement
[Extracted from issue description]

## Technical Requirements
[Derived technical requirements]

## API Specifications
[Endpoint definitions, request/response schemas]

## Data Models
[Database schemas, entity relationships]

## Interface Requirements
[UI/UX specifications if applicable]

## Integration Points
[External services, dependencies]

## Acceptance Criteria
[Technical acceptance criteria]

## Assumptions & Constraints
[Technical assumptions and limitations]
```

### 2. Developer Review Phase

- Command pauses and displays generated issue text
- Developer reviews generated issue text
- Provides feedback or approval to proceed with creating the issue in GitHub Issues
- **This command does not create an issue in GitHub Issues without the explicit approval of the user**

## High-Level Flow

1. Validate the provided source file exists and is readable.
2. Parse issue blocks from the file (title, description, labels, acceptance criteria, dependencies, effort estimate, etc.).
3. For each valid issue definition:
   - Normalize title → slug
   - Generate default labels if not explicitly defined (e.g., `triage`, `auto-generated`)
   - Create GitHub issue via MCP server
   - Persist per-issue spec stub (optional, configurable)
4. Link dependencies (second pass) using newly created issue numbers.
5. Output a summary table of created issues.

## Output (Console Summary Example)

```text
📄 Source: .copilot/iac.md
🔍 Parsed: 12 issue definitions (10 valid, 2 skipped: missing title/criteria)

#   Issue Title                                  Labels                         Est Effort
--  -------------------------------------------  ------------------------------ ----------
101 Session Lifecycle Core API                   backend,session,auto-generated  M (3d)
102 Session State Persistence                    backend,session,auto-generated  S (1d)
103 Participant Join Flow (QR + Code)            frontend,participant            M (2d)
... (truncated)

✅ Created 10 issues successfully
```
