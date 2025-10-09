# IAM OIDC Provider & Terraform Deployer Roles

This Terraform stack provisions GitHub Actions authentication infrastructure for automated CI/CD deployments.

## Overview

Creates:
- AWS IAM OIDC identity provider for GitHub Actions
- Three environment-scoped IAM roles (dev, staging, prod)
- Repository-restricted trust policies
- Permissions for infrastructure phases 0-5

## Resources Created

1. **OIDC Provider:** `token.actions.githubusercontent.com`
2. **IAM Roles:**
   - `conflicto-terraform-deployer-dev`
   - `conflicto-terraform-deployer-staging`
   - `conflicto-terraform-deployer-prod`

## Usage

### Initial Deployment

```bash
cd infrastructure/iam
terraform init
terraform plan
terraform apply
```

### Get Role ARNs

```bash
terraform output deployer_role_arns
```

### Use in GitHub Actions

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN_DEV }}
    aws-region: us-west-2
```

## Configuration

### Variables

- `aws_region` - AWS region (default: us-west-2)
- `environments` - Environment list (default: [dev, staging, prod])
- `github_repository` - Repository in `owner/repo` format
- `github_oidc_thumbprint` - GitHub OIDC certificate thumbprint
- `max_session_duration` - Session duration in seconds (1-12 hours)

### Outputs

- `oidc_provider_arn` - OIDC provider ARN
- `deployer_role_arns` - Map of role ARNs by environment
- Individual role ARNs for easy reference

## Permission Scope

Roles can manage:
- Remote state (S3 + DynamoDB)
- Networking (VPC, subnets, security groups)
- DNS and certificates (Route53, ACM)
- Databases (RDS, Secrets Manager)
- Compute (ECS, ECR, ALB)
- Observability (CloudWatch, SNS)

**PassRole:** Limited to ECS task execution roles only.

## Security Notes

### Trust Policy

- Restricted to repository: `tristanl-slalom/conflicto`
- Cannot restrict by branch (OIDC limitation)
- Audience verification: `sts.amazonaws.com`

### Permissions

- All wildcards marked with Phase 10 hardening TODOs
- Secrets Manager scoped to `conflicto-*` prefix
- PassRole requires `ecs-tasks.amazonaws.com` service

## Maintenance

### Updating Thumbprint

If GitHub rotates certificates:

```bash
# Get new thumbprint
openssl s_client -servername token.actions.githubusercontent.com \
  -showcerts -connect token.actions.githubusercontent.com:443 < /dev/null 2>/dev/null \
  | openssl x509 -fingerprint -sha1 -noout -in /dev/stdin \
  | sed 's/://g' | awk -F= '{print tolower($2)}'

# Update variable and apply
terraform apply -var="github_oidc_thumbprint=NEW_THUMBPRINT"
```

### Phase 10 Hardening

See policy TODOs for specific refinements:
- Replace wildcards with resource ARN patterns
- Add tag-based conditions
- Differentiate dev/staging/prod permissions

## Troubleshooting

### "No identity-based policy allows the sts:AssumeRoleWithWebIdentity action"

Check:
- OIDC provider exists and thumbprint is current
- Trust policy `sub` condition matches repository
- GitHub Actions workflow uses correct role ARN

### "User is not authorized to perform: iam:CreateOpenIDConnectProvider"

Your AWS user lacks IAM permissions. Request admin assistance or use elevated credentials.

## Related Issues

- #57 - CI/CD Terraform Workflow (consumes these role ARNs)
- #47 - Remote State Backend (provides S3 + DynamoDB)
