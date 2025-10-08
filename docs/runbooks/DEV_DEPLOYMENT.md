# Development Environment Runbook

Operational procedures and troubleshooting guide for the Conflicto development environment.

## Environment Overview

- **URL**: https://dev.conflicto.app
- **Purpose**: Continuous integration testing and feature validation
- **Deployment**: Automatic on main branch commits
- **Resources**: Cost-optimized AWS infrastructure
- **Database**: Development RDS instance

## Routine Operations

### Monitoring Development Deployments

**Check Deployment Status**:
1. Go to [GitHub Actions](https://github.com/tristanl-slalom/conflicto/actions)
2. Look for "Deploy to Development" workflows
3. Most recent runs should be green (successful)

**Verify Deployment Health**:
```bash
# Quick health check
curl https://dev.conflicto.app/api/v1/health/

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "0.1.0",
  "environment": "dev",
  "app_version": "abc123..."
}
```

### Daily Operational Checks

**Morning Checklist** (5 minutes):
- [ ] Check overnight deployment results
- [ ] Verify application health endpoint
- [ ] Review CloudWatch logs for errors
- [ ] Confirm integration tests are passing

**Weekly Maintenance**:
- [ ] Review resource utilization metrics
- [ ] Check for failed deployments requiring investigation
- [ ] Validate that dev environment mirrors production configuration
- [ ] Update deployment documentation if needed

## Troubleshooting

### Deployment Failures

#### Scenario: Infrastructure Deployment Fails
**Symptoms**: Terraform apply fails in GitHub Actions

**Investigation Steps**:
1. Check GitHub Actions logs for Terraform errors
2. Review AWS CloudTrail for permission issues
3. Verify Terraform state consistency

**Common Fixes**:
```bash
# If state lock issue
cd iac/environments/dev
terraform force-unlock <lock-id>

# If resource naming conflicts
terraform import <resource> <aws-resource-id>
```

#### Scenario: Application Deployment Fails
**Symptoms**: ECS service fails to start, health checks failing

**Investigation Steps**:
1. Check ECS service events in AWS console
2. Review CloudWatch logs for container startup errors
3. Verify container image exists in GHCR

**Common Fixes**:
- Image tag mismatch: Verify correct commit SHA in deployment
- Resource limits: Check ECS task definition CPU/memory allocation
- Environment variables: Verify configuration in task definition

### Application Issues

#### Scenario: Health Endpoint Returns 503
**Investigation**:
```bash
# Check application logs
aws logs tail /ecs/conflicto-backend-dev --follow

# Check database connectivity
aws rds describe-db-instances --db-instance-identifier conflicto-dev

# Test database connection
psql $DEV_DATABASE_URL -c "SELECT 1;"
```

**Common Causes**:
- Database connection timeout
- Migration failures
- Resource exhaustion (CPU/memory)

#### Scenario: Integration Tests Failing
**Investigation**:
1. Check test logs in GitHub Actions
2. Verify test environment configuration
3. Test endpoints manually

**Common Fixes**:
```bash
# Run tests locally against dev environment
cd tests/integration
export TEST_BASE_URL="https://dev.conflicto.app"
python -m pytest test_deployed_environment.py -v
```

### Database Issues

#### Scenario: Migration Failures
**Investigation**:
```bash
# Check migration status
cd backend
export DATABASE_URL="$DEV_DATABASE_URL"
poetry run alembic current

# Check migration logs
aws logs filter-log-events \
  --log-group-name /ecs/conflicto-backend-dev \
  --filter-pattern "migration"
```

**Recovery Steps**:
```bash
# Manual migration execution
cd backend
export DATABASE_URL="$DEV_DATABASE_URL"
export ENVIRONMENT="dev"
poetry run python scripts/migrate.py
```

### Performance Issues

#### Scenario: Slow Response Times
**Investigation**:
```bash
# Check ECS service metrics
aws ecs describe-services --cluster conflicto-dev-cluster --services conflicto-dev-svc

# Check database performance
aws rds describe-db-instances --db-instance-identifier conflicto-dev

# Test response times
time curl https://dev.conflicto.app/api/v1/health/
```

**Optimization Steps**:
- Review CloudWatch metrics for resource utilization
- Check database connection pooling settings
- Verify ECS task resource allocation

## Development Workflows

### Testing New Features

**Before Merging to Main**:
1. Create feature branch
2. Test locally with development configuration
3. Run unit tests and integration tests
4. Create pull request with comprehensive description

**After Merging to Main**:
1. Monitor automatic dev deployment
2. Verify feature works in deployed environment
3. Run manual testing if needed
4. Update integration tests if necessary

### Database Schema Changes

**Safe Migration Process**:
1. Create backward-compatible migrations
2. Test migration locally first
3. Deploy to dev environment
4. Verify data integrity
5. Plan production deployment

**Migration Validation**:
```bash
# Check migration in dev
cd backend
export DATABASE_URL="$DEV_DATABASE_URL"

# Run migration
poetry run alembic upgrade head

# Validate data
poetry run python scripts/validate_migration.py  # If exists
```

### Configuration Changes

**Environment Variable Updates**:
1. Update `iac/environments/dev/terraform.tfvars`
2. Update `backend/.env.dev` if needed
3. Deploy via GitHub Actions
4. Verify configuration through health endpoints

**Infrastructure Changes**:
1. Test Terraform changes in development first
2. Review Terraform plan carefully
3. Monitor deployment for issues
4. Validate infrastructure changes work as expected

## Emergency Procedures

### Development Environment Down
**Quick Assessment**:
```bash
# Check application health
curl -I https://dev.conflicto.app/api/v1/health/

# Check DNS resolution
nslookup dev.conflicto.app

# Check load balancer
aws elbv2 describe-load-balancers --names conflicto-dev-alb
```

**Recovery Actions**:
1. Check recent deployment logs
2. Execute rollback if needed using rollback workflow
3. If infrastructure issue, check AWS service health
4. Manually restart ECS service if necessary

### Data Loss or Corruption
**Assessment**:
```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier conflicto-dev

# Check recent backups
aws rds describe-db-snapshots --db-instance-identifier conflicto-dev
```

**Recovery Options**:
1. Restore from automated backup (acceptable for dev)
2. Re-run migrations from scratch
3. Reset development data if necessary

## Monitoring and Alerting

### Key Metrics to Watch
- **Application Health**: Health endpoint response status
- **Response Times**: API endpoint latency
- **Error Rates**: HTTP 4xx/5xx error percentages
- **Resource Utilization**: ECS CPU/memory usage
- **Database Performance**: Connection count, query times

### Log Locations
```bash
# Application logs
/ecs/conflicto-backend-dev

# Load balancer access logs
/aws/applicationloadbalancer/conflicto-dev-alb

# ECS service events
AWS Console → ECS → Services → conflicto-dev-svc → Events
```

### Setting Up Local Monitoring
```bash
# Watch deployment status
watch -n 30 'curl -s https://dev.conflicto.app/api/v1/health/ | jq .'

# Monitor logs
aws logs tail /ecs/conflicto-backend-dev --follow
```

## Development Environment Maintenance

### Resource Cleanup
**Weekly Tasks**:
- Review and delete old ECS task definitions
- Check for unused container images
- Monitor cost and resource usage

### Backup Validation
**Monthly Tasks**:
- Verify automated backups are working
- Test backup restoration process
- Document backup/restore procedures

### Security Updates
**As Needed**:
- Update base container images
- Apply security patches to dependencies
- Review and rotate access keys

## Contacts and Escalation

### Development Issues
- **Primary**: Repository owner (@tristanl-slalom)
- **Documentation**: This runbook and deployment guide
- **Logs**: GitHub Actions and CloudWatch

### Infrastructure Issues
- **AWS Console**: Check service health dashboards
- **AWS Support**: If widespread AWS service issues
- **Terraform State**: Review state file and recent changes

### Emergency Escalation
1. Check if issue affects production (higher priority)
2. Document issue details and attempted fixes
3. Contact repository owner with:
   - Description of issue
   - Steps already taken
   - Current system state
   - Urgency level
