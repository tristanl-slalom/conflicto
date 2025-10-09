# Implementation Plan: Phase 0.5 - IAM OIDC Provider & Terraform Deployer Roles

**GitHub Issue:** [#64](https://github.com/tristanl-slalom/conflicto/issues/64)
**Generated:** 2025-10-08
**Branch:** `feature/issue-64-phase-0-5-iam-oidc-provider-terraform-deployer-roles`

## Implementation Strategy

### High-Level Approach

Create a new Terraform stack in `infrastructure/iam/` that provisions:
1. AWS IAM OIDC identity provider for GitHub Actions
2. Three environment-scoped IAM roles (dev, staging, prod)
3. Repository-restricted trust policies
4. Inline permission policies covering phases 0-5 infrastructure

The stack will be isolated from bootstrap infrastructure to allow independent lifecycle management while using the same S3 remote state backend.

### Key Design Decisions

1. **Inline Policies vs Managed Policies:** Use inline policies to keep permissions co-located with roles and facilitate future per-environment differentiation
2. **Single OIDC Provider:** Share one provider across all environments for simplicity
3. **For_each Pattern:** Use Terraform for_each to create roles from environment list, ensuring consistency
4. **Wildcard Documentation:** Mark all wildcard permissions with TODO comments for Phase 10 hardening
5. **Output Strategy:** Provide both map and individual role ARNs for flexible workflow integration

## File Structure Changes

### New Files

```
infrastructure/iam/
├── main.tf              # OIDC provider + IAM roles + policies
├── variables.tf         # Input variables (region, environments, repo)
├── outputs.tf           # Role ARNs and provider ARN
├── backend.tf           # S3 remote state configuration
└── README.md           # Documentation and usage instructions
```

### Modified Files

- `infrastructure/README.md` - Add section documenting IAM stack and CI/CD auth flow
- `.copilot/iac.md` - Update with Phase 0.5 completion status

### No Changes Required

- Bootstrap infrastructure remains untouched
- GitHub Actions workflows (handled in #57)

## Implementation Steps

### Step 1: Create Infrastructure Directory and Backend Configuration

**File:** `infrastructure/iam/backend.tf`

```hcl
terraform {
  backend "s3" {
    bucket         = "conflicto-terraform-state-418389084763"
    key            = "iam/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "conflicto-terraform-locks"
    encrypt        = true
  }
}
```

**Validation:** Backend references existing Phase 0 resources

### Step 2: Define Provider and Variables

**File:** `infrastructure/iam/variables.tf`

```hcl
variable "aws_region" {
  description = "AWS region for provider configuration"
  type        = string
  default     = "us-west-2"
}

variable "environments" {
  description = "List of environments for deployer roles"
  type        = list(string)
  default     = ["dev", "staging", "prod"]
}

variable "github_repository" {
  description = "GitHub repository in format owner/repo"
  type        = string
  default     = "tristanl-slalom/conflicto"
  
  validation {
    condition     = can(regex("^[^/]+/[^/]+$", var.github_repository))
    error_message = "Repository must be in format 'owner/repo'."
  }
}

variable "github_oidc_thumbprint" {
  description = "GitHub OIDC provider thumbprint"
  type        = string
  default     = "6938fd4d98bab03faadb97b34396831e3780aea1"
}

variable "max_session_duration" {
  description = "Maximum CLI/API session duration in seconds (1-12 hours)"
  type        = number
  default     = 3600
  
  validation {
    condition     = var.max_session_duration >= 3600 && var.max_session_duration <= 43200
    error_message = "Session duration must be between 3600 (1 hour) and 43200 (12 hours)."
  }
}
```

**File:** `infrastructure/iam/main.tf` (provider block)

```hcl
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
```

### Step 3: Create OIDC Provider Resource

**File:** `infrastructure/iam/main.tf` (add OIDC provider)

```hcl
# GitHub Actions OIDC Provider
resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
  
  client_id_list = [
    "sts.amazonaws.com"
  ]
  
  thumbprint_list = [
    var.github_oidc_thumbprint
  ]
  
  tags = {
    Name        = "github-actions-oidc"
    Project     = "conflicto"
    ManagedBy   = "terraform"
    Description = "OIDC provider for GitHub Actions CI/CD"
  }
}
```

**Notes:**
- GitHub's thumbprint may change; documented in README for maintenance
- Single provider shared across all environments

### Step 4: Create IAM Roles with Trust Policies

**File:** `infrastructure/iam/main.tf` (add roles)

```hcl
# Terraform Deployer Roles (per environment)
resource "aws_iam_role" "terraform_deployer" {
  for_each = toset(var.environments)
  
  name        = "conflicto-terraform-deployer-${each.key}"
  description = "GitHub Actions role for Terraform deployments to ${each.key} environment"
  
  max_session_duration = var.max_session_duration
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "GitHubActionsOIDC"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:*"
          }
        }
      }
    ]
  })
  
  tags = {
    Name        = "conflicto-terraform-deployer-${each.key}"
    Environment = each.key
    Project     = "conflicto"
    ManagedBy   = "terraform"
    Purpose     = "ci-cd-terraform-deployment"
  }
}
```

**Security Notes:**
- Trust restricted to specific repository
- Cannot restrict by branch (OIDC limitation - documented in README)
- Session duration configurable via variable

### Step 5: Attach Inline Permission Policies

**File:** `infrastructure/iam/main.tf` (add policies)

```hcl
# Permission policies for Terraform deployment
resource "aws_iam_role_policy" "terraform_deployer_policy" {
  for_each = toset(var.environments)
  
  name = "conflicto-terraform-deployer-${each.key}-policy"
  role = aws_iam_role.terraform_deployer[each.key].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Remote State Access
      {
        Sid    = "TerraformStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::conflicto-terraform-state-${data.aws_caller_identity.current.account_id}",
          "arn:aws:s3:::conflicto-terraform-state-${data.aws_caller_identity.current.account_id}/*"
        ]
      },
      {
        Sid    = "TerraformLockAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/conflicto-terraform-locks"
      },
      
      # Networking (Phase 1)
      {
        Sid    = "NetworkingManagement"
        Effect = "Allow"
        Action = [
          "ec2:*Vpc*",
          "ec2:*Subnet*",
          "ec2:*Route*",
          "ec2:*Gateway*",
          "ec2:*SecurityGroup*",
          "ec2:*NetworkAcl*",
          "ec2:*Address*",
          "ec2:Describe*",
          "ec2:CreateTags",
          "ec2:DeleteTags"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to VPC tags or specific VPC ARNs
      },
      
      # DNS & Certificates (Phase 2)
      {
        Sid    = "Route53Management"
        Effect = "Allow"
        Action = [
          "route53:ChangeResourceRecordSets",
          "route53:GetChange",
          "route53:GetHostedZone",
          "route53:ListHostedZones",
          "route53:ListResourceRecordSets",
          "route53:ListTagsForResource"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to specific hosted zone ARN
      },
      {
        Sid    = "CertificateManagement"
        Effect = "Allow"
        Action = [
          "acm:RequestCertificate",
          "acm:DescribeCertificate",
          "acm:ListCertificates",
          "acm:DeleteCertificate",
          "acm:AddTagsToCertificate",
          "acm:ListTagsForCertificate"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to certificates with Project=conflicto tag
      },
      
      # Database (Phase 3)
      {
        Sid    = "RDSManagement"
        Effect = "Allow"
        Action = [
          "rds:*"
        ]
        Resource = "*"
        # TODO Phase 10: Replace with granular actions and DB instance ARN pattern
      },
      {
        Sid    = "SecretsManagement"
        Effect = "Allow"
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:TagResource"
        ]
        Resource = "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:conflicto-*"
      },
      
      # Compute (Phases 4-5)
      {
        Sid    = "ECSManagement"
        Effect = "Allow"
        Action = [
          "ecs:*Cluster*",
          "ecs:*Service*",
          "ecs:*TaskDefinition*",
          "ecs:*Task",
          "ecs:Describe*",
          "ecs:List*",
          "ecs:TagResource",
          "ecs:UntagResource"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* cluster and service ARN patterns
      },
      {
        Sid    = "ECRManagement"
        Effect = "Allow"
        Action = [
          "ecr:*"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* repository ARN pattern
      },
      {
        Sid    = "LoadBalancerManagement"
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:*"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* load balancer and target group ARN patterns
      },
      
      # Observability
      {
        Sid    = "CloudWatchManagement"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:DeleteLogGroup",
          "logs:TagLogGroup",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:DeleteAlarms",
          "cloudwatch:DescribeAlarms"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to /aws/ecs/conflicto-* log group pattern
      },
      {
        Sid    = "SNSManagement"
        Effect = "Allow"
        Action = [
          "sns:CreateTopic",
          "sns:DeleteTopic",
          "sns:Subscribe",
          "sns:Unsubscribe",
          "sns:SetTopicAttributes",
          "sns:GetTopicAttributes",
          "sns:ListTopics",
          "sns:TagResource"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* topic ARN pattern
      },
      
      # IAM (Limited PassRole only)
      {
        Sid    = "ECSTaskRolePassRole"
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/conflicto-*-ecs-exec",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/conflicto-*-ecs-task"
        ]
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}
```

**Key Policy Features:**
- All wildcards marked with Phase 10 TODOs
- SecretsManager scoped to `conflicto-*` prefix
- PassRole limited to ECS roles with service condition
- State bucket explicitly referenced by account ID

### Step 6: Define Outputs

**File:** `infrastructure/iam/outputs.tf`

```hcl
output "oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider"
  value       = aws_iam_openid_connect_provider.github_actions.arn
}

output "deployer_role_arns" {
  description = "Map of environment to deployer role ARN"
  value = {
    for env in var.environments :
    env => aws_iam_role.terraform_deployer[env].arn
  }
}

output "deployer_role_arn_dev" {
  description = "ARN of dev deployer role (for easy reference)"
  value       = aws_iam_role.terraform_deployer["dev"].arn
}

output "deployer_role_arn_staging" {
  description = "ARN of staging deployer role (for easy reference)"
  value       = aws_iam_role.terraform_deployer["staging"].arn
}

output "deployer_role_arn_prod" {
  description = "ARN of prod deployer role (for easy reference)"
  value       = aws_iam_role.terraform_deployer["prod"].arn
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "github_repository" {
  description = "GitHub repository with access"
  value       = var.github_repository
}
```

**Usage:** Outputs support both map iteration and direct individual access

### Step 7: Create Documentation

**File:** `infrastructure/iam/README.md`

```markdown
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
```

**File:** Update `infrastructure/README.md` (add section)

```markdown
## CI/CD Authentication

GitHub Actions workflows authenticate using IAM roles via OIDC.

**Stack:** `infrastructure/iam/`

**Roles:**
- `conflicto-terraform-deployer-dev`
- `conflicto-terraform-deployer-staging`
- `conflicto-terraform-deployer-prod`

**Trust:** Restricted to repository `tristanl-slalom/conflicto`

See `infrastructure/iam/README.md` for details.
```

### Step 8: Update Project Documentation

**File:** `.copilot/iac.md` (add Phase 0.5 section)

```markdown
## Phase 0.5: IAM OIDC Provider & Terraform Deployer Roles

**Status:** ✅ Complete
**Issue:** #64
**Stack:** `infrastructure/iam/`

### Resources Created

- AWS IAM OIDC provider for GitHub Actions
- Three IAM roles: `conflicto-terraform-deployer-{dev,staging,prod}`
- Repository-restricted trust policies
- Permissions covering phases 0-5 infrastructure

### Usage

Role ARNs consumed by GitHub Actions workflows in #57.

```bash
cd infrastructure/iam
terraform output deployer_role_arns
```

### Next Steps

- Integrate role ARNs into CI/CD workflows (#57)
- Schedule Phase 10 hardening (wildcard removal, tag conditions)
```

## Testing Strategy

### Unit Tests (Manual Verification)

1. **Terraform Validation**
   ```bash
   cd infrastructure/iam
   terraform init
   terraform validate
   terraform fmt -check
   ```

2. **Plan Review**
   ```bash
   terraform plan
   # Verify 4 resources to create (1 provider + 3 roles + 3 policies)
   ```

3. **Apply and Output Verification**
   ```bash
   terraform apply
   terraform output
   # Confirm 3 role ARNs displayed
   ```

### Integration Tests

1. **Role Assumption Simulation**
   ```bash
   # Create test GitHub Actions workflow that assumes role
   # Workflow should successfully authenticate and run `aws sts get-caller-identity`
   ```

2. **Permission Validation**
   ```bash
   # Test S3 state access
   aws s3 ls s3://conflicto-terraform-state-ACCOUNT_ID/ --role-arn ROLE_ARN
   
   # Test DynamoDB lock access
   aws dynamodb describe-table --table-name conflicto-terraform-locks --role-arn ROLE_ARN
   ```

3. **Trust Policy Enforcement**
   ```bash
   # Attempt role assumption from different repository (should fail)
   # Attempt role assumption with wrong audience (should fail)
   ```

### Acceptance Criteria Validation

- [ ] Run `terraform apply` successfully
- [ ] Verify 4 resources created (1 OIDC provider + 3 roles)
- [ ] Confirm outputs display all role ARNs
- [ ] Check trust policies restrict to correct repository
- [ ] Review inline policies for Phase 0-5 permissions
- [ ] Validate all wildcards have TODO comments
- [ ] Test sample role assumption (documented command)

## Deployment Considerations

### Prerequisites

- Remote state S3 bucket exists (`conflicto-terraform-state-ACCOUNT_ID`)
- DynamoDB lock table exists (`conflicto-terraform-locks`)
- Current AWS user has IAM permissions to create OIDC providers and roles

### Deployment Order

1. Deploy this stack first (provides authentication)
2. Configure GitHub repository secrets/variables with role ARNs
3. Implement #57 workflows consuming these roles

### Rollback Strategy

```bash
# Destroy all resources
cd infrastructure/iam
terraform destroy

# State remains in S3 for recovery
```

**Risk:** Deleting OIDC provider breaks all CI/CD workflows. Coordinate with team before destruction.

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Overly broad initial permissions | Medium | Mark TODOs; schedule Phase 10 hardening |
| OIDC thumbprint rotation | Low | Document update procedure in README |
| Role ARN drift | Low | Single source of truth via Terraform outputs |
| Unauthorized access | High | Trust policy enforces repository restriction |
| Accidental role deletion | High | State file backup; require approval for destroy |

## Estimated Effort

- **Implementation:** 2-3 hours
  - Terraform configuration: 1 hour
  - Documentation: 1 hour
  - Testing: 1 hour
- **Review:** 30 minutes
- **Deployment:** 15 minutes
- **Total:** ~3-4 hours

## Dependencies

- **Blocked By:** #47 (Remote State Backend) - must exist before deployment
- **Blocks:** #57 (CI/CD Workflow) - provides required role ARNs
- **Related:** Phase 10 (Security Hardening) - future permission refinement

## Success Criteria

1. ✅ Terraform apply completes without errors
2. ✅ Three role ARNs output correctly
3. ✅ Sample role assumption documented and tested
4. ✅ Trust policies enforce repository restriction
5. ✅ Permissions include all services from phases 0-5
6. ✅ All wildcards justified with TODO comments
7. ✅ Documentation complete and accurate
8. ✅ Ready for #57 workflow integration
