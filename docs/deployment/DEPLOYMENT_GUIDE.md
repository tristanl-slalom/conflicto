# Conflicto Deployment Guide

This guide covers the deployment procedures and workflows for the Conflicto live event engagement platform.

## Overview

Conflicto uses a continuous deployment pipeline that automatically deploys to development environments and provides manual approval gates for production deployments.

### Architecture

- **Development Environment**: Continuous deployment from `main` branch
- **Production Environment**: Manual workflow dispatch with approval gates
- **Infrastructure**: AWS ECS Fargate with RDS PostgreSQL
- **Container Registry**: GitHub Container Registry (GHCR)

## Environments

### Development Environment
- **URL**: https://dev.conflicto.app
- **Trigger**: Automatic on main branch push
- **Database**: Development RDS instance (db.t4g.micro)
- **Resources**: Cost-optimized (256 CPU, 512 MB memory)

### Production Environment
- **URL**: https://conflicto.app
- **Trigger**: Manual workflow dispatch with approval
- **Database**: Production RDS instance (db.r6g.large)
- **Resources**: Performance-optimized (1024 CPU, 2048 MB memory)

## Deployment Workflows

### Development Deployment (Automatic)

Triggered automatically when code is pushed to the `main` branch.

**Workflow**: `.github/workflows/deploy-dev.yml`

**Steps**:
1. Deploy/update infrastructure with Terraform
2. Run database migrations
3. Deploy applications to ECS
4. Execute health checks
5. Run integration tests
6. Notify deployment status

**Duration**: ~10-15 minutes

### Production Deployment (Manual)

Triggered manually through GitHub Actions workflow dispatch.

**Workflow**: `.github/workflows/deploy-prod.yml`

**Steps**:
1. Validate deployment inputs
2. **Manual approval gate** (requires @tristanl-slalom approval)
3. Deploy/update infrastructure with Terraform
4. Run database migrations
5. Deploy applications to ECS
6. Execute health checks
7. Run smoke tests
8. Notify deployment status

**Duration**: ~15-20 minutes (excluding approval time)

### Emergency Rollback

Available for both environments through manual workflow dispatch.

**Workflow**: `.github/workflows/rollback.yml`

**Requirements**:
- Specify environment (dev/prod)
- Provide rollback target (image tag/commit SHA)
- Type "ROLLBACK" to confirm

**Duration**: ~5-10 minutes

## Deployment Process

### Initiating a Development Deployment

Development deployments happen automatically:

1. Create a pull request to `main` branch
2. Get code review and approval
3. Merge to `main` branch
4. Deployment workflow triggers automatically
5. Monitor workflow progress in GitHub Actions
6. Verify deployment at https://dev.conflicto.app

### Initiating a Production Deployment

Production deployments require manual initiation:

1. Navigate to GitHub Actions → "Deploy to Production" workflow
2. Click "Run workflow"
3. Specify the container image tag (e.g., commit SHA)
4. Type "DEPLOY" in the confirmation field
5. Click "Run workflow"
6. Approve the deployment when prompted
7. Monitor workflow progress
8. Verify deployment at https://conflicto.app

### Image Tag Selection

**For Development**: Uses the commit SHA automatically (`${{ github.sha }}`)

**For Production**: Manually specify the tag, typically:
- A specific commit SHA: `a1b2c3d4e5f6...`
- A release tag: `v1.2.3`
- The latest stable commit SHA from main branch

## Required Secrets

The following GitHub secrets must be configured:

### AWS Credentials
```
AWS_ACCESS_KEY_ID=<aws-access-key>
AWS_SECRET_ACCESS_KEY=<aws-secret-key>
```

### Database URLs
```
DEV_DATABASE_URL=postgresql://user:pass@dev-db:5432/conflicto_dev
PROD_DATABASE_URL=postgresql://user:pass@prod-db:5432/conflicto_prod
```

## Health Checks and Validation

### Health Check Endpoints

- **Basic Health**: `/api/v1/health/` - Database connectivity and service status
- **Readiness**: `/api/v1/health/ready` - Service ready to accept requests
- **Liveness**: `/api/v1/health/live` - Service alive and running

### Deployment Validation

Each deployment includes:
1. **Infrastructure validation**: Terraform plan/apply success
2. **Migration validation**: Database migration completion
3. **Health validation**: Service health check passes
4. **Integration testing**: API functionality validation (dev only)
5. **Smoke testing**: Critical path validation (prod only)

## Database Migrations

### Migration Strategy

- **Automated Execution**: Migrations run automatically during deployment
- **Backward Compatibility**: All migrations must support rollback
- **Safety Checks**: Pre-migration database backup (prod)
- **Validation**: Post-migration integrity checks

### Migration Scripts

- **Migration Runner**: `backend/scripts/migrate.py`
- **Health Checker**: `backend/scripts/health-check.py`

### Manual Migration (Emergency)

If automated migrations fail:

```bash
# SSH to ECS task or run locally with prod database access
cd backend
export DATABASE_URL="<production-database-url>"
export ENVIRONMENT="prod"
poetry run python scripts/migrate.py
```

## Rollback Procedures

### When to Rollback

- Critical bugs in production
- Performance degradation
- Database migration issues
- Service unavailability

### Rollback Process

1. Navigate to GitHub Actions → "Emergency Rollback" workflow
2. Select environment (dev/prod)
3. Specify rollback target (known working commit SHA)
4. Type "ROLLBACK" to confirm
5. Approve rollback (for production)
6. Monitor rollback progress
7. Verify service health

### Finding Rollback Targets

**Recent Deployments**: Check GitHub Actions history for successful deployment commits

**Git History**:
```bash
git log --oneline main
```

**Container Images**: Check GHCR for available image tags

## Monitoring and Observability

### Application Logs

- **Backend Logs**: CloudWatch Log Groups `/ecs/conflicto-backend-<env>`
- **Access Logs**: Application Load Balancer access logs
- **Migration Logs**: ECS task execution logs

### Key Metrics

- **Response Time**: API endpoint response times
- **Error Rate**: HTTP 4xx/5xx error rates
- **Availability**: Service uptime percentage
- **Database Performance**: Connection count, query performance

### Troubleshooting

#### Deployment Failures

1. Check GitHub Actions logs for specific error
2. Review Terraform apply logs for infrastructure issues
3. Check ECS service deployment status
4. Verify health check endpoints

#### Service Issues

1. Check CloudWatch logs for application errors
2. Verify database connectivity
3. Check ECS task status and resource utilization
4. Review load balancer target health

#### Database Issues

1. Check RDS instance status and metrics
2. Review migration logs for failures
3. Verify database connectivity from ECS tasks
4. Check for blocking queries or locks

## Configuration Management

### Environment Variables

Environment-specific configuration is managed through:

- **Terraform Variables**: Infrastructure-level configuration
- **ECS Environment Variables**: Application runtime configuration
- **AWS Parameter Store**: Sensitive configuration values (future)

### Configuration Files

- **Development**: `backend/.env.dev`
- **Production**: `backend/.env.prod`
- **Terraform Dev**: `iac/environments/dev/terraform.tfvars`
- **Terraform Prod**: `iac/environments/prod/terraform.tfvars`

## Security Considerations

### Access Control

- **GitHub Environments**: Protection rules for production deployments
- **AWS IAM**: Least privilege access for deployment roles
- **Secrets Management**: GitHub secrets for sensitive values

### Network Security

- **VPC Isolation**: ECS tasks in private subnets
- **Security Groups**: Restrictive rules for service communication
- **Load Balancer**: HTTPS termination with SSL certificates

## Support and Escalation

### Primary Contact
- **Owner**: @tristanl-slalom
- **Repository**: https://github.com/tristanl-slalom/conflicto

### Escalation Process
1. Check deployment logs and health endpoints
2. Review recent commits for potential issues
3. Consider rollback for critical production issues
4. Contact repository owner for complex issues

### Emergency Procedures
- **Production Down**: Execute emergency rollback immediately
- **Database Issues**: Review migration logs and consider rollback
- **Infrastructure Issues**: Check AWS console and Terraform state
