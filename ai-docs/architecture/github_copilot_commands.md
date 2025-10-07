# GitHub Copilot Commands for Caja Development

## Documentation Management Commands

### Update Documentation with Development Learnings

**Command:** `/updateProcessedDocs`

**Purpose:** Automatically update the ai-docs folder with new technical decisions, implementations, and learnings from recent development work.

**Usage:**
```
updateProcessedDocs
```

**What it does:**
1. Reviews recent changes in the codebase (git diff, new files, modified configurations)
2. Identifies technical decisions and implementation changes
3. Updates relevant files in the `/ai-docs/architecture` folder:
   - `technical_decisions_log.md` - Adds new technical decisions with rationale
   - `caja-app-features.md` - Updates feature implementation status
   - `copilot-rules-plan.md` - Updates development guidelines and standards
4. Creates new documentation files if needed
5. Ensures documentation reflects current project state

**Specific Actions Performed:**
- Analyze configuration changes (package.json, config files)
- Document testing framework migrations
- Update implementation status of features (✅ IMPLEMENTED, ⚠️ PARTIAL, ⏳ PENDING)
- Add technical implementation details
- Update Copilot rules with new patterns and standards
- Record performance improvements and developer experience enhancements

**Auto-Detection Triggers:**
- **Testing Changes:** `package.json` testing dependencies, `vitest.config.*`, test files
- **Frontend Changes:** React components, routes, UI configs, state management files
- **Backend Changes:** API routes, models, services, FastAPI configuration
- **Infrastructure Changes:** Terraform files, Docker, CI/CD pipeline files

---

## Feature Development Commands

### Create Feature Implementation Plan

**Command:** `/planFeature`

**Purpose:** Generate a comprehensive implementation plan for a new Caja feature.

**Usage:**
```
planFeature [feature-name] [persona] [priority]
```

**Example:**
```
planFeature "Live Polling System" participant high
```

---

## Code Generation Commands

### Generate Persona Interface Component

**Command:** `/genPersonaComponent`

**Purpose:** Generate a new React component following the multi-persona interface patterns.

**Usage:**
```
genPersonaComponent [component-name] [persona] [activity-type]
```

**Example:**
```
genPersonaComponent "PollVoting" participant poll
```

---

## Testing Commands

### Generate Test Suite for Feature

**Command:** `/genTests`

**Purpose:** Generate comprehensive test suite for a feature using Vitest patterns.

**Usage:**
```
genTests [feature-name] [test-type]
```

**Example:**
```
genTests "session-management" component
```

**Test Types:**
- `component` - React component tests with RTL
- `hook` - Custom hook tests with mock implementations
- `integration` - API integration tests
- `e2e` - End-to-end user flow tests

---

## Usage Guidelines

### When to Use Documentation Commands

1. **After Major Technical Changes:**
   - Framework migrations (Jest → Vitest)
   - Architecture updates (monorepo → microservices)
   - Tooling changes (build systems, CI/CD)

2. **After Feature Completion:**
   - Update implementation status
   - Document performance improvements
   - Record lessons learned

3. **Before Major Development Phases:**
   - Sync documentation with current state
   - Update Copilot rules with new patterns
   - Ensure team alignment on standards

### Best Practices

1. **Run updateProcessedDocs after significant work** to keep documentation current
2. **Include rationale** for technical decisions in commit messages for better auto-detection
3. **Update both status and implementation details** when completing features
4. **Keep Copilot rules current** with actual implementation patterns
5. **Document performance impacts** and developer experience changes

### Integration with MCP Workflow

These commands integrate with the Model Context Protocol setup to:
- Create GitHub issues directly from VS Code
- Maintain traceability from requirements to implementation
- Ensure documentation stays current with rapid development cycles
- Support AI-assisted development with current project context