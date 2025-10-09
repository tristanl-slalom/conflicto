# GitHub Actions OIDC Authentication - Usage Examples

This document provides examples of using the GitHub Actions OIDC provider and Terraform deployer roles in CI/CD workflows.

## Prerequisites

- IAM OIDC provider and deployer roles created (see `IAM_OIDC_SETUP.md`)
- Repository variables configured with role ARNs

## Basic Usage

### Configure AWS Credentials in Workflow

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN_DEV }}
          aws-region: us-west-2
          role-session-name: GitHubActions-${{ github.run_id }}
      
      - name: Verify AWS Identity
        run: aws sts get-caller-identity
      
      - name: Deploy with Terraform
        run: |
          cd infrastructure/iam
          terraform init
          terraform plan
          terraform apply -auto-approve
```

## Environment-Specific Deployments

### Dev Environment (Auto-Deploy)

```yaml
name: Deploy to Dev

on:
  push:
    branches: [main]
    paths:
      - 'infrastructure/**'

permissions:
  id-token: write
  contents: read

jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN_DEV }}
          aws-region: us-west-2
      
      - name: Terraform Apply
        working-directory: infrastructure/iam
        run: |
          terraform init
          terraform apply -auto-approve
```

### Staging Environment (Manual Approval)

```yaml
name: Deploy to Staging

on:
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging  # Requires manual approval in GitHub
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN_STAGING }}
          aws-region: us-west-2
      
      - name: Terraform Apply
        working-directory: infrastructure/iam
        run: |
          terraform init
          terraform apply -auto-approve
```

### Production Environment (Protected)

```yaml
name: Deploy to Production

on:
  release:
    types: [published]

permissions:
  id-token: write
  contents: read

jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment: production  # Protected environment with required reviewers
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN_PROD }}
          aws-region: us-west-2
          role-session-name: GitHubActions-Prod-${{ github.run_id }}
      
      - name: Terraform Plan
        id: plan
        working-directory: infrastructure/iam
        run: |
          terraform init
          terraform plan -out=tfplan
      
      - name: Terraform Apply
        working-directory: infrastructure/iam
        run: terraform apply tfplan
```

## Multi-Stack Deployment

Deploy multiple infrastructure stacks in sequence:

```yaml
name: Deploy All Infrastructure

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars[format('AWS_DEPLOYER_ROLE_ARN_{0}', github.event.inputs.environment)] }}
          aws-region: us-west-2
      
      - name: Deploy IAM Stack
        working-directory: infrastructure/iam
        run: |
          terraform init
          terraform apply -auto-approve
      
      - name: Deploy Network Stack
        working-directory: infrastructure/network
        run: |
          terraform init
          terraform apply -auto-approve
      
      - name: Deploy ECS Stack
        working-directory: infrastructure/ecs
        run: |
          terraform init
          terraform apply -auto-approve
```

## Pull Request Plan Preview

Show Terraform plan in PR comments:

```yaml
name: Terraform Plan on PR

on:
  pull_request:
    paths:
      - 'infrastructure/**'

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN_DEV }}
          aws-region: us-west-2
      
      - name: Terraform Plan
        id: plan
        working-directory: infrastructure/iam
        run: |
          terraform init
          terraform plan -no-color | tee plan.txt
      
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('infrastructure/iam/plan.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Terraform Plan\n\`\`\`\n${plan}\n\`\`\``
            });
```

## Repository Variables Setup

Configure these variables in GitHub repository settings:

### Variables → Repository Variables

```
AWS_DEPLOYER_ROLE_ARN_DEV     = arn:aws:iam::418389084763:role/conflicto-terraform-deployer-dev
AWS_DEPLOYER_ROLE_ARN_STAGING = arn:aws:iam::418389084763:role/conflicto-terraform-deployer-staging
AWS_DEPLOYER_ROLE_ARN_PROD    = arn:aws:iam::418389084763:role/conflicto-terraform-deployer-prod
```

### Environment Secrets (Optional)

For environment-specific configurations:

1. Settings → Environments → Create `dev`, `staging`, `prod`
2. Add protection rules (required reviewers for staging/prod)
3. Add environment variables if needed

## Security Best Practices

### 1. Use Minimal Permissions

```yaml
permissions:
  id-token: write    # Required for OIDC
  contents: read     # Only if checking out code
  # Don't grant unnecessary permissions
```

### 2. Explicit Role Session Names

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN_DEV }}
    role-session-name: GitHubActions-${{ github.workflow }}-${{ github.run_id }}
    aws-region: us-west-2
```

This helps with CloudTrail auditing.

### 3. Environment Protection Rules

- **Dev:** No protection, auto-deploy on push
- **Staging:** Require manual approval from team lead
- **Prod:** Require 2 reviewers + branch protection

### 4. Condition on Terraform Apply

```yaml
- name: Terraform Apply
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: terraform apply -auto-approve
```

### 5. Use Terraform Backend Encryption

Already configured in `backend.tf`:
```hcl
backend "s3" {
  encrypt = true
}
```

## Troubleshooting

### Error: "Unable to get OIDC token"

**Cause:** Workflow doesn't have `id-token: write` permission

**Fix:**
```yaml
permissions:
  id-token: write
  contents: read
```

### Error: "Not authorized to perform: sts:AssumeRoleWithWebIdentity"

**Cause:** Trust policy mismatch or wrong repository

**Fix:** Verify trust policy `sub` condition:
```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": "repo:tristanl-slalom/conflicto:*"
}
```

### Error: "Access Denied" during Terraform operations

**Cause:** Role lacks necessary permissions

**Fix:** Review inline policy in IAM role, ensure all required actions are included

### Session Duration Issues

**Cause:** Long-running workflows exceed 1-hour default

**Fix:** Increase `max_session_duration` in `infrastructure/iam/variables.tf`:
```hcl
variable "max_session_duration" {
  default = 7200  # 2 hours
}
```

## Advanced Patterns

### Matrix Strategy for Multi-Environment

```yaml
jobs:
  deploy:
    strategy:
      matrix:
        environment: [dev, staging, prod]
        include:
          - environment: dev
            auto_approve: true
          - environment: staging
            auto_approve: false
          - environment: prod
            auto_approve: false
    
    runs-on: ubuntu-latest
    environment: ${{ matrix.environment }}
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars[format('AWS_DEPLOYER_ROLE_ARN_{0}', matrix.environment)] }}
          aws-region: us-west-2
      
      - name: Terraform Apply
        run: |
          cd infrastructure/iam
          terraform init
          terraform apply ${{ matrix.auto_approve && '-auto-approve' || '' }}
```

### Conditional Role Selection

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ 
      github.ref == 'refs/heads/main' && vars.AWS_DEPLOYER_ROLE_ARN_PROD ||
      github.ref == 'refs/heads/staging' && vars.AWS_DEPLOYER_ROLE_ARN_STAGING ||
      vars.AWS_DEPLOYER_ROLE_ARN_DEV
    }}
    aws-region: us-west-2
```

## Related Documentation

- [AWS Configure Credentials Action](https://github.com/aws-actions/configure-aws-credentials)
- [GitHub OIDC with AWS Guide](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [IAM OIDC Setup Guide](./IAM_OIDC_SETUP.md)
- [Infrastructure IAM README](../infrastructure/iam/README.md)
