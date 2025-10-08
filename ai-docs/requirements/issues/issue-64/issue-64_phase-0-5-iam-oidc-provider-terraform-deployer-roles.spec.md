# Technical Specification: Phase 0.5 - IAM OIDC Provider & Terraform Deployer Roles

**GitHub Issue:** [#64](https://github.com/tristanl-slalom/conflicto/issues/64)
**Generated:** 2025-10-08
**Labels:** infrastructure, iac-bootstraping, terraform, security, iam, phase-0-5

## Problem Statement

The CI/CD Terraform workflow (Phase 9, #57) requires environment-scoped IAM roles assumable via GitHub OIDC. Currently, no infrastructure provisions the OIDC identity provider or the deployer roles, creating a gap that would cause automated deployments to fail.

This issue establishes the authentication foundation for GitHub Actions to deploy infrastructure changes without long-lived AWS credentials.

## Technical Requirements

### 1. OIDC Identity Provider
- Single AWS IAM OIDC provider for GitHub Actions
- Provider URL: `token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`
- Thumbprint: GitHub's current certificate thumbprint
- Shared across all environments (single provider)

### 2. IAM Roles Architecture
- **Role Naming Convention:** `conflicto-terraform-deployer-{env}`
- **Environments:** `dev`, `staging`, `prod`
- **Trust Policy:** Web identity federation restricted to this repository
- **Policy Attachment:** Inline policies with service permissions for phases 0-5

### 3. Repository Trust Restriction
Trust policies must enforce:
- Repository scope: `repo:tristanl-slalom/conflicto:*`
- Audience verification: `sts.amazonaws.com`
- Principal: OIDC provider ARN

### 4. Permission Scope (Phases 0-5)
Roles require access to:

**State Management:**
- S3: GetObject, PutObject, ListBucket, DeleteObject (state bucket)
- DynamoDB: GetItem, PutItem, DeleteItem, DescribeTable (lock table)

**Networking (Phase 1):**
- EC2: VPC, Subnet, RouteTable, InternetGateway, NatGateway operations
- EC2: SecurityGroup create/modify/delete operations
- EC2: Describe* (read-only discovery)

**DNS & Certificates (Phase 2):**
- Route53: ChangeResourceRecordSets, List*, Get*
- ACM: RequestCertificate, DescribeCertificate, ListCertificates, DeleteCertificate

**Database (Phase 3):**
- RDS: Full access (narrow in Phase 10 hardening)
- Secrets Manager: Create/Update/Delete secrets (prefix `conflicto-*`)

**Compute & Load Balancing (Phase 4-5):**
- ECS: Cluster, Service, TaskDefinition operations
- ECR: Repository management, image push/pull
- ELB: Application Load Balancer create/modify/delete
- Target Groups: Create/modify/delete/register operations

**Observability:**
- CloudWatch: Log groups, alarms, metrics
- SNS: Topic create/modify/delete (for alarms)

**IAM (Limited):**
- PassRole: Restricted to ECS task execution role ARNs only
- Condition: `iam:PassedToService` must be `ecs-tasks.amazonaws.com`

## Data Models

### Trust Policy Schema
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GitHubActionsOIDC",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${account_id}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:tristanl-slalom/conflicto:*"
        }
      }
    }
  ]
}
```

### Terraform Output Schema
```hcl
outputs = {
  oidc_provider_arn = "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
  deployer_role_arns = {
    dev     = "arn:aws:iam::ACCOUNT_ID:role/conflicto-terraform-deployer-dev"
    staging = "arn:aws:iam::ACCOUNT_ID:role/conflicto-terraform-deployer-staging"
    prod    = "arn:aws:iam::ACCOUNT_ID:role/conflicto-terraform-deployer-prod"
  }
}
```

## Integration Points

### GitHub Actions Workflow Integration (#57)
Workflows will use the `aws-actions/configure-aws-credentials` action:
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ vars.AWS_DEPLOYER_ROLE_ARN }}
    aws-region: us-east-1
    role-session-name: GitHubActions-${{ github.run_id }}
```

### Terraform Backend
- Uses same S3 backend as other infrastructure stacks
- State key: `iam/terraform.tfstate`
- Locks via DynamoDB table from Phase 0

### Infrastructure Stack Location
- **Path:** `infrastructure/iam/`
- **Isolation:** Separate from bootstrap to allow independent lifecycle
- **Backend:** S3 remote state (already provisioned in Phase 0)

## Acceptance Criteria

- [ ] `infrastructure/iam/` directory created with Terraform configuration
- [ ] OIDC provider resource defined (or documented skip if pre-existing)
- [ ] Three IAM roles created: `conflicto-terraform-deployer-{dev,staging,prod}`
- [ ] Trust policies restrict access to `repo:tristanl-slalom/conflicto:*`
- [ ] Inline policies grant required permissions for phases 0-5
- [ ] `terraform apply` successfully provisions all resources
- [ ] Outputs display all three role ARNs
- [ ] README documents CI/CD authentication flow
- [ ] Policy wildcards justified with TODO comments for Phase 10 hardening
- [ ] Sample `aws sts assume-role-with-web-identity` command documented

## Assumptions & Constraints

### Assumptions
1. AWS account does not have existing GitHub OIDC provider (will create)
2. Bootstrap S3 backend and DynamoDB lock table exist from Phase 0
3. Current AWS user has permissions to create IAM roles and OIDC providers
4. GitHub repository is `tristanl-slalom/conflicto`

### Constraints
1. **Least Privilege Iteration:** Initial permissions broader than final state, hardening in Phase 10
2. **No Permissions Boundary:** Deferred to future enhancement if needed
3. **Single OIDC Provider:** Shared across all environments for simplicity
4. **Repository Scope Only:** Cannot restrict to specific branches in trust policy (OIDC limitation)
5. **Manual Role ARN Configuration:** Workflow files (#57) must manually reference output ARNs

### Security Constraints
- No wildcard resource ARNs where practical
- PassRole limited to ECS execution roles with service condition
- Secrets Manager restricted by naming prefix
- All wildcards marked with TODO for hardening

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Overly broad initial permissions | Medium | High | Mark TODOs in policy; schedule hardening pass before prod go-live |
| OIDC condition misconfiguration | High | Low | Use canonical GitHub docs pattern; test with dry-run workflow |
| Role ARN drift between environments | Low | Low | Single Terraform root controlling all three roles |
| Unauthorized repository access | High | Low | Trust policy enforces repository restriction |
| State file contains sensitive ARNs | Low | Medium | S3 bucket already encrypted and access-controlled |

## Future Hardening Roadmap (Phase 10)

1. **Resource ARN Specificity**
   - Replace `rds:*` with specific database ARN patterns
   - Scope ECS/ECR to `conflicto-*` resource names
   - Replace EC2 wildcards with VPC-scoped conditions

2. **Permissions Boundary**
   - Add boundary restricting actions to resources tagged `Project=conflicto`
   - Prevent privilege escalation via tag enforcement

3. **Environment Differentiation**
   - Dev: Broader permissions for experimentation
   - Staging: Production-like with additional destroy capabilities
   - Prod: Minimal write access, read-heavy for verification

4. **Branch-Specific Policies** (if GitHub adds support)
   - Main branch: All environments
   - Feature branches: Dev only
   - Release branches: Staging + Prod

5. **Audit & Monitoring**
   - CloudTrail alerts on role assumption events
   - Session duration monitoring
   - Periodic policy review automation

## Dependencies

- **Depends On:** #47 (Phase 0 - Remote State Backend) - requires S3 bucket and DynamoDB table
- **Blocks:** #57 (Phase 9 - CI/CD Terraform Workflow) - provides role ARNs for automation

## Related Documentation

- [AWS GitHub OIDC Guide](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform aws_iam_openid_connect_provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_openid_connect_provider)
- [GitHub Actions AWS Credentials Action](https://github.com/aws-actions/configure-aws-credentials)
