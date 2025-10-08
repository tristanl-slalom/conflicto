# Production Environment Runbook

Comprehensive operational procedures and emergency response guide for the Conflicto production environment.

## Environment Overview

- **URL**: https://conflicto.app
- **Purpose**: Production workloads and user traffic
- **Deployment**: Manual approval required via GitHub Actions
- **Resources**: Production-grade AWS infrastructure with high availability
- **Database**: Production RDS instance with automated backups

## Critical Production Guidelines

### ⚠️ PRODUCTION SAFETY RULES
1. **NO direct database changes** without backup and rollback plan
2. **ALWAYS test in development first** before production deployment
3. **REQUIRE approval** for all production deployments
4. **MONITOR for 30 minutes** after every deployment
5. **HAVE rollback plan** ready before any changes

### Change Control Process
1. All production changes must be approved by repository owner
2. Changes must be tested in development environment first
3. Production deployments require manual approval in GitHub Actions
4. Post-deployment monitoring is mandatory
5. Rollback procedures must be documented and tested

## Routine Operations

### Production Deployment Process

**Pre-Deployment Checklist**:
- [ ] Changes tested and verified in development environment
- [ ] Database migrations reviewed and tested
- [ ] Rollback procedure documented and ready
- [ ] Monitoring plan established
- [ ] Approval from repository owner obtained

**Deployment Steps**:
1. Navigate to GitHub Actions
2. Run "Deploy to Production" workflow
3. Wait for approval gate (manual approval required)
4. Monitor deployment progress
5. Execute post-deployment verification
6. Monitor for 30 minutes minimum

**Post-Deployment Verification**:
```bash
# Verify application health
curl https://conflicto.app/api/v1/health/

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "0.1.0",
  "environment": "prod",
  "app_version": "abc123..."
}

# Check readiness
curl https://conflicto.app/api/v1/health/ready

# Check liveness
curl https://conflicto.app/api/v1/health/live
```

### Daily Production Monitoring

**Morning Checklist** (10 minutes):
- [ ] Verify application health endpoints
- [ ] Check CloudWatch logs for overnight errors
- [ ] Review performance metrics and response times
- [ ] Confirm backup completion
- [ ] Check for any failed scheduled tasks

**Critical Metrics Dashboard**:
```bash
# Health check
curl -w "@curl-format.txt" -s https://conflicto.app/api/v1/health/

# Where curl-format.txt contains:
#     time_namelookup:  %{time_namelookup}\n
#      time_connect:  %{time_connect}\n
#   time_appconnect:  %{time_appconnect}\n
#  time_pretransfer:  %{time_pretransfer}\n
#     time_redirect:  %{time_redirect}\n
#time_starttransfer:  %{time_starttransfer}\n
#                   ----------\n
#        time_total:  %{time_total}\n
```

### Weekly Production Maintenance

**Scheduled Maintenance Window**: Sundays 2:00 AM - 4:00 AM UTC
- [ ] Review security updates and patches
- [ ] Analyze performance trends
- [ ] Review error logs and alerts
- [ ] Test backup restoration procedures
- [ ] Update documentation if needed
- [ ] Plan upcoming deployments

## Emergency Response Procedures

### 🚨 CRITICAL: Production Down

**Immediate Assessment** (< 2 minutes):
```bash
# Quick health check
curl -I https://conflicto.app/api/v1/health/

# Check DNS
nslookup conflicto.app

# Check load balancer
aws elbv2 describe-load-balancers --names conflicto-prod-alb --region us-east-1
```

**Escalation Steps**:
1. **0-2 min**: Confirm outage and check recent changes
2. **2-5 min**: Execute immediate rollback if recent deployment
3. **5-10 min**: Contact repository owner if rollback doesn't resolve
4. **10+ min**: Engage AWS support if infrastructure issue

**Immediate Actions**:
```bash
# Check recent deployments
gh run list --workflow="Deploy to Production" --limit=5

# Execute emergency rollback if needed
gh workflow run rollback.yml -f environment=prod -f version=<last-known-good>
```

### Database Emergencies

#### Critical: Database Connection Failures
**Investigation**:
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier conflicto-prod

# Check database connectivity from task
aws ecs execute-command --cluster conflicto-prod-cluster \
  --task <task-arn> --container conflicto-backend \
  --command "/bin/bash" --interactive
```

**Recovery Options**:
1. **Connection timeout**: Restart ECS service
2. **Database unavailable**: Check RDS events and AWS service health
3. **Corruption detected**: Restore from latest backup (requires approval)

#### Critical: Data Loss or Corruption
**⚠️ STOP ALL WRITES IMMEDIATELY**
```bash
# Scale ECS service to 0 to stop all traffic
aws ecs update-service --cluster conflicto-prod-cluster \
  --service conflicto-prod-svc --desired-count 0

# Document exact time of incident
echo "Incident start: $(date -u)"
```

**Recovery Process**:
1. **Assess damage**: Connect to read replica if available
2. **Notify stakeholders**: Immediately contact repository owner
3. **Prepare restoration**: Identify last known good backup
4. **Execute restoration**: Follow documented backup restore procedure
5. **Validate data**: Thoroughly test data integrity before resuming service

### Application Performance Issues

#### High Response Times
**Investigation**:
```bash
# Check ECS service health
aws ecs describe-services --cluster conflicto-prod-cluster --services conflicto-prod-svc

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics --namespace AWS/ECS \
  --metric-name CPUUtilization --dimensions Name=ServiceName,Value=conflicto-prod-svc \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 --statistics Average

# Check database performance
aws rds describe-db-instances --db-instance-identifier conflicto-prod
```

**Mitigation Actions**:
1. **Scale up ECS tasks**: Increase desired count if CPU/memory high
2. **Database tuning**: Check connection pool settings
3. **Load balancer**: Verify health check configuration

#### Error Rate Spikes
**Investigation**:
```bash
# Check application logs for errors
aws logs filter-log-events --log-group-name /ecs/conflicto-backend-prod \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR"

# Check for specific error patterns
aws logs filter-log-events --log-group-name /ecs/conflicto-backend-prod \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "Exception"
```

## Deployment Troubleshooting

### Failed Production Deployments

#### Terraform Infrastructure Failure
**Symptoms**: Infrastructure deployment fails during GitHub Actions

**Investigation Steps**:
1. Check Terraform plan and apply logs
2. Verify AWS service quotas and limits
3. Check for resource naming conflicts
4. Review IAM permissions

**Recovery Actions**:
```bash
# Check Terraform state
cd iac/environments/prod
terraform show

# If state lock issue
terraform force-unlock <lock-id>

# Plan to see differences
terraform plan -var-file="terraform.tfvars"
```

#### ECS Service Update Failure
**Symptoms**: ECS service fails to reach stable state

**Investigation**:
```bash
# Check service events
aws ecs describe-services --cluster conflicto-prod-cluster --services conflicto-prod-svc

# Check task definition
aws ecs describe-task-definition --task-definition conflicto-prod:<revision>

# Check running tasks
aws ecs list-tasks --cluster conflicto-prod-cluster --service-name conflicto-prod-svc
```

**Recovery Steps**:
1. **Rollback**: Use rollback workflow to revert to previous version
2. **Task restart**: Stop tasks to force recreation with new configuration
3. **Service reset**: Update service with known-good task definition

### Migration Failures

#### Database Migration Stuck or Failed
**⚠️ CRITICAL**: Database migrations must be handled carefully in production

**Assessment**:
```bash
# Check migration status
export DATABASE_URL="$PROD_DATABASE_URL"
cd backend
poetry run alembic current

# Check for locks or long-running transactions
psql $PROD_DATABASE_URL -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

**Recovery Options**:
1. **Wait**: If migration is running, monitor progress
2. **Manual intervention**: Only if migration is clearly stuck
3. **Rollback database**: Restore from pre-migration backup (last resort)

**Migration Recovery**:
```bash
# If safe to retry migration
cd backend
export DATABASE_URL="$PROD_DATABASE_URL"
export ENVIRONMENT="prod"
poetry run python scripts/migrate.py --retry

# Check data integrity after recovery
poetry run python scripts/validate_data.py  # If exists
```

## Monitoring and Alerting

### Critical Metrics Thresholds
- **Response Time**: >2 seconds (warning), >5 seconds (critical)
- **Error Rate**: >1% (warning), >5% (critical)
- **CPU Usage**: >70% (warning), >90% (critical)
- **Memory Usage**: >80% (warning), >95% (critical)
- **Database Connections**: >70% of max (warning), >90% (critical)

### Real-Time Monitoring
```bash
# Continuous health monitoring
watch -n 10 'curl -s https://conflicto.app/api/v1/health/ | jq .'

# Monitor application logs
aws logs tail /ecs/conflicto-backend-prod --follow --since 1h

# Check service status
watch -n 30 'aws ecs describe-services --cluster conflicto-prod-cluster --services conflicto-prod-svc --query "services[0].{Status:status,Running:runningCount,Desired:desiredCount}"'
```

### Log Analysis
```bash
# Error pattern analysis
aws logs filter-log-events --log-group-name /ecs/conflicto-backend-prod \
  --start-time $(date -d '24 hours ago' +%s)000 \
  --filter-pattern "ERROR" | jq '.events[].message'

# Performance analysis
aws logs filter-log-events --log-group-name /ecs/conflicto-backend-prod \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "[timestamp, request_id, method, path, status_code, response_time > 2000]"
```

## Backup and Recovery

### Automated Backup Verification
```bash
# Check recent backups
aws rds describe-db-snapshots --db-instance-identifier conflicto-prod \
  --snapshot-type automated --max-items 5

# Verify backup completion
aws rds describe-db-snapshots --db-instance-identifier conflicto-prod \
  --snapshot-type automated --query 'DBSnapshots[0].{Status:Status,Time:SnapshotCreateTime}'
```

### Backup Recovery Testing
**Monthly Process** (during maintenance window):
1. Create test RDS instance from backup
2. Verify data integrity and completeness
3. Test application connection to restored database
4. Document recovery time and process
5. Clean up test resources

### Emergency Backup Recovery
**⚠️ PRODUCTION DATA RECOVERY PROCESS**
```bash
# 1. Create recovery RDS instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier conflicto-prod-recovery \
  --db-snapshot-identifier <snapshot-identifier>

# 2. Wait for instance availability
aws rds wait db-instance-available --db-instance-identifiers conflicto-prod-recovery

# 3. Update application configuration to point to recovery database
# 4. Verify data integrity
# 5. Switch DNS or load balancer to recovery instance
```

## Security Procedures

### Security Incident Response
1. **Identify**: Confirm security incident scope and impact
2. **Contain**: Isolate affected systems immediately
3. **Investigate**: Document evidence and attack vectors
4. **Recover**: Restore systems from clean backups if needed
5. **Learn**: Update security measures and document lessons

### Access Management
- All production access requires MFA
- Use AWS SSO for administrative access
- Rotate access keys quarterly
- Review IAM permissions monthly

### Security Monitoring
```bash
# Check for suspicious API activity
aws logs filter-log-events --log-group-name /ecs/conflicto-backend-prod \
  --start-time $(date -d '24 hours ago' +%s)000 \
  --filter-pattern "[timestamp, request_id, method, path, status_code >= 400]"

# Monitor authentication failures
aws logs filter-log-events --log-group-name /ecs/conflicto-backend-prod \
  --filter-pattern "authentication failed"
```

## Performance Optimization

### Capacity Planning
- **Current baselines**: Document current performance metrics
- **Growth projections**: Plan for 2x traffic capacity
- **Scaling triggers**: Automate scaling based on metrics
- **Cost optimization**: Regular review of resource utilization

### Performance Tuning
```bash
# Database performance analysis
psql $PROD_DATABASE_URL -c "SELECT * FROM pg_stat_activity WHERE state != 'idle';"

# Application performance metrics
curl -w "@curl-format.txt" -s https://conflicto.app/api/v1/health/
```

## Compliance and Documentation

### Change Documentation
- All production changes must be documented
- Include rollback procedures for every change
- Maintain deployment history and impact assessment
- Review and approve all changes before implementation

### Audit Trail
```bash
# Review deployment history
gh run list --workflow="Deploy to Production" --limit=20

# Check infrastructure changes
cd iac/environments/prod
git log --oneline -10 terraform.tfvars
```

## Emergency Contacts

### Primary Contacts
- **Repository Owner**: @tristanl-slalom
- **Emergency Contact**: [Configure emergency contact information]

### Escalation Matrix
1. **Level 1** (0-15 min): Repository owner
2. **Level 2** (15-30 min): Technical lead
3. **Level 3** (30+ min): Management escalation

### External Support
- **AWS Support**: Use AWS console for support cases
- **GitHub Support**: For GitHub Actions or repository issues
- **DNS Provider**: For DNS-related issues

## Documentation Updates

### Runbook Maintenance
- Review monthly for accuracy
- Update after major deployments
- Include lessons learned from incidents
- Validate emergency procedures quarterly

### Version Control
- All runbook changes via pull requests
- Include rationale for procedural changes
- Maintain version history
- Regular review and approval process
