# Quick Start: GitHub Actions to ECS Deployment

## TL;DR - How It Works

1. **Push code** to `main` branch
2. **GitHub Actions** authenticates via OIDC (no credentials needed!)
3. **Docker image** built from your code
4. **Image pushed** to Amazon ECR
5. **ECS service** updated with new image
6. **Done!** Your app is running on AWS

## Setup Checklist

### ✅ Already Complete (Issue #64)

- [x] OIDC provider created
- [x] IAM roles created (dev, staging, prod)
- [x] Roles imported into Terraform

### ⏳ Next Steps

#### 1. Create GitHub Environment Variables

Go to **Settings → Environments** in GitHub:

**Create "dev" environment:**
- Variable: `AWS_DEPLOYER_ROLE_ARN` = `arn:aws:iam::418389084763:role/conflicto-terraform-deployer-dev`
- Variable: `AWS_REGION` = `us-east-1`

**Create "staging" environment:**
- Variable: `AWS_DEPLOYER_ROLE_ARN` = `arn:aws:iam::418389084763:role/conflicto-terraform-deployer-staging`
- Variable: `AWS_REGION` = `us-east-1`
- Protection rule: Require 1 approval

**Create "prod" environment:**
- Variable: `AWS_DEPLOYER_ROLE_ARN` = `arn:aws:iam::418389084763:role/conflicto-terraform-deployer-prod`
- Variable: `AWS_REGION` = `us-east-1`
- Protection rule: Require 2 approvals

#### 2. Deploy AWS Infrastructure (Terraform)

This creates ECR, ECS cluster, services, etc.:

```bash
# Dev environment
cd infrastructure/environments/dev
terraform init
terraform apply

# Staging environment (when ready)
cd infrastructure/environments/staging
terraform init
terraform apply

# Prod environment (when ready)
cd infrastructure/environments/prod
terraform init
terraform apply
```

#### 3. Use the Workflow

The workflow file is already created at `.github/workflows/deploy-backend.yml`

**Automatic deployment to dev:**
```bash
git add backend/
git commit -m "feat: Update backend"
git push origin main
```
→ Auto-deploys to dev environment

**Manual deployment to staging/prod:**
1. Go to **Actions** tab in GitHub
2. Click **Build and Deploy Backend to ECS**
3. Click **Run workflow**
4. Select environment: `staging` or `prod`
5. Click **Run workflow**
6. Approve if required

## What the Workflow Does

```mermaid
graph LR
    A[Push Code] --> B[Checkout]
    B --> C[OIDC Auth]
    C --> D[Build Docker]
    D --> E[Push to ECR]
    E --> F[Update Task Def]
    F --> G[Deploy to ECS]
    G --> H[Wait for Stability]
    H --> I[Done!]
```

## Example Output

When workflow runs successfully:

```
✅ Deployment Summary

- Environment: dev
- Image: `418389084763.dkr.ecr.us-east-1.amazonaws.com/conflicto-backend-dev:abc1234`
- Cluster: conflicto-dev
- Service: conflicto-backend-service-dev
- Git SHA: abc1234567890

✅ Deployment successful!
```

## Common Commands

**View ECS service status:**
```bash
aws ecs describe-services \
  --cluster conflicto-dev \
  --services conflicto-backend-service-dev \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'
```

**View container logs:**
```bash
aws logs tail /ecs/conflicto-backend-dev --follow
```

**List ECR images:**
```bash
aws ecr list-images \
  --repository-name conflicto-backend-dev \
  --query 'imageIds[*].imageTag' \
  --output table
```

**Rollback to previous version:**
```bash
# Find previous task definition
aws ecs list-task-definitions --family-prefix conflicto-backend-dev

# Update service to previous revision
aws ecs update-service \
  --cluster conflicto-dev \
  --service conflicto-backend-service-dev \
  --task-definition conflicto-backend-dev:PREVIOUS_REVISION_NUMBER
```

## Security Benefits of OIDC

✅ **No AWS credentials in GitHub**
- Credentials never stored anywhere
- Can't be leaked or stolen
- Auto-expire after each session

✅ **Repository-scoped access**
- Roles only work from `tristanl-slalom/conflicto` repo
- Forked repos can't assume the role
- External actors can't use the credentials

✅ **Full audit trail**
- Every deployment logged in CloudTrail
- See exactly who deployed what and when
- Track back to specific GitHub workflow run

## Troubleshooting

**Problem:** "Could not assume role"
- **Fix:** Check `AWS_DEPLOYER_ROLE_ARN` is set correctly in GitHub environment variables

**Problem:** "No such repository in ECR"
- **Fix:** Run `terraform apply` to create ECR repository first

**Problem:** "Service did not stabilize"
- **Fix:** Check CloudWatch logs: `aws logs tail /ecs/conflicto-backend-dev --follow`

**Problem:** "Access denied to ECR"
- **Fix:** Verify IAM role has ECR permissions (should already have `ecr:*`)

## Related Documentation

- **[CICD_ECS_DEPLOYMENT.md](./CICD_ECS_DEPLOYMENT.md)** - Complete detailed guide
- **[IAM_OIDC_SETUP.md](./IAM_OIDC_SETUP.md)** - OIDC setup guide (already done)
- **[GITHUB_ACTIONS_OIDC.md](./GITHUB_ACTIONS_OIDC.md)** - More workflow examples
