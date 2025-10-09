# CI/CD Pipeline for ECS Deployment

This document explains how to use GitHub Actions with OIDC authentication to build Docker images and deploy them to Amazon ECS.

## Overview

The CI/CD pipeline automates the following workflow:

1. **Authenticate** to AWS using OIDC (no AWS credentials stored in GitHub)
2. **Build** Docker image from your application code
3. **Push** image to Amazon ECR (Elastic Container Registry)
4. **Update** ECS task definition with new image
5. **Deploy** updated task definition to ECS service

## Architecture

```
GitHub Actions (OIDC)
    ↓
AWS STS (Assume Role)
    ↓
Deployer Role (conflicto-terraform-deployer-{env})
    ↓
├── ECR: Push Docker images
├── ECS: Update task definitions
└── ECS: Deploy to services
```

## Prerequisites

### 1. GitHub Repository Variables

Configure these variables in **Settings → Secrets and variables → Actions → Variables**:

#### Environment-Specific Variables

For each environment (dev, staging, prod), create an **Environment** and add:

- **`AWS_DEPLOYER_ROLE_ARN`**: The role ARN for that environment
  - Dev: `arn:aws:iam::418389084763:role/conflicto-terraform-deployer-dev`
  - Staging: `arn:aws:iam::418389084763:role/conflicto-terraform-deployer-staging`
  - Prod: `arn:aws:iam::418389084763:role/conflicto-terraform-deployer-prod`

- **`AWS_REGION`** (optional): AWS region (defaults to `us-west-2`)

### 2. AWS Infrastructure

The following AWS resources must exist (created via Terraform):

#### ECR Repositories
- `conflicto-backend-dev`
- `conflicto-backend-staging`
- `conflicto-backend-prod`

#### ECS Clusters
- `conflicto-dev`
- `conflicto-staging`
- `conflicto-prod`

#### ECS Services
- `conflicto-backend-service-dev`
- `conflicto-backend-service-staging`
- `conflicto-backend-service-prod`

#### ECS Task Definitions
- `conflicto-backend-dev`
- `conflicto-backend-staging`
- `conflicto-backend-prod`

## How It Works

### Step 1: OIDC Authentication

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN }}
    aws-region: us-west-2
```

**What happens:**
1. GitHub Actions generates an OIDC token
2. Token includes repository info: `repo:tristanl-slalom/conflicto:*`
3. AWS STS validates token against OIDC provider
4. IAM role trust policy checks repository match
5. Temporary credentials issued (valid for session duration)

**Security benefits:**
- No AWS credentials stored in GitHub
- Role assumes restricted to specific repository
- Credentials auto-expire after session
- Full AWS CloudTrail audit logging

### Step 2: Build Docker Image

```yaml
- name: Build, tag, and push image to Amazon ECR
  run: |
    cd backend
    docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
```

**What happens:**
1. Workflow checks out repository code
2. Navigates to `backend/` directory
3. Builds Docker image using `backend/Dockerfile`
4. Tags with Git SHA (e.g., `abc1234`) and `latest`

**Image naming convention:**
- Repository: `conflicto-backend-{environment}`
- Tag: `{git-sha-short}` (e.g., `abc1234`)
- Also tagged: `latest`

### Step 3: Push to ECR

```yaml
- name: Login to Amazon ECR
  uses: aws-actions/amazon-ecr-login@v2

- name: Push image
  run: |
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
```

**What happens:**
1. Action uses assumed role credentials to get ECR login token
2. Docker authenticates to ECR registry
3. Image pushed to environment-specific repository
4. Both versioned tag and `latest` tag pushed

**Result:**
```
418389084763.dkr.ecr.us-west-2.amazonaws.com/conflicto-backend-dev:abc1234
418389084763.dkr.ecr.us-west-2.amazonaws.com/conflicto-backend-dev:latest
```

### Step 4: Update Task Definition

```yaml
- name: Download current task definition
  run: |
    aws ecs describe-task-definition \
      --task-definition conflicto-backend-${ENV} \
      --query taskDefinition > task-definition.json

- name: Fill in the new image ID
  uses: aws-actions/amazon-ecs-render-task-definition@v1
  with:
    task-definition: task-definition.json
    container-name: conflicto-backend
    image: ${{ steps.vars.outputs.image_uri }}
```

**What happens:**
1. Downloads current task definition from ECS
2. Updates container image URI to new version
3. Preserves all other task definition settings (CPU, memory, env vars, etc.)

### Step 5: Deploy to ECS

```yaml
- name: Deploy Amazon ECS task definition
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: ${{ steps.task-def.outputs.task-definition }}
    service: conflicto-backend-service-${{ env.ENV }}
    cluster: conflicto-${{ env.ENV }}
    wait-for-service-stability: true
```

**What happens:**
1. Registers new task definition revision
2. Updates ECS service to use new revision
3. ECS performs rolling deployment:
   - Starts new tasks with new image
   - Waits for health checks to pass
   - Drains connections from old tasks
   - Stops old tasks
4. Workflow waits for deployment to complete

## Workflow Triggers

### Automatic Deployment (Dev)

Pushes to `main` branch with changes in `backend/` automatically deploy to dev:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
```

### Manual Deployment (Staging/Prod)

Use **workflow_dispatch** to manually trigger deployments:

1. Go to **Actions** tab in GitHub
2. Select **Build and Deploy Backend to ECS**
3. Click **Run workflow**
4. Choose environment: `staging` or `prod`
5. Click **Run workflow**

## Environment Protection Rules

Configure protection rules in **Settings → Environments**:

### Dev Environment
- ✅ Auto-deploy on push to main
- No approval required

### Staging Environment
- 🔒 Manual approval required
- Reviewers: DevOps team

### Prod Environment
- 🔒 Manual approval required
- 🔒 Require deployment branch: `main` only
- Reviewers: DevOps + Tech Lead

## Monitoring Deployments

### GitHub Actions UI

1. Go to **Actions** tab
2. Click on workflow run
3. View logs for each step
4. Check **Summary** for deployment info

### AWS Console

**ECS Service Events:**
1. Navigate to **ECS → Clusters → conflicto-{env}**
2. Click on service
3. View **Events** tab for deployment progress

**CloudWatch Logs:**
1. Navigate to **CloudWatch → Log groups**
2. Find `/ecs/conflicto-backend-{env}`
3. View application logs from containers

**AWS CloudTrail:**
1. Navigate to **CloudTrail → Event history**
2. Filter by:
   - User name: `conflicto-terraform-deployer-{env}`
   - Event source: `ecs.amazonaws.com`, `ecr.amazonaws.com`

## Rollback Procedure

### Option 1: Rollback via GitHub Actions

1. Re-run previous successful workflow
2. Or manually trigger workflow with older Git SHA

### Option 2: Rollback via AWS Console

1. Navigate to **ECS → Clusters → conflicto-{env}**
2. Click on service → **Deployments** tab
3. Find previous stable task definition revision
4. Click **Update service**
5. Select previous task definition revision
6. Click **Update**

### Option 3: Rollback via AWS CLI

```bash
# List task definition revisions
aws ecs list-task-definitions \
  --family-prefix conflicto-backend-dev

# Update service to previous revision
aws ecs update-service \
  --cluster conflicto-dev \
  --service conflicto-backend-service-dev \
  --task-definition conflicto-backend-dev:5
```

## Troubleshooting

### "Error: Could not assume role"

**Cause:** OIDC authentication failed

**Solutions:**
1. Verify role ARN in environment variable is correct
2. Check workflow has `id-token: write` permission
3. Verify IAM role trust policy includes repository name
4. Check OIDC provider exists in AWS IAM

### "Error: No such image"

**Cause:** ECR repository doesn't exist

**Solutions:**
1. Create ECR repository: `aws ecr create-repository --repository-name conflicto-backend-dev`
2. Or deploy ECR infrastructure via Terraform first

### "Error: Unable to describe task definition"

**Cause:** ECS task definition doesn't exist yet

**Solutions:**
1. Create initial task definition manually or via Terraform
2. Or modify workflow to create task definition if it doesn't exist

### "Deployment failed: Service did not stabilize"

**Cause:** New tasks failed health checks

**Solutions:**
1. Check CloudWatch logs for application errors
2. Verify Docker image builds and runs locally
3. Check ECS service health check configuration
4. Verify security groups allow ALB → ECS traffic

### "Error: AccessDenied for ECR operations"

**Cause:** IAM role lacks ECR permissions

**Solutions:**
1. Verify role has `ECRManagement` statement in inline policy
2. Check policy includes `ecr:*` actions
3. Ensure role assumption worked (check `aws sts get-caller-identity`)

## Best Practices

### Image Tagging Strategy

✅ **Do:**
- Tag with Git SHA for traceability: `abc1234`
- Also tag as `latest` for convenience
- Consider semantic versioning for releases: `v1.2.3`

❌ **Don't:**
- Use only `latest` (makes rollback difficult)
- Use random/incrementing numbers without Git reference

### Deployment Strategy

✅ **Do:**
- Auto-deploy to dev on every merge to main
- Require manual approval for staging/prod
- Wait for service stability before completing
- Include deployment summary in workflow output

❌ **Don't:**
- Auto-deploy to prod without approval
- Skip health checks to speed up deployment
- Deploy without testing in lower environment first

### Security

✅ **Do:**
- Use OIDC (no stored credentials)
- Restrict IAM roles to specific repository
- Use environment-specific roles (dev/staging/prod)
- Enable CloudTrail logging
- Scan images for vulnerabilities (Trivy, Snyk, etc.)

❌ **Don't:**
- Store AWS credentials in GitHub secrets
- Use same role for all environments
- Grant broader permissions than needed
- Skip image scanning

### Monitoring

✅ **Do:**
- Monitor ECS service metrics (CPU, memory, task count)
- Set up CloudWatch alarms for deployment failures
- Review CloudWatch logs for application errors
- Track deployment frequency and success rate

## Example: Complete Setup

### 1. Create GitHub Environment

**Settings → Environments → New environment**

Name: `dev`

**Environment variables:**
- `AWS_DEPLOYER_ROLE_ARN`: `arn:aws:iam::418389084763:role/conflicto-terraform-deployer-dev`
- `AWS_REGION`: `us-west-2`

### 2. Deploy Infrastructure (Terraform)

```bash
cd infrastructure/environments/dev
terraform init
terraform plan
terraform apply
```

This creates:
- ECR repository
- ECS cluster
- ECS service
- ECS task definition
- ALB target group

### 3. Push Code and Deploy

```bash
git add .
git commit -m "feat: Add backend API"
git push origin main
```

GitHub Actions automatically:
1. Authenticates via OIDC
2. Builds Docker image
3. Pushes to ECR
4. Deploys to ECS dev environment

### 4. Verify Deployment

**Check GitHub Actions:**
```
Actions → Build and Deploy Backend to ECS → [latest run]
```

**Check ECS:**
```bash
aws ecs describe-services \
  --cluster conflicto-dev \
  --services conflicto-backend-service-dev
```

**Test endpoint:**
```bash
curl https://api-dev.conflicto.com/health
```

## Next Steps

1. ✅ Set up OIDC provider and roles (Issue #64) - **COMPLETE**
2. ⏳ Create ECR repositories via Terraform
3. ⏳ Create ECS cluster and services via Terraform
4. ⏳ Set up GitHub environment variables
5. ⏳ Test deployment workflow
6. ⏳ Add image vulnerability scanning
7. ⏳ Set up deployment notifications (Slack/email)
8. ⏳ Configure auto-rollback on failed health checks

## Related Documentation

- [IAM OIDC Setup Guide](./IAM_OIDC_SETUP.md) - Manual setup of OIDC provider and roles
- [GitHub Actions OIDC](./GITHUB_ACTIONS_OIDC.md) - OIDC usage examples
- [Infrastructure README](../infrastructure/README.md) - Infrastructure overview
- [Backend README](../backend/README.md) - Backend application setup

## References

- [AWS Actions: Configure AWS Credentials](https://github.com/aws-actions/configure-aws-credentials)
- [AWS Actions: Amazon ECR Login](https://github.com/aws-actions/amazon-ecr-login)
- [AWS Actions: Amazon ECS Deploy Task Definition](https://github.com/aws-actions/amazon-ecs-deploy-task-definition)
- [GitHub OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
