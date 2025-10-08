# IAM OIDC Setup Guide - AWS Console Manual Creation

This guide provides step-by-step instructions for manually creating the GitHub Actions OIDC provider and Terraform deployer roles in the AWS Console. This is required because the current AWS user has PowerUserAccess permissions which do not include `iam:CreateOpenIDConnectProvider` or `iam:CreateRole`.

After manual creation, these resources will be imported into Terraform for ongoing management.

## Prerequisites

- AWS Console access with IAM permissions to create:
  - OIDC Identity Providers
  - IAM Roles
  - IAM Policies
- GitHub repository: `tristanl-slalom/conflicto`
- AWS Account ID: `418389084763`

## Part 1: Create GitHub OIDC Identity Provider

### Step 1: Navigate to IAM

1. Sign in to AWS Console
2. Navigate to **IAM** service (search for "IAM" in the top search bar)
3. In the left sidebar, click **Identity providers**

### Step 2: Add Identity Provider

1. Click **Add provider** button
2. Select **OpenID Connect** as provider type
3. Fill in the following details:

   **Provider URL:** `https://token.actions.githubusercontent.com`
   
   **Audience:** `sts.amazonaws.com`

4. Click **Get thumbprint** button
   - AWS will automatically fetch the certificate thumbprint
   - Expected thumbprint: `6938fd4d98bab03faadb97b34396831e3780aea1`
   - If different, use the auto-fetched value

5. Click **Add provider**

### Step 3: Add Tags (Optional)

After creation, add these tags:
- `Name` = `github-actions-oidc`
- `Project` = `conflicto`
- `ManagedBy` = `terraform`
- `Description` = `OIDC provider for GitHub Actions CI/CD`

### Step 4: Note the Provider ARN

Copy the provider ARN (will look like):
```
arn:aws:iam::418389084763:oidc-provider/token.actions.githubusercontent.com
```

You'll need this for the trust policies in Part 2.

## Part 2: Create Dev Deployer Role

### Step 1: Create Role

1. In IAM, navigate to **Roles** in the left sidebar
2. Click **Create role**
3. Select **Web identity** as the trusted entity type
4. Configure trust:
   - **Identity provider:** Select `token.actions.githubusercontent.com`
   - **Audience:** Select `sts.amazonaws.com`
   - Click **Next**

### Step 2: Skip Permission Policies (for now)

1. On the "Add permissions" page, click **Next** without selecting any policies
2. We'll add inline policies after role creation

### Step 3: Name and Create Role

1. **Role name:** `conflicto-terraform-deployer-dev`
2. **Description:** `GitHub Actions role for Terraform deployments to dev environment`
3. **Tags:**
   - `Name` = `conflicto-terraform-deployer-dev`
   - `Environment` = `dev`
   - `Project` = `conflicto`
   - `ManagedBy` = `terraform`
   - `Purpose` = `ci-cd-terraform-deployment`
4. Click **Create role**

### Step 4: Edit Trust Policy

1. After creation, click on the newly created role
2. Navigate to **Trust relationships** tab
3. Click **Edit trust policy**
4. Replace the trust policy with:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GitHubActionsOIDC",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::418389084763:oidc-provider/token.actions.githubusercontent.com"
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

5. Click **Update policy**

### Step 5: Add Inline Permission Policy

1. Navigate to **Permissions** tab
2. Click **Add permissions** → **Create inline policy**
3. Click **JSON** tab
4. Paste the complete permission policy (see expandable section below)
5. Click **Next**
6. **Policy name:** `conflicto-terraform-deployer-dev-policy`
7. Click **Create policy**

<details>
<summary>Click to expand: Complete Permission Policy JSON</summary>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformStateAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::conflicto-tfstate",
        "arn:aws:s3:::conflicto-tfstate/*"
      ]
    },
    {
      "Sid": "TerraformLockAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:DescribeTable"
      ],
      "Resource": "arn:aws:dynamodb:*:418389084763:table/conflicto-terraform-locks"
    },
    {
      "Sid": "NetworkingManagement",
      "Effect": "Allow",
      "Action": [
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
      ],
      "Resource": "*"
    },
    {
      "Sid": "Route53Management",
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets",
        "route53:GetChange",
        "route53:GetHostedZone",
        "route53:ListHostedZones",
        "route53:ListResourceRecordSets",
        "route53:ListTagsForResource"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CertificateManagement",
      "Effect": "Allow",
      "Action": [
        "acm:RequestCertificate",
        "acm:DescribeCertificate",
        "acm:ListCertificates",
        "acm:DeleteCertificate",
        "acm:AddTagsToCertificate",
        "acm:ListTagsForCertificate"
      ],
      "Resource": "*"
    },
    {
      "Sid": "RDSManagement",
      "Effect": "Allow",
      "Action": [
        "rds:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManagement",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:UpdateSecret",
        "secretsmanager:DeleteSecret",
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:TagResource"
      ],
      "Resource": "arn:aws:secretsmanager:*:418389084763:secret:conflicto-*"
    },
    {
      "Sid": "ECSManagement",
      "Effect": "Allow",
      "Action": [
        "ecs:*Cluster*",
        "ecs:*Service*",
        "ecs:*TaskDefinition*",
        "ecs:*Task",
        "ecs:Describe*",
        "ecs:List*",
        "ecs:TagResource",
        "ecs:UntagResource"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECRManagement",
      "Effect": "Allow",
      "Action": [
        "ecr:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "LoadBalancerManagement",
      "Effect": "Allow",
      "Action": [
        "elasticloadbalancing:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchManagement",
      "Effect": "Allow",
      "Action": [
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
      ],
      "Resource": "*"
    },
    {
      "Sid": "SNSManagement",
      "Effect": "Allow",
      "Action": [
        "sns:CreateTopic",
        "sns:DeleteTopic",
        "sns:Subscribe",
        "sns:Unsubscribe",
        "sns:SetTopicAttributes",
        "sns:GetTopicAttributes",
        "sns:ListTopics",
        "sns:TagResource"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECSTaskRolePassRole",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": [
        "arn:aws:iam::418389084763:role/conflicto-*-ecs-exec",
        "arn:aws:iam::418389084763:role/conflicto-*-ecs-task"
      ],
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "ecs-tasks.amazonaws.com"
        }
      }
    }
  ]
}
```

</details>

### Step 6: Note the Role ARN

Copy the role ARN:
```
arn:aws:iam::418389084763:role/conflicto-terraform-deployer-dev
```

## Part 3: Create Staging Deployer Role

Repeat Part 2 with these changes:

1. **Role name:** `conflicto-terraform-deployer-staging`
2. **Description:** `GitHub Actions role for Terraform deployments to staging environment`
3. **Tags:** Change `Environment` to `staging`
4. Use the same trust policy (repository restriction applies)
5. **Inline policy name:** `conflicto-terraform-deployer-staging-policy`
6. Use the same permission policy JSON

Note the staging role ARN:
```
arn:aws:iam::418389084763:role/conflicto-terraform-deployer-staging
```

## Part 4: Create Prod Deployer Role

Repeat Part 2 with these changes:

1. **Role name:** `conflicto-terraform-deployer-prod`
2. **Description:** `GitHub Actions role for Terraform deployments to prod environment`
3. **Tags:** Change `Environment` to `prod`
4. Use the same trust policy (repository restriction applies)
5. **Inline policy name:** `conflicto-terraform-deployer-prod-policy`
6. Use the same permission policy JSON

Note the prod role ARN:
```
arn:aws:iam::418389084763:role/conflicto-terraform-deployer-prod
```

## Part 5: Verification Checklist

After creating all resources, verify:

- [ ] OIDC provider exists with correct URL and audience
- [ ] OIDC provider has correct thumbprint
- [ ] Three roles created: dev, staging, prod
- [ ] Each role has trust policy restricting to `tristanl-slalom/conflicto`
- [ ] Each role has inline permission policy attached
- [ ] All role ARNs noted for next steps

## Part 6: Terraform Import

Now import these manually created resources into Terraform:

```bash
cd infrastructure/iam
terraform init

# Import OIDC provider
terraform import aws_iam_openid_connect_provider.github_actions \
  arn:aws:iam::418389084763:oidc-provider/token.actions.githubusercontent.com

# Import roles
terraform import 'aws_iam_role.terraform_deployer["dev"]' conflicto-terraform-deployer-dev
terraform import 'aws_iam_role.terraform_deployer["staging"]' conflicto-terraform-deployer-staging
terraform import 'aws_iam_role.terraform_deployer["prod"]' conflicto-terraform-deployer-prod

# Import inline policies
terraform import 'aws_iam_role_policy.terraform_deployer_policy["dev"]' \
  conflicto-terraform-deployer-dev:conflicto-terraform-deployer-dev-policy
terraform import 'aws_iam_role_policy.terraform_deployer_policy["staging"]' \
  conflicto-terraform-deployer-staging:conflicto-terraform-deployer-staging-policy
terraform import 'aws_iam_role_policy.terraform_deployer_policy["prod"]' \
  conflicto-terraform-deployer-prod:conflicto-terraform-deployer-prod-policy

# Verify import (should show no changes)
terraform plan
```

If `terraform plan` shows changes, review and apply to align console resources with Terraform configuration.

## Part 7: Optional - Test Role Assumption

You can test role assumption using GitHub Actions:

1. Create a test workflow in `.github/workflows/test-oidc.yml`:

```yaml
name: Test OIDC Authentication

on:
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::418389084763:role/conflicto-terraform-deployer-dev
          aws-region: us-east-1
      
      - name: Verify Identity
        run: |
          aws sts get-caller-identity
          echo "Successfully authenticated as GitHub Actions!"
```

2. Run the workflow manually from Actions tab
3. Verify successful authentication
4. Delete the test workflow file

## Troubleshooting

### "No OpenIDConnect provider found"

- Verify OIDC provider URL is exactly: `https://token.actions.githubusercontent.com`
- Check that audience is `sts.amazonaws.com`

### "Not authorized to perform sts:AssumeRoleWithWebIdentity"

- Verify trust policy `sub` condition: `repo:tristanl-slalom/conflicto:*`
- Check that GitHub Actions workflow has `id-token: write` permission

### "Access Denied" errors during Terraform operations

- Verify inline policy is attached to the role
- Check policy JSON for syntax errors
- Ensure resource ARNs use correct account ID (418389084763)

## Next Steps

After successful manual creation and import:

1. Run `terraform plan` to verify no drift
2. Update GitHub repository variables with role ARNs
3. Implement CI/CD workflows in Issue #57
4. Schedule Phase 10 security hardening
