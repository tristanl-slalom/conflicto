# Implementation Plan: Implement Continuous Deployment Pipeline with Dev/Prod Environments

**GitHub Issue:** [#76](https://github.com/tristanl-slalom/conflicto/issues/76)
**Generated:** 2025-10-08T19:31:46Z

## Implementation Strategy

This implementation follows a phased approach to establish continuous deployment capabilities while building on existing Terraform infrastructure and GitHub Actions CI/CD. The strategy prioritizes infrastructure automation, environment separation, and comprehensive testing integration to enable reliable, automated deployments to AWS.

### High-Level Approach
1. **Infrastructure Enhancement**: Extend existing Terraform modules for deployment automation
2. **Workflow Creation**: Build GitHub Actions workflows for dev/prod deployment pipelines
3. **Application Integration**: Add health checks, configuration management, and migration automation
4. **Testing Framework**: Implement comprehensive integration and smoke testing
5. **Monitoring Setup**: Configure CloudWatch monitoring and alerting
6. **Documentation**: Create operational runbooks and deployment procedures

## File Structure Changes

### New Files to Create

```
.github/workflows/
├── deploy-dev.yml                    # Automated dev environment deployment
├── deploy-prod.yml                   # Manual prod environment deployment
├── integration-tests.yml             # Post-deployment integration testing
└── rollback.yml                      # Emergency rollback workflow

iac/
├── environments/
│   ├── dev/
│   │   ├── main.tf                   # Dev environment Terraform configuration
│   │   ├── terraform.tfvars          # Dev-specific variable values
│   │   └── outputs.tf                # Dev environment outputs
│   └── prod/
│       ├── main.tf                   # Prod environment Terraform configuration
│       ├── terraform.tfvars          # Prod-specific variable values
│       └── outputs.tf                # Prod environment outputs
├── modules/ecs/
│   ├── deployment.tf                 # ECS deployment configuration enhancements
│   └── task-definitions/
│       ├── dev.json                  # Dev task definition template
│       └── prod.json                 # Prod task definition template
└── scripts/
    ├── deploy-infrastructure.sh      # Infrastructure deployment script
    ├── deploy-applications.sh        # Application deployment script
    ├── run-migrations.sh             # Database migration script
    └── rollback.sh                   # Emergency rollback script

backend/
├── app/
│   ├── core/
│   │   ├── deployment.py             # Deployment tracking and status
│   │   └── health.py                 # Health check utilities
│   ├── models/
│   │   └── deployment.py             # Deployment data model
│   └── routes/
│       ├── health.py                 # Health check endpoints
│       └── deployment.py             # Deployment status API
├── migrations/
│   └── versions/
│       └── xxx_add_deployment_tracking.py  # Deployment tracking migration
└── scripts/
    ├── migrate.py                    # Migration runner for CI/CD
    └── health-check.py               # Deployment health validation

tests/
├── integration/
│   ├── test_deployed_environment.py  # End-to-end deployment tests
│   ├── test_api_integration.py       # API integration tests
│   └── test_database_integration.py  # Database connectivity tests
└── performance/
    ├── load-test.js                  # k6 load testing script
    └── baseline-test.js              # Performance baseline validation

docs/
├── deployment/
│   ├── DEPLOYMENT_GUIDE.md           # Deployment procedures and workflows
│   ├── ROLLBACK_PROCEDURES.md        # Emergency rollback documentation
│   ├── MONITORING_SETUP.md           # CloudWatch monitoring configuration
│   └── TROUBLESHOOTING.md            # Common deployment issues and solutions
└── runbooks/
    ├── DEV_DEPLOYMENT.md             # Dev environment operational runbook
    └── PROD_DEPLOYMENT.md            # Production deployment runbook
```

### Existing Files to Modify

```
iac/modules/ecs/
├── main.tf                           # Add deployment configuration support
├── variables.tf                      # Add deployment-related variables
└── outputs.tf                        # Add service names and ARNs for deployment

iac/modules/rds/
├── main.tf                           # Add backup and migration support
└── variables.tf                      # Add environment-specific sizing variables

backend/
├── app/
│   ├── main.py                       # Add health check route registration
│   ├── core/config.py                # Add environment-specific configuration
│   └── db/database.py                # Add migration execution capability
├── pyproject.toml                    # Add deployment and migration dependencies
└── Dockerfile                        # Add health check configuration

frontend/
├── src/
│   ├── config/
│   │   └── environment.ts            # Environment-specific configuration
│   └── components/
│       └── HealthCheck.tsx           # Health status component (optional)
├── package.json                      # Add build and deployment scripts
└── Dockerfile                        # Add health check configuration

Makefile                              # Add deployment and testing targets
README.md                             # Add deployment documentation links
```

## Implementation Steps

### Phase 1: Infrastructure Foundation (Days 1-3)

#### Step 1: Terraform Environment Structure
**Files Created:**
- `iac/environments/dev/main.tf`
- `iac/environments/dev/terraform.tfvars`
- `iac/environments/prod/main.tf`
- `iac/environments/prod/terraform.tfvars`

**Implementation:**
```bash
# Create environment-specific Terraform configurations
mkdir -p iac/environments/{dev,prod}

# Set up Terraform backend configuration with workspace separation
terraform {
  backend "s3" {
    bucket         = "conflicto-terraform-state"
    key            = "environments/${var.environment}/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

#### Step 2: ECS Module Enhancement
**Files Modified:**
- `iac/modules/ecs/main.tf`
- `iac/modules/ecs/variables.tf`
- `iac/modules/ecs/outputs.tf`

**Implementation:**
```hcl
# Add deployment configuration to ECS module
resource "aws_ecs_service" "main" {
  # ... existing configuration ...

  deployment_configuration {
    maximum_percent         = var.deployment_maximum_percent
    minimum_healthy_percent = var.deployment_minimum_healthy_percent

    deployment_circuit_breaker {
      enable   = true
      rollback = true
    }
  }
}
```

#### Step 3: Task Definition Templates
**Files Created:**
- `iac/modules/ecs/task-definitions/dev.json`
- `iac/modules/ecs/task-definitions/prod.json`

**Implementation:**
```json
{
  "family": "conflicto-backend-${environment}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "${cpu}",
  "memory": "${memory}",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "${backend_image}",
      "essential": true,
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "ENVIRONMENT", "value": "${environment}"},
        {"name": "DATABASE_URL", "value": "${database_url}"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Phase 2: Application Integration (Days 4-6)

#### Step 4: Health Check Implementation
**Files Created:**
- `backend/app/routes/health.py`
- `backend/app/core/health.py`

**Files Modified:**
- `backend/app/main.py`

**Implementation:**
```python
# backend/app/routes/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/deep")
async def deep_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")
```

#### Step 5: Configuration Management
**Files Modified:**
- `backend/app/core/config.py`

**Files Created:**
- `backend/.env.dev`
- `backend/.env.prod`

**Implementation:**
```python
# Enhanced configuration for deployment environments
class Settings(BaseSettings):
    # Environment detection
    environment: str = Field(default="dev", env="ENVIRONMENT")
    app_version: str = Field(default="unknown", env="APP_VERSION")

    # Database configuration
    database_url: str = Field(env="DATABASE_URL")
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")

    # AWS configuration
    aws_region: str = Field(default="us-west-2", env="AWS_REGION")

    # Feature toggles per environment
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")

    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"
```

#### Step 6: Database Migration Automation
**Files Created:**
- `backend/scripts/migrate.py`
- `backend/scripts/health-check.py`

**Implementation:**
```python
# backend/scripts/migrate.py
import asyncio
from alembic.config import Config
from alembic import command
from app.core.config import settings

async def run_migrations():
    """Execute database migrations during deployment"""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    print(f"Running migrations for environment: {settings.environment}")
    command.upgrade(alembic_cfg, "head")

    print("Migration completed successfully")
    return True

if __name__ == "__main__":
    asyncio.run(run_migrations())
```

### Phase 3: Deployment Workflows (Days 7-9)

#### Step 7: Development Deployment Workflow
**Files Created:**
- `.github/workflows/deploy-dev.yml`

**Implementation:**
```yaml
name: Deploy to Development
on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - '*.md'
      - 'ai-docs/**'

env:
  AWS_REGION: us-west-2
  ENVIRONMENT: dev

jobs:
  deploy-infrastructure:
    name: Deploy Infrastructure
    runs-on: ubuntu-latest
    environment: development
    outputs:
      backend_service_name: ${{ steps.terraform.outputs.backend_service_name }}
      frontend_service_name: ${{ steps.terraform.outputs.frontend_service_name }}
      cluster_name: ${{ steps.terraform.outputs.cluster_name }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_wrapper: false

      - name: Terraform Deploy
        id: terraform
        working-directory: iac/environments/dev
        run: |
          terraform init
          terraform plan -var-file=terraform.tfvars
          terraform apply -auto-approve -var-file=terraform.tfvars

          # Export outputs for next job
          echo "backend_service_name=$(terraform output -raw backend_service_name)" >> $GITHUB_OUTPUT
          echo "frontend_service_name=$(terraform output -raw frontend_service_name)" >> $GITHUB_OUTPUT
          echo "cluster_name=$(terraform output -raw cluster_name)" >> $GITHUB_OUTPUT

  deploy-applications:
    name: Deploy Applications
    needs: deploy-infrastructure
    runs-on: ubuntu-latest
    environment: development

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update ECS Services
        run: |
          # Update backend service with new image
          aws ecs update-service \
            --cluster ${{ needs.deploy-infrastructure.outputs.cluster_name }} \
            --service ${{ needs.deploy-infrastructure.outputs.backend_service_name }} \
            --force-new-deployment

          # Update frontend service with new image
          aws ecs update-service \
            --cluster ${{ needs.deploy-infrastructure.outputs.cluster_name }} \
            --service ${{ needs.deploy-infrastructure.outputs.frontend_service_name }} \
            --force-new-deployment

      - name: Wait for Deployment
        run: |
          aws ecs wait services-stable \
            --cluster ${{ needs.deploy-infrastructure.outputs.cluster_name }} \
            --services ${{ needs.deploy-infrastructure.outputs.backend_service_name }} \
                      ${{ needs.deploy-infrastructure.outputs.frontend_service_name }}

  integration-tests:
    name: Integration Tests
    needs: deploy-applications
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Run Integration Tests
        env:
          TEST_BASE_URL: https://dev.conflicto.app
        run: |
          cd tests/integration
          npm install
          npm test
```

#### Step 8: Production Deployment Workflow
**Files Created:**
- `.github/workflows/deploy-prod.yml`

**Implementation:**
```yaml
name: Deploy to Production
on:
  workflow_dispatch:
    inputs:
      image_tag:
        description: 'Container image tag to deploy'
        required: true
        type: string
      confirm_deployment:
        description: 'Type "DEPLOY" to confirm production deployment'
        required: true
        type: string

env:
  AWS_REGION: us-west-2
  ENVIRONMENT: prod

jobs:
  validate-input:
    name: Validate Deployment Input
    runs-on: ubuntu-latest
    steps:
      - name: Validate Confirmation
        if: ${{ github.event.inputs.confirm_deployment != 'DEPLOY' }}
        run: |
          echo "❌ Deployment not confirmed. Please type 'DEPLOY' in the confirmation field."
          exit 1

  deploy-production:
    name: Deploy to Production
    needs: validate-input
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://conflicto.app

    steps:
      - name: Manual Approval Gate
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ github.TOKEN }}
          approvers: tristanl-slalom
          issue-title: "Production Deployment Approval"
          issue-body: |
            ## Production Deployment Request

            **Image Tag**: ${{ github.event.inputs.image_tag }}
            **Requested by**: ${{ github.actor }}
            **Workflow**: ${{ github.workflow }}

            Please review and approve this production deployment.

      - name: Checkout
        uses: actions/checkout@v4

      - name: Deploy Infrastructure
        working-directory: iac/environments/prod
        run: |
          terraform init
          terraform plan -var-file=terraform.tfvars
          terraform apply -auto-approve -var-file=terraform.tfvars

      - name: Deploy Applications
        run: |
          # Implementation similar to dev but with prod-specific configuration
          echo "Deploying to production with image tag: ${{ github.event.inputs.image_tag }}"

      - name: Run Smoke Tests
        run: |
          # Basic smoke tests to validate production deployment
          echo "Running production smoke tests..."
```

### Phase 4: Testing Integration (Days 10-12)

#### Step 9: Integration Test Implementation
**Files Created:**
- `tests/integration/test_deployed_environment.py`
- `tests/integration/test_api_integration.py`
- `tests/performance/load-test.js`

**Implementation:**
```python
# tests/integration/test_deployed_environment.py
import pytest
import httpx
import os

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test basic health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "environment" in health_data
        assert "version" in health_data

@pytest.mark.asyncio
async def test_deep_health_check():
    """Test database connectivity through health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health/deep")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["database"] == "connected"

@pytest.mark.asyncio
async def test_api_endpoints():
    """Test core API functionality"""
    async with httpx.AsyncClient() as client:
        # Test session creation
        session_data = {"name": "Test Session", "description": "Integration test"}
        response = await client.post(f"{BASE_URL}/api/sessions", json=session_data)
        assert response.status_code == 201

        session = response.json()
        session_id = session["id"]

        # Test session retrieval
        response = await client.get(f"{BASE_URL}/api/sessions/{session_id}")
        assert response.status_code == 200

        # Cleanup
        await client.delete(f"{BASE_URL}/api/sessions/{session_id}")
```

#### Step 10: Performance Testing
**Files Created:**
- `tests/performance/baseline-test.js`

**Implementation:**
```javascript
// k6 performance baseline test
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },  // Ramp up
    { duration: '5m', target: 10 },  // Stay at 10 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.1'],    // Error rate under 10%
  },
};

const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';

export default function () {
  // Health check test
  let response = http.get(`${BASE_URL}/health`);
  check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  });

  sleep(1);
}
```

### Phase 5: Documentation and Operations (Days 13-15)

#### Step 11: Documentation and Runbooks
**Files Created:**
- `docs/deployment/DEPLOYMENT_GUIDE.md`
- `docs/deployment/ROLLBACK_PROCEDURES.md`
- `docs/runbooks/DEV_DEPLOYMENT.md`
- `docs/runbooks/PROD_DEPLOYMENT.md`

**Implementation:**
```markdown
# DEPLOYMENT_GUIDE.md
## Conflicto Deployment Guide

### Development Environment
- **Trigger**: Automatic on main branch push
- **URL**: https://dev.conflicto.app

### Production Environment
- **Trigger**: Manual workflow dispatch
- **URL**: https://conflicto.app

### Emergency Procedures
1. **Immediate Rollback**: Use rollback.yml workflow
2. **Database Issues**: Follow database rollback procedures
3. **Escalation**: Contact @tristanl-slalom for production issues
```

## Testing Strategy

### Unit Tests
- **Coverage Target**: >80% code coverage maintained
- **Scope**: Business logic, utilities, and service layer functions
- **Execution**: Pre-deployment in CI pipeline

### Integration Tests
- **Scope**: End-to-end API workflows against deployed environments
- **Execution**: Post-deployment validation for dev environment
- **Tools**: pytest with httpx for async API testing

### Performance Tests
- **Scope**: Baseline performance validation and regression detection
- **Tools**: k6 for load testing
- **Thresholds**: 95th percentile response time <500ms, error rate <10%

### Smoke Tests
- **Scope**: Critical path validation for production deployments
- **Execution**: Manual trigger before production traffic routing
- **Coverage**: Authentication, core API endpoints, database connectivity

## Deployment Considerations

### Database Migration Strategy
- **Backward Compatible**: All migrations must support rollback
- **Validation**: Post-migration data integrity checks
- **Rollback**: Automated snapshot creation before migrations

### Environment Variables
```bash
# Development
ENVIRONMENT=dev
DATABASE_URL=postgresql://user:pass@dev-db:5432/conflicto_dev
DEBUG_MODE=true
APP_VERSION=${GITHUB_SHA}

# Production
ENVIRONMENT=prod
DATABASE_URL=postgresql://user:pass@prod-db:5432/conflicto_prod
DEBUG_MODE=false
APP_VERSION=${GITHUB_SHA}
```

### Container Configuration
- **Health Checks**: HTTP health endpoints with 30s intervals
- **Resource Limits**: Environment-specific CPU/memory allocation
- **Secrets**: AWS Systems Manager Parameter Store integration

## Risk Assessment

### High Risk Areas
1. **Database Migrations**: Potential for data loss or corruption
   - **Mitigation**: Automated backups, migration testing, rollback procedures

2. **Service Disruption**: Potential downtime during deployments
   - **Mitigation**: Health checks, deployment validation, rollback procedures

3. **Configuration Management**: Environment-specific secrets and variables
   - **Mitigation**: AWS Parameter Store, environment isolation, audit logging

### Medium Risk Areas
1. **Integration Test Reliability**: Flaky tests blocking deployments
   - **Mitigation**: Test stability validation, retry mechanisms, manual override capability

2. **Resource Scaling**: Insufficient capacity during traffic spikes
   - **Mitigation**: Auto-scaling configuration, capacity planning

### Low Risk Areas
1. **Documentation Drift**: Outdated operational procedures
   - **Mitigation**: Regular review cycles, automated documentation generation

2. **Cost Management**: Unexpected AWS cost increases
   - **Mitigation**: Resource tagging, budget alerts

## Estimated Effort

### Development Time
- **Infrastructure Setup**: 3-4 days (Terraform modules, environment configuration)
- **Application Integration**: 2-3 days (Health checks, configuration management, migrations)
- **Workflow Implementation**: 2-3 days (GitHub Actions, testing integration)
- **Documentation**: 1-2 days (Runbooks, procedures, troubleshooting guides)

### Total Estimate: 8-12 days

### Complexity Assessment
- **High Complexity**: Infrastructure orchestration, deployment automation
- **Medium Complexity**: Integration testing, workflow setup
- **Low Complexity**: Health checks, configuration management

### Dependencies
- **External**: AWS account setup, domain configuration, SSL certificates
- **Internal**: Existing Terraform modules, CI/CD pipeline, container images
- **Team**: DevOps expertise for Terraform, backend development for health checks
