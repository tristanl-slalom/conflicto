# Technical Specification: Implement Continuous Deployment Pipeline with Dev/Prod Environments

**GitHub Issue:** [#76](https://github.com/tristanl-slalom/conflicto/issues/76)
**Generated:** 2025-10-08T19:31:46Z

## Problem Statement

The Conflicto application currently has comprehensive CI/CD testing and building infrastructure but lacks automated deployment capabilities to AWS environments. The project needs a continuous deployment pipeline that builds on existing Terraform infrastructure and GitHub Actions to automatically deploy to AWS with proper environment separation, integration testing, and promotion gates.

## Technical Requirements

### 1. Environment Architecture

#### Development Environment
- **Trigger**: Automatic deployment on main branch commits
- **Infrastructure**: ECS Fargate services, RDS PostgreSQL, Application Load Balancer
- **Domain**: dev.conflicto.app (or similar subdomain)
- **Testing**: Full integration test suite execution post-deployment
- **Database**: Separate dev database instance with test data

#### Production Environment
- **Trigger**: Manual approval-gated deployment
- **Infrastructure**: ECS Fargate services, RDS PostgreSQL, Application Load Balancer
- **Domain**: conflicto.app (production domain)
- **Testing**: Smoke tests and manual QA validation
- **Database**: Production database with backup/restore capabilities

### 2. Terraform Infrastructure Updates

#### Environment Separation Strategy
- **Terraform Workspaces**: Use separate workspaces for dev/prod environments
- **State Management**: Separate state files per environment in S3 backend
- **Variable Management**: Environment-specific terraform.tfvars files
- **Resource Naming**: Environment prefix for all AWS resources

#### Required Terraform Modules Enhancement
```hcl
# Enhanced ECS module for deployment automation
module "ecs_service" {
  source = "./modules/ecs"

  environment             = var.environment
  task_definition_family  = "conflicto-${var.environment}"
  container_definitions   = templatefile("task-definitions/${var.environment}.json", {
    backend_image  = var.backend_image_uri
    frontend_image = var.frontend_image_uri
    db_host       = module.rds.endpoint
    environment   = var.environment
  })

  # Blue/green deployment support
  deployment_configuration = {
    maximum_percent         = 200
    minimum_healthy_percent = 50
    deployment_circuit_breaker = {
      enable   = true
      rollback = true
    }
  }
}

# Enhanced RDS module with environment-specific sizing
module "rds" {
  source = "./modules/rds"

  environment     = var.environment
  instance_class  = var.environment == "prod" ? "db.r6g.large" : "db.t4g.micro"
  allocated_storage = var.environment == "prod" ? 100 : 20

  # Automated backups for prod
  backup_retention_period = var.environment == "prod" ? 7 : 1
  backup_window          = var.environment == "prod" ? "03:00-04:00" : null
}
```

### 3. GitHub Actions Workflow Specifications

#### 3.1 Dev Deployment Workflow (.github/workflows/deploy-dev.yml)
```yaml
name: Deploy to Development
on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - '*.md'

jobs:
  deploy-infrastructure:
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - name: Deploy Terraform
        working-directory: iac/stacks/dev
        run: |
          terraform init
          terraform plan -var-file=dev.tfvars
          terraform apply -auto-approve -var-file=dev.tfvars
    outputs:
      backend_service_name: ${{ steps.terraform.outputs.backend_service_name }}
      frontend_service_name: ${{ steps.terraform.outputs.frontend_service_name }}

  deploy-applications:
    needs: deploy-infrastructure
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - name: Update ECS Services
        run: |
          # Update backend service
          aws ecs update-service \
            --cluster conflicto-dev \
            --service ${{ needs.deploy-infrastructure.outputs.backend_service_name }} \
            --task-definition conflicto-backend-dev:${{ github.sha }}

          # Update frontend service
          aws ecs update-service \
            --cluster conflicto-dev \
            --service ${{ needs.deploy-infrastructure.outputs.frontend_service_name }} \
            --task-definition conflicto-frontend-dev:${{ github.sha }}
```

#### 3.2 Production Deployment Workflow (.github/workflows/deploy-prod.yml)
```yaml
name: Deploy to Production
on:
  workflow_dispatch:
    inputs:
      image_tag:
        description: 'Container image tag to deploy'
        required: true
        type: string

jobs:
  deploy-production:
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
          issue-title: "Production Deployment Approval for ${{ github.event.inputs.image_tag }}"
```

### 4. Application Configuration Requirements

#### 4.1 Environment Detection
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    environment: str = Field(default="dev", env="ENVIRONMENT")

    # Database configuration per environment
    database_url: str = Field(env="DATABASE_URL")

    # Environment-specific feature flags
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")

    # AWS configuration
    aws_region: str = Field(default="us-west-2", env="AWS_REGION")

    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"
```

#### 4.2 Health Check Endpoints
```python
# backend/app/routes/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": os.getenv("APP_VERSION", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/deep")
async def deep_health_check(db: Session = Depends(get_db)):
    # Database connectivity check
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "environment": settings.environment
    }
```

### 5. Database Migration Strategy

#### 5.1 Automated Migration Execution
```python
# Migration runner for deployment pipeline
async def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    # Run migrations
    command.upgrade(alembic_cfg, "head")

    # Verify migration success
    command.current(alembic_cfg)
```

#### 5.2 Migration Safety Checks
- **Backward Compatibility**: All migrations must be backward compatible
- **Zero Downtime**: Use online schema changes for production
- **Rollback Plan**: Each migration must have explicit downgrade path
- **Data Validation**: Post-migration data integrity checks

### 6. Integration Testing Specifications

#### 6.1 End-to-End Test Suite
```typescript
// Integration test structure for deployed environments
describe('Deployed Environment Integration Tests', () => {
  const baseUrl = process.env.TEST_BASE_URL || 'https://dev.conflicto.app';

  test('API Health Check', async () => {
    const response = await fetch(`${baseUrl}/api/health`);
    expect(response.status).toBe(200);

    const health = await response.json();
    expect(health.status).toBe('healthy');
    expect(health.environment).toBeDefined();
  });

  test('Database Connectivity', async () => {
    const response = await fetch(`${baseUrl}/api/health/deep`);
    const health = await response.json();
    expect(health.database).toBe('healthy');
  });

  test('Frontend-Backend Integration', async () => {
    // Test complete user workflow
    // Session creation, activity execution, data persistence
  });
});
```

#### 6.2 Performance Baseline Tests
- **Load Testing**: Artillery/k6 scripts for performance regression detection
- **Response Time Monitoring**: API endpoint response time thresholds
- **Resource Utilization**: ECS task CPU/memory consumption validation

### 7. Monitoring and Observability

#### 7.1 CloudWatch Integration
```yaml
# CloudWatch Log Groups
log_groups:
  - name: "/ecs/conflicto-backend-${environment}"
    retention_in_days: 14
  - name: "/ecs/conflicto-frontend-${environment}"
    retention_in_days: 14

# CloudWatch Alarms
alarms:
  - name: "High-Error-Rate-${environment}"
    metric: "HTTPCode_Target_5XX_Count"
    threshold: 10
    comparison: "GreaterThanThreshold"
```

#### 7.2 Application Metrics
```python
# Custom metrics collection
from prometheus_client import Counter, Histogram, generate_latest

# Business metrics
deployment_counter = Counter('deployments_total', 'Total deployments', ['environment'])
response_time_histogram = Histogram('http_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response_time_histogram.observe(process_time)
    return response
```

### 8. Security Requirements

#### 8.1 IAM Roles and Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:RegisterTaskDefinition"
      ],
      "Resource": [
        "arn:aws:ecs:*:*:service/conflicto-${environment}/*",
        "arn:aws:ecs:*:*:task-definition/conflicto-*:*"
      ]
    }
  ]
}
```

#### 8.2 Secrets Management
- **AWS Systems Manager Parameter Store**: Environment-specific configuration
- **GitHub Secrets**: Deployment credentials and sensitive values
- **Container Environment Variables**: Runtime configuration injection

### 9. Rollback Mechanisms

#### 9.1 ECS Service Rollback
```bash
# Emergency rollback script
aws ecs update-service \
  --cluster conflicto-${ENVIRONMENT} \
  --service conflicto-backend-${ENVIRONMENT} \
  --task-definition $(aws ecs describe-services \
    --cluster conflicto-${ENVIRONMENT} \
    --services conflicto-backend-${ENVIRONMENT} \
    --query 'services[0].deployments[1].taskDefinition' \
    --output text)
```

#### 9.2 Database Rollback Strategy
- **Backup Before Migration**: Automated RDS snapshot before each deployment
- **Point-in-Time Recovery**: RDS PITR capability for emergency rollback
- **Migration Rollback**: Alembic downgrade scripts for schema rollback

## API Specifications

### Deployment Status API
```yaml
/api/deployment:
  get:
    summary: Get current deployment information
    responses:
      200:
        description: Deployment status
        content:
          application/json:
            schema:
              type: object
              properties:
                environment:
                  type: string
                  enum: [dev, prod]
                version:
                  type: string
                  description: Git SHA or tag
                deployed_at:
                  type: string
                  format: date-time
                status:
                  type: string
                  enum: [healthy, degraded, unhealthy]
```

## Data Models

### Deployment Tracking
```python
# Track deployment history and status
class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True)
    environment = Column(String(10), nullable=False)  # dev/prod
    version = Column(String(40), nullable=False)      # Git SHA
    deployed_at = Column(DateTime, default=datetime.utcnow)
    deployed_by = Column(String(100))                 # GitHub actor
    status = Column(String(20), default="deploying")  # deploying/success/failed
    rollback_version = Column(String(40), nullable=True)

    # Deployment metadata
    pull_request_number = Column(Integer, nullable=True)
    commit_message = Column(Text)
    deployment_duration = Column(Integer)  # seconds
```

## Integration Points

### 1. GitHub Actions Integration
- **Workflow Triggers**: Push to main (dev), workflow_dispatch (prod)
- **Environment Protection**: Required reviewers for production deployments
- **Artifact Management**: Container images from GHCR registry

### 2. AWS Services Integration
- **ECS Fargate**: Container orchestration and deployment
- **RDS PostgreSQL**: Database management and migration execution
- **Application Load Balancer**: Traffic routing and health checks
- **CloudWatch**: Logging, metrics, and alerting
- **Systems Manager**: Parameter Store for configuration management

### 3. External Services
- **GitHub Container Registry**: Container image storage and retrieval
- **Slack/Teams**: Deployment notifications and approval requests
- **DataDog/New Relic** (future): Advanced APM and monitoring

## Acceptance Criteria

### Infrastructure Deployment
- [ ] Terraform successfully provisions dev environment on main branch commits
- [ ] Terraform provisions prod environment with manual approval gate
- [ ] Environment separation maintained with proper resource naming
- [ ] RDS databases configured with appropriate sizing per environment

### Application Deployment
- [ ] ECS services updated with new container images automatically
- [ ] Database migrations executed safely during deployment
- [ ] Zero-downtime deployments achieved through blue/green strategy
- [ ] Health checks validate deployment success before traffic routing

### Testing and Validation
- [ ] Integration tests execute against live dev environment post-deployment
- [ ] Production smoke tests validate critical functionality
- [ ] Performance baseline tests detect regressions
- [ ] Manual approval gate prevents unauthorized production deployments

### Monitoring and Operations
- [ ] CloudWatch dashboards display deployment and application metrics
- [ ] Deployment notifications sent to appropriate channels
- [ ] Rollback procedures tested and documented
- [ ] All deployment activities logged and auditable

### Security and Compliance
- [ ] IAM roles follow least privilege principle
- [ ] Secrets managed through AWS Parameter Store
- [ ] Network isolation maintained between environments
- [ ] Audit trail captures all deployment activities

## Assumptions & Constraints

### Technical Assumptions
- **Container Registry**: GitHub Container Registry (GHCR) continues as image store
- **AWS Region**: Single region deployment (us-west-2) for MVP
- **Database Strategy**: Separate RDS instances per environment (no cross-environment sharing)
- **SSL/TLS**: AWS Certificate Manager provides SSL certificates

### Operational Constraints
- **Deployment Windows**: No maintenance windows required for dev; prod deployments during business hours
- **Cost Management**: Dev environment sized for cost optimization, prod sized for performance
- **Team Access**: Limited production access with audit logging requirements
- **Backup Strategy**: 7-day retention for prod, 1-day for dev

### Business Constraints
- **Approval Process**: Production deployments require manual approval from technical lead
- **Rollback SLA**: < 5 minute rollback capability for emergency situations
- **Uptime Requirements**: 99.9% uptime target for production environment
- **Security Compliance**: SOC 2 Type II readiness for future compliance audits
