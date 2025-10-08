# Emergency Rollback Procedures

This document outlines the procedures for emergency rollbacks in case of critical production issues.

## When to Execute Emergency Rollback

Execute an emergency rollback when:

- ✅ **Critical Production Bug**: Application functionality is severely broken
- ✅ **Performance Degradation**: Unacceptable response times or high error rates
- ✅ **Database Migration Issues**: Data corruption or migration failures
- ✅ **Service Unavailability**: Application is not responding or returning errors
- ✅ **Security Issues**: Discovered vulnerabilities requiring immediate action

## Rollback Decision Matrix

| Severity | Action | Timeframe |
|----------|--------|-----------|
| **Critical** - Production down | Emergency rollback | Immediately |
| **High** - Significant functionality broken | Schedule rollback within 1 hour | < 1 hour |
| **Medium** - Minor issues affecting some users | Plan fix or rollback | < 4 hours |
| **Low** - Cosmetic or edge case issues | Fix in next deployment | Next release |

## Quick Rollback Checklist

### ⚡ Immediate Actions (< 5 minutes)

1. **Assess Impact**
   - [ ] Verify the issue exists in production
   - [ ] Determine scope of impact (all users vs. subset)
   - [ ] Check recent deployment history

2. **Identify Rollback Target**
   - [ ] Find last known working commit SHA
   - [ ] Verify target image exists in GHCR
   - [ ] Confirm target was previously deployed successfully

3. **Initiate Rollback**
   - [ ] Navigate to GitHub Actions
   - [ ] Select "Emergency Rollback" workflow
   - [ ] Fill in rollback details
   - [ ] Execute rollback

### 🔍 Detailed Rollback Process

#### Step 1: Verify Issue and Impact

```bash
# Check application health
curl https://conflicto.app/api/v1/health/

# Check error rates in CloudWatch or monitoring
# Review recent deployment logs
```

#### Step 2: Identify Rollback Target

**Option A: Use Recent Successful Deployment**
1. Go to GitHub Actions history
2. Find last successful "Deploy to Production" workflow
3. Note the commit SHA used in that deployment

**Option B: Use Git History**
```bash
# Find recent commits on main branch
git log --oneline main -10

# Check which commits have successful deployments
# Look for commits that passed CI/CD successfully
```

**Option C: Check Container Images**
```bash
# List available container images (if you have access)
# Or check GHCR web interface for available tags
```

#### Step 3: Execute Emergency Rollback

1. **Navigate to GitHub Actions**
   - Go to https://github.com/tristanl-slalom/conflicto/actions
   - Select "Emergency Rollback" workflow
   - Click "Run workflow"

2. **Fill Rollback Parameters**
   ```
   Environment: prod
   Rollback to Tag: <commit-sha-or-tag>
   Confirm Rollback: ROLLBACK
   ```

3. **Approve Rollback (for Production)**
   - The workflow will create an approval issue
   - Approve immediately for emergency situations
   - Add rollback justification in approval

4. **Monitor Rollback Progress**
   - Watch workflow logs in real-time
   - Verify each step completes successfully
   - Watch for ECS service stabilization

#### Step 4: Verify Rollback Success

```bash
# Health check
curl https://conflicto.app/api/v1/health/

# Basic functionality test
curl https://conflicto.app/api/v1/sessions/

# Check response times
time curl https://conflicto.app/api/v1/health/
```

## Rollback Commands Reference

### GitHub CLI (if available)
```bash
# List recent workflow runs
gh run list --workflow="deploy-prod.yml" --limit=5

# Trigger rollback workflow
gh workflow run rollback.yml \
  --field environment=prod \
  --field rollback_to_tag=<commit-sha> \
  --field confirm_rollback=ROLLBACK
```

### AWS CLI (for direct service manipulation)
```bash
# Get current task definition
aws ecs describe-services \
  --cluster conflicto-prod-cluster \
  --services conflicto-prod-svc

# Force new deployment with previous task definition
aws ecs update-service \
  --cluster conflicto-prod-cluster \
  --service conflicto-prod-svc \
  --task-definition <previous-task-def-arn> \
  --force-new-deployment
```

## Database Rollback Considerations

### When Database Changes are Involved

If the deployment included database migrations:

1. **Check Migration Impact**
   ```bash
   # Review recent migration files
   ls backend/migrations/versions/ | tail -5

   # Check if migrations added/removed columns or tables
   ```

2. **Assess Data Risk**
   - **Safe**: Migrations only added new columns/tables
   - **Risky**: Migrations removed or modified existing data
   - **Critical**: Migrations performed destructive operations

3. **Database Rollback Options**

   **Option A: Application Rollback Only (Recommended)**
   - Roll back application code only
   - Leave database in current state
   - Ensure rolled-back code is compatible with current schema

   **Option B: Database Schema Rollback (High Risk)**
   ```bash
   # Only if absolutely necessary and you have backups
   cd backend
   poetry run alembic downgrade <target-revision>
   ```

   **Option C: Point-in-Time Recovery (Last Resort)**
   - Requires AWS RDS snapshot restoration
   - Results in data loss
   - Only for critical data corruption scenarios

## Communication During Rollback

### Internal Communication
```
🚨 EMERGENCY ROLLBACK IN PROGRESS 🚨

Issue: [Brief description of the problem]
Rollback Target: [commit SHA/tag]
Estimated Time: 5-10 minutes
Status: [In Progress/Complete]

ETA for resolution: [timestamp]
```

### User Communication (if needed)
```
We're experiencing a technical issue and are working to resolve it quickly.
The service may be temporarily unavailable.
We expect to have this resolved within 10 minutes.
```

## Post-Rollback Actions

### Immediate (< 30 minutes)
- [ ] Verify service health and functionality
- [ ] Monitor error rates and response times
- [ ] Document rollback details and timeline
- [ ] Create incident report

### Short-term (< 24 hours)
- [ ] Investigate root cause of original issue
- [ ] Identify fix for the problem
- [ ] Plan remediation deployment
- [ ] Update rollback procedures if needed

### Follow-up (< 1 week)
- [ ] Conduct post-incident review
- [ ] Implement preventive measures
- [ ] Update deployment processes if needed
- [ ] Share lessons learned with team

## Common Rollback Scenarios

### Scenario 1: Application Won't Start
**Symptoms**: Health checks failing, ECS tasks restarting
**Rollback**: Safe - roll back to previous working image
**Timeline**: 5-10 minutes

### Scenario 2: Database Migration Failure
**Symptoms**: Migration script errors, data corruption
**Rollback**: Risky - may require database restoration
**Timeline**: 15-30 minutes (or longer for database recovery)

### Scenario 3: Performance Degradation
**Symptoms**: Slow response times, timeout errors
**Rollback**: Safe - performance should improve immediately
**Timeline**: 5-10 minutes + monitoring time

### Scenario 4: Feature Breaking Change
**Symptoms**: Specific functionality not working
**Rollback**: Safe - functionality should be restored
**Timeline**: 5-10 minutes

## Testing Rollback Procedures

### Development Environment Testing
```bash
# Test rollback workflow in dev environment
# Use a recent commit as rollback target
# Verify the process works end-to-end
```

### Rollback Simulation Checklist
- [ ] Test rollback workflow execution
- [ ] Verify rollback time is under 10 minutes
- [ ] Confirm health checks pass after rollback
- [ ] Test database compatibility (if migrations involved)
- [ ] Document any issues or improvements needed

## Emergency Contacts

### Primary
- **Owner**: @tristanl-slalom (GitHub)
- **Repository**: https://github.com/tristanl-slalom/conflicto

### Escalation
- **AWS Support**: (if infrastructure issues)
- **On-call Engineer**: (if after hours)

## Rollback Troubleshooting

### Rollback Workflow Fails
1. Check GitHub Actions logs for specific error
2. Verify rollback target image exists
3. Check AWS credentials and permissions
4. Try manual ECS service update if needed

### Service Still Unhealthy After Rollback
1. Verify rollback actually completed (check ECS tasks)
2. Check if issue was environmental (not code-related)
3. Consider rolling back further to known stable version
4. Check for infrastructure or dependency issues

### Database Issues During Rollback
1. Do not attempt database schema rollback without backup
2. Focus on application-level compatibility
3. Consider maintenance mode if necessary
4. Engage database expert if data corruption suspected

Remember: **Speed is critical in emergency situations. When in doubt, execute the rollback and investigate the root cause afterward.**
