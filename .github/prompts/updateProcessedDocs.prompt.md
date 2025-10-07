---
mode: agent
description: "Update processed folder documentation with development learnings and technical decisions"
---

# /updateProcessedDocs - Documentation Sync Workflow

Updates the processed folder documentation with new technical decisions, implementations, and learnings from recent development work for the Caja live event engagement platform.

## Usage

```
updateProcessedDocs
```

## Examples

- `updateProcessedDocs` - Automatically detect and document all recent changes
- Command analyzes git history, modified files, and implementation progress
- Updates documentation based on detected technical decisions and feature completions

## Workflow Steps

### 1. Intelligent Change Detection
- **Git Analysis:** Review recent commits, modified files, and new configurations
- **Technical Decision Detection:** Identify framework migrations, dependency changes, config updates
- **Implementation Progress:** Compare current state with planned features in processed docs
- **Scope Determination:** Automatically categorize changes (testing, frontend, backend, infrastructure)
- **Context Gathering:** Extract rationale and impacts from code changes and commit messages

### 2. Automatic Documentation Updates

#### Detected Testing Changes
When framework migrations, test configuration, or testing strategies are detected:
- Testing framework migrations (Jest → Vitest, etc.)
- New test patterns and best practices
- Coverage threshold changes and quality gates
- Mock strategies and test environment setup
- CI/CD pipeline testing integration

#### Detected Frontend Changes
When React components, UI frameworks, or build configs are modified:
- Component architecture and design system changes
- State management patterns (TanStack Query, Context, etc.)
- Persona-specific interface implementations
- Responsive design and accessibility improvements
- Build system and deployment optimizations

#### Detected Backend Changes
When API code, database models, or service logic is updated:
- API design patterns and endpoint structures
- Database schema changes and migration strategies
- Authentication and authorization implementations
- Performance optimizations and caching strategies
- Service architecture and integration patterns

#### Detected Infrastructure Changes
When Terraform, AWS configs, or deployment files are modified:
- AWS resource configurations and Terraform modules
- Deployment pipeline improvements and automation
- Monitoring, logging, and alerting setup
- Security policies and compliance requirements
- Environment management and configuration strategies

### 3. File Updates by Priority

#### Primary Updates
**`processed/technical_decisions_log.md`**
- Add new technical decisions with full context and rationale
- Document problem statements and solution approaches
- Include before/after code examples for significant changes
- Record performance impacts and developer experience improvements
- Track migration steps and lessons learned

**`processed/caja_app_features.md`**
- Update feature implementation status (✅ IMPLEMENTED, ⚠️ PARTIAL, ⏳ PENDING)
- Add technical implementation details for completed features
- Document component architecture and integration points
- Update user story completion status
- Add performance characteristics and scalability notes

**`processed/copilot_rules_plan.md`**
- Update development guidelines with new patterns
- Add code generation rules for new frameworks and tools
- Update tech stack documentation with current choices
- Revise testing strategies and quality standards
- Include new workflow patterns and team procedures

#### Secondary Updates
**Create new documentation files as needed:**
- Architecture decision records for major changes
- Migration guides for framework transitions
- Performance benchmarks and optimization guides
- Development workflow improvements

### 4. Content Generation Patterns

#### Technical Decision Format
```markdown
## [Framework/Technology] Migration: [Old] → [New]

**Date:** [Current Date]  
**Issue:** [Problem Description]  
**Decision:** [Solution Implemented]  

### Background
[Context and motivation for change]

### Problem Details
- [Specific issues encountered]
- [Compatibility conflicts]
- [Developer experience problems]

### Solution Implemented
[Detailed implementation steps and changes]

### Results
- ✅ [Benefit 1]
- ✅ [Benefit 2]
- ✅ [Performance improvement]

### Configuration Files
[Code examples and configuration changes]

### Impact on Development Workflow
[Changes to developer experience and processes]
```

#### Feature Status Update Format
```markdown
### [Feature Name] ✅ **IMPLEMENTED** / ⚠️ **PARTIAL** / ⏳ **PENDING**
**Description:** [Feature overview]

**Technical Implementation:**
- **Framework:** [Technology stack]
- **Components:** [Key components implemented]
- **Testing:** [Test coverage and strategy]
- **Integration:** [How it connects to other systems]

**User Stories Foundation:**
- As a [persona], I can [action] ✅/⚠️/⏳
```

### 5. Quality Assurance

#### Documentation Completeness Check
- [ ] All technical decisions properly documented with rationale
- [ ] Implementation status accurately reflects current state
- [ ] Code examples and configurations are current and tested
- [ ] Cross-references between documents are maintained
- [ ] New patterns added to Copilot rules for consistency

#### Accuracy Validation
- [ ] Feature status matches actual implementation
- [ ] Technical details align with current codebase
- [ ] Performance claims are measurable and verified
- [ ] Dependencies and integrations are correctly documented

#### Team Alignment
- [ ] Documentation supports onboarding new team members
- [ ] Architecture decisions are clearly communicated
- [ ] Development workflow changes are documented
- [ ] Future development guidance is actionable

### 6. Integration Points

#### GitHub MCP Integration
- Link technical decisions to relevant GitHub issues
- Reference pull requests that implemented changes
- Track decision implementation across multiple repositories
- Maintain traceability from requirements to documentation

#### Copilot Rules Synchronization
- Ensure new patterns are captured in `.copilot/instructions.md`
- Update architecture guidelines with current implementations
- Sync persona-specific development rules
- Add new activity framework patterns

## Auto-Detection Triggers

### File Pattern Analysis
**Testing Changes Detected When:**
- `package.json` testing dependencies modified
- `jest.config.*` or `vitest.config.*` files changed
- `__tests__/`, `*.test.*`, `*.spec.*` files modified
- CI/CD test configuration updated

**Frontend Changes Detected When:**
- React components in `/src/components/` modified
- Route files in `/src/routes/` changed
- UI configuration files updated (`tailwind.config.*`, `vite.config.*`)
- State management files in `/src/hooks/` or `/src/store/` modified

**Backend Changes Detected When:**
- API routes in `/backend/app/routes/` modified
- Database models or migrations changed
- Service layer files updated
- FastAPI configuration modified

**Infrastructure Changes Detected When:**
- Terraform files (`*.tf`) modified
- Docker or container configuration changed
- CI/CD pipeline files updated
- AWS or deployment configuration modified

## Error Handling

### No Recent Changes Detected
- Analyze git history for the last 7 days
- Check for unreflected changes in processed documentation
- Suggest manual review if significant changes exist but aren't auto-detectable
- Provide summary of current documentation state

### Ambiguous Changes
- Use git commit messages and file patterns for context
- Default to comprehensive update when scope is unclear
- Prioritize user-facing and architectural changes

### Documentation Conflicts
- Preserve existing content while adding new information
- Use clear section headers for chronological organization
- Maintain backward compatibility with existing references

## Expected Output Format

```
� Analyzing workspace for recent changes...
� Detected changes in: frontend (testing framework), components (persona interfaces)
🔧 Identified technical decisions: Jest→Vitest migration, TanStack integration
📝 Updating processed documentation...

Updated files:
✅ processed/technical_decisions_log.md - Added Jest→Vitest migration details
✅ processed/caja_app_features.md - Updated Multi-Persona Interface status to ✅ IMPLEMENTED  
✅ processed/copilot_rules_plan.md - Added Vitest testing standards and frontend completion

Auto-detected changes:
• Testing Framework: Migrated from Jest to Vitest for better Vite integration
• Frontend Architecture: Completed multi-persona interface system with TanStack
• Component Library: Implemented shadcn/ui with comprehensive test coverage
• Development Workflow: Enhanced test feedback loop and coverage reporting

📚 Documentation now reflects:
- Current implementation status with accurate feature markers
- Latest technical decisions with migration rationale
- Updated development guidelines for Vitest and TanStack patterns
- Team workflow improvements and testing strategies

🎯 Ready for next development phase:
- Backend API integration (frontend framework complete)
- Real-time WebSocket implementation (polling framework ready)
- Additional activity types (component architecture established)
```

This command ensures the processed folder documentation stays current with rapid development cycles while maintaining consistency and providing valuable context for AI-assisted development.