# AI-Generated Documentation Structure

This directory contains organized documentation generated and managed through AI-assisted development workflows for the Caja live event engagement platform.

## Directory Structure

```
ai-docs/
├── architecture/           # System design and technical specifications
│   ├── system-overview.md      # High-level system architecture
│   ├── tech-stack.md          # Technology choices and standards
│   ├── deployment-strategy.md  # AWS infrastructure and deployment
│   ├── caja-app-features.md   # Comprehensive feature specifications
│   ├── caja-app-goals.md      # Project goals and requirements
│   └── copilot-rules-plan.md  # GitHub Copilot integration plan
├── requirements/          # Issue specifications and implementation plans
│   └── issues/               # Individual issue documentation
│       └── issue-{number}/      # Per-issue folder structure
│           ├── issue-{number}_{title-slug}.spec.md  # Technical specification
│           └── issue-{number}_{title-slug}.plan.md  # Implementation plan
└── transcripts/          # Meeting and discussion records
    ├── 01-intro.md              # Initial project discussion
    ├── 02-requirements-discussion.md  # Requirements gathering session
    └── 03-technical-discovery.md      # Technical architecture decisions
```

## Purpose

### Architecture Documentation
Contains system-wide specifications, architectural decisions, and technical standards that guide development across the entire platform.

### Requirements Management
Provides structured documentation for each GitHub issue, including:
- **Specification Files (.spec.md):** Technical requirements, API definitions, data models, and acceptance criteria
- **Implementation Plans (.plan.md):** Step-by-step implementation approach, file structure changes, testing strategies, and risk assessment

### Transcripts
Historical records of team discussions, requirements gathering sessions, and technical discovery meetings that provide context for architectural decisions.

## Integration with Development Workflow

### Enhanced /conflictoIssue Command
The enhanced conflictoIssue custom prompt now follows a two-phase approach:

1. **Specification Phase:** Generates detailed technical specifications and implementation plans
2. **Review Phase:** Allows developer review and approval before code generation
3. **Implementation Phase:** Generates code following the approved specifications

### Benefits
- **Better Planning:** Forces detailed analysis before implementation
- **Review Process:** Enables developer oversight of AI interpretation
- **Documentation:** Creates searchable implementation history
- **Consistency:** Ensures implementations follow reviewed specifications
- **Traceability:** Links requirements to implementation decisions

## Usage Examples

### For Closed Issues
Issue #3 demonstrates the documentation format for completed work:
- `issue-3_create-fastapi-backend-foundation.spec.md` - Technical specification
- `issue-3_create-fastapi-backend-foundation.plan.md` - Implementation plan

### For New Issues
Use the enhanced conflictoIssue command:
```
/conflictoIssue 15                    # Full workflow with review
/conflictoIssue 15 --spec-only        # Generate specification only
/conflictoIssue 15 --implement        # Skip to implementation if spec exists
```

## Maintenance

This documentation structure is automatically maintained through the AI-assisted development workflow. When implementing new features:

1. Specifications and plans are generated automatically
2. Architecture documentation is updated as needed
3. Links between issues and implementations are maintained
4. Historical context is preserved through structured organization

The ai-docs folder serves as the central knowledge repository for the project, providing both current specifications and historical context for all development decisions.
