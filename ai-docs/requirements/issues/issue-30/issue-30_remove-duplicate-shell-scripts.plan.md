# Implementation Plan: Remove duplicate shell script files from root directory

**GitHub Issue:** [#30](https://github.com/tristanl-slalom/conflicto/issues/30)
**Generated:** 2025-10-07T17:28:00Z

## Implementation Strategy

This is a cleanup task focused on removing technical debt by eliminating duplicate shell scripts. The approach prioritizes safety through thorough validation before removal, ensuring no functionality is lost and all references are properly handled.

### High-Level Approach
1. **Validation Phase**: Comprehensive analysis of existing scripts and dependencies
2. **Reference Updates**: Update any documentation or configuration that references root scripts
3. **Safe Removal**: Remove duplicate files after confirming safety
4. **Verification Phase**: Validate all functionality remains intact

## File Structure Changes

### Files to Remove
```
- /reset-db.sh (DELETE)
- /run-tests.sh (DELETE)
- /start-dev.sh (DELETE)
- /stop-dev.sh (DELETE)
```

### Files to Analyze (No Changes Expected)
```
- /Makefile (verify no dependencies)
- /.github/workflows/*.yml (check for script references)
- /README.md (update if references root scripts)
- /docs/* (update documentation if needed)
- /backend/reset-db.sh (confirm functionality)
- /backend/run-tests.sh (confirm functionality)
- /backend/start-dev.sh (confirm functionality)
- /backend/stop-dev.sh (confirm functionality)
```

### Potential Documentation Updates
```
- /README.md (may need script path updates)
- /docs/DEVELOPMENT.md (may need script path updates)
- /docs/BACKEND_SETUP_COMPLETE.md (may need script path updates)
```

## Implementation Steps

### Step 1: Pre-removal Analysis and Validation
**Files to examine:**
- `/Makefile` - Check for any targets that call root-level scripts
- `/.github/workflows/` - Scan all workflow files for script references
- `/README.md` - Look for instructions referencing root scripts
- `/docs/` - Check all documentation for script references

**Validation commands to run:**
```bash
# Search for references to root scripts in codebase
grep -r "reset-db.sh" . --exclude-dir=.git
grep -r "run-tests.sh" . --exclude-dir=.git
grep -r "start-dev.sh" . --exclude-dir=.git
grep -r "stop-dev.sh" . --exclude-dir=.git

# Compare root scripts with backend versions
diff reset-db.sh backend/reset-db.sh
diff run-tests.sh backend/run-tests.sh
diff start-dev.sh backend/start-dev.sh
diff stop-dev.sh backend/stop-dev.sh
```

### Step 2: Documentation Updates (if needed)
**Files potentially requiring updates:**
- Update any README or documentation that references root scripts to point to backend scripts
- Update development setup instructions
- Modify any getting-started guides

### Step 3: Configuration Updates (if needed)
**Files potentially requiring updates:**
- Update Makefile targets if they reference root scripts
- Update GitHub Actions workflows if they use root scripts
- Update any deployment scripts or configurations

### Step 4: Safe Script Removal
**Commands to execute:**
```bash
# Remove duplicate scripts from root directory
rm reset-db.sh
rm run-tests.sh
rm start-dev.sh
rm stop-dev.sh
```

### Step 5: Post-removal Verification
**Validation steps:**
```bash
# Verify backend scripts work correctly
cd backend && ./reset-db.sh --help
cd backend && ./run-tests.sh --help
cd backend && ./start-dev.sh --help
cd backend && ./stop-dev.sh --help

# Run tests to ensure nothing is broken
make test  # or equivalent test command

# Verify CI/CD still works (push to feature branch)
```

## Testing Strategy

### Pre-removal Testing
- [ ] Execute each root script with `--help` flag to document functionality
- [ ] Execute each backend script with `--help` flag to compare functionality
- [ ] Run full test suite to establish baseline
- [ ] Test development workflow commands (start, test, stop, reset)

### Post-removal Testing
- [ ] Verify backend scripts provide same functionality as removed scripts
- [ ] Run full test suite to ensure no regressions
- [ ] Test development workflow using backend scripts
- [ ] Validate CI/CD pipeline continues to work
- [ ] Test documentation instructions with backend script paths

### Integration Testing
- [ ] Full development setup from scratch using backend scripts
- [ ] Makefile target execution (if any use scripts)
- [ ] GitHub Actions workflow execution
- [ ] Docker container functionality (if scripts affect containers)

## Deployment Considerations

### No Database Changes
- No migrations required
- No data model changes
- No schema updates needed

### No Infrastructure Changes
- No environment variable changes
- No container configuration updates
- No service dependencies affected

### Backward Compatibility
- Developers must update their local workflows to use backend scripts
- Documentation updates will guide transition
- Consider adding deprecation notice period for team communication

## Risk Assessment

### Low Risk Areas
- **Script Removal**: Root scripts are duplicates, backend versions provide same functionality
- **Functionality Loss**: All functionality preserved through backend scripts
- **Development Impact**: Minimal - developers can easily adapt to backend script usage

### Medium Risk Areas
- **Hidden Dependencies**: Some undocumented process might reference root scripts
- **CI/CD Dependencies**: GitHub Actions or other automation might use root scripts
- **Documentation Lag**: Updated documentation might not reach all team members immediately

### Mitigation Strategies
1. **Thorough Analysis**: Comprehensive grep search for all script references
2. **Incremental Approach**: Remove one script at a time if concerns arise
3. **Quick Rollback**: Keep backup of scripts until PR is merged and validated
4. **Team Communication**: Announce changes and provide clear migration guidance

### Rollback Plan
If issues are discovered after removal:
1. Restore scripts from git history: `git checkout HEAD~1 -- reset-db.sh run-tests.sh start-dev.sh stop-dev.sh`
2. Investigate specific dependencies that were missed
3. Update those dependencies first, then retry removal

## Estimated Effort

### Time Estimation
- **Analysis Phase**: 30 minutes (searching references, comparing scripts)
- **Documentation Updates**: 15 minutes (updating README/docs if needed)
- **Script Removal**: 5 minutes (simple file deletion)
- **Testing & Validation**: 30 minutes (verifying functionality, running tests)
- **Total Estimated Time**: 1.5 hours

### Complexity Assessment
- **Technical Complexity**: Low (simple file removal)
- **Risk Complexity**: Low-Medium (need to verify no hidden dependencies)
- **Testing Complexity**: Low (straightforward functionality validation)
- **Documentation Complexity**: Low (minor path updates if needed)

### Prerequisites
- Access to repository and ability to create/push branches
- Local development environment set up to test scripts
- Understanding of current development workflow and script usage

### Success Metrics
- [ ] Root directory contains 4 fewer shell script files
- [ ] All development operations continue to work using backend scripts
- [ ] No CI/CD pipeline failures
- [ ] Documentation accurately reflects script locations
- [ ] Team members can successfully use backend scripts for all operations
