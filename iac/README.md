# Infrastructure as Code (IaC) – AWS Account & Credential Bootstrap

This document captures the **manual steps** you must perform in the AWS Console before Terraform code for this project can safely and predictably target the correct AWS environment. These actions cannot (and should not) be automated via IaC because they establish the trust and security foundation on which Terraform will operate.

> If you already completed parts of this (e.g. created a user and attached `PowerUserAccess`), skim the checklist sections to see what to refine before committing to Terraform workflows.

---

## 1. Identify / Confirm the Target AWS Environment

| Item | Decision / Value | Notes |
|------|------------------|-------|
| AWS Account ID | (record) | Visible in the console (top-right). |
| Account Alias | (record) | Helpful for clarity in CLI prompts. |
| Primary Region | (decide) | e.g. `us-east-1` or `us-west-2`; choose one primary deployment region. |
| Additional Regions? | (list) | Only enable if required; reduces attack surface & costs. |
| Environment Strategy | Single account with multiple workspaces OR multi-account | Multi-account (e.g. landing zone) is preferable long term. |

Make these explicit now—Terraform code will encode or assume them (e.g. provider `region`, tagging, naming conventions).

---

## 2. Enable / Access IAM Identity Center (AWS SSO) (If Not Already Done)

1. Log in with an Organization management account or an account admin having rights to manage IAM Identity Center.
2. Navigate: AWS Console → IAM Identity Center.
3. If not enabled, click **Enable IAM Identity Center**.
4. Note the **SSO Start URL** (will look like `https://d-XXXXXXXXXX.awsapps.com/start`).
5. Decide whether to authenticate locally via SSO (preferred) vs long‑lived access keys on an IAM user (legacy / fallback only).

> Best Practice: Use SSO + permission sets + roles instead of IAM users with static keys. The initial quick path (“create user + PowerUserAccess”) should later be replaced by a least‑privilege Terraform deploy role.

---

## 3. (Current State) Manual User Creation (What You Did)

You mentioned you:

1. Logged into the AWS account with sufficient privileges.
2. Created an IAM user for this application (likely via IAM Console → Users → Create user).
3. Attached the AWS managed policy `PowerUserAccess`.

### Short-Term Acceptability

This works for bootstrapping, but is broader than necessary. Move toward a **role-based** approach soon (see Section 10).

### If You Need Access Keys (Temporary Only)

1. Select the user → **Security credentials** tab.
2. Create an access key (choose “Command Line Interface”).
3. Store the secret access key in a secure secret manager (NOT in `.env`, NOT in repo, NOT pasted into tickets).
4. Configure locally (see Section 6) then remove/rotate once SSO & role assumption are in place.

---

## 4. (Preferred) Create a Terraform Deployment Role via SSO

Do this once you have the basics working:

1. In IAM Identity Center, create a **Permission Set** named `TerraformPowerUserTemp` (start with AWS managed `PowerUserAccess`).
2. Assign it to your user for the target account.
3. After bootstrap, replace with a least‑privilege custom permission set (policy examples below).

> If you cannot yet create permission sets, proceed with the user method, but plan to migrate.

---

## 5. Decide Naming & Tagging Conventions (Before Writing Terraform)

| Concern | Example Decision |
|---------|------------------|
| Global project prefix | `conflicto` |
| Environment suffix | `dev`, `stg`, `prod` |
| Resource name pattern | `<prefix>-<env>-<component>` (e.g. `conflicto-dev-vpc`) |
| Mandatory tags | `Project=conflicto`, `Env=dev`, `Owner=<team>`, `CostCenter=<id>` |
| Optional governance tags | `DataClass=Internal`, `Backup=Daily` |

Document these and use Terraform locals or modules to enforce them.

---

## 6. Configure AWS CLI Authentication Locally

### Configure SSO

```bash
aws configure sso
# Provide:
#  - SSO start URL: <your SSO start URL>
#  - SSO region: <e.g. us-east-1>
#  - Account: <target account id>
#  - Role/Permission Set: TerraformPowerUserTemp (or similar)
#  - Profile Name: genai-immersion-houston
```

Validate:

```bash
aws sts get-caller-identity --profile {sso-profile-name}
```

Expect a response in the following format: 

```json
{
    "UserId": "AR...:{login-id}",
    "Account": "418xxxxxxxx3",
    "Arn": "arn:aws:sts::418xxxxxxxx3:assumed-role/AWSReservedSSO_PowerUserAccess_b8365xxxxxxxxxx6/{login-id}"
}
```

---

## 7. Core Bootstrap Resources for Terraform State

Terraform needs a durable backend before you scale modules.

| Resource | Purpose | Notes |
|----------|---------|-------|
| S3 Bucket | Remote state storage | Enable versioning, encryption (SSE-S3 or SSE-KMS), block public access. |
| DynamoDB Table | State locking | Table with primary key `LockID` (string). |
| KMS Key (optional) | Encrypt state | If compliance requires customer managed key. |

### Suggested Naming

* Bucket: `conflicto-tfstate` (append `-dev` if multi-account not in place yet). Avoid region-specific suffix unless multi-region planned.
* DynamoDB table: `conflicto-terraform-locks`.

> Strategy: Bootstrap these either manually once OR via an initial local backend run of a `bootstrap` Terraform stack, then migrate to remote backend.

---

## 8. Pre-Terraform Decision Checklist

| Category | Decide / Record | Why It Matters |
|----------|-----------------|----------------|
| Accounts model | Single vs multi-account | Affects provider aliasing & isolation. |
| Primary region | (e.g. `us-east-1`) | Provider default & latency. |
| State bucket name | (record) | Hard-coded in backend blocks. |
| Lock table name | (record) | Same as above. |
| Tag schema | (finalize) | Consistency enforcement. |
| CIDR ranges | e.g. `10.20.0.0/16` | VPC module design. |
| Number of AZs | 2 or 3 | Subnet count & HA. |
| Public vs private subnets | (plan) | Security posture. |
| Secrets strategy | SSM Parameter Store vs Secrets Manager | Module selection + costs. |
| KMS strategy | Reuse or per-service keys | Encryption planning. |
| Logging | CloudTrail + Config + central S3? | Compliance & traceability. |
| Deployment pipeline | GitHub Actions OIDC vs static creds | Security & automation. |
| Budget & alarms | Budgets service activated? | Cost control early. |

Complete this table before writing large modules—refactors later are expensive.

---

## 9. Minimum Viable Terraform Folder Structure (Planned)

Example (not yet created):

```text
iac/
  bootstrap/          # Creates state bucket, lock table (first apply uses local backend)
  global/             # Org/global services (e.g., logging, guardrails) (optional early)
  envs/
    dev/
      main.tf
      variables.tf
      outputs.tf
    prod/
      ...
  modules/
    network/
    compute/
    observability/
```

> Keep `bootstrap` isolated so you can safely reconfigure the backend after initial creation.

---

## 10. Evolving Toward Least Privilege

### Transitional Policy (PowerUserAccess)

Good for momentum, but broad: includes almost all AWS actions except certain IAM & org-level.

### Hardened Approach

Create a custom policy for Terraform such as:

* Full access to: S3 (limited to state bucket), DynamoDB (lock table), CloudWatch Logs, VPC, EC2 networking, IAM role creation limited by path (e.g. `/conflicto/`), ECR (if containers), Lambda (if serverless), RDS or Aurora (if needed), Secrets Manager/SSM Get/Put restricted by naming convention.
* Deny actions outside approved resource ARNs.

Sample (illustrative fragment – refine before use):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": "arn:aws:s3:::conflicto-tfstate"},
    {"Effect": "Allow", "Action": ["s3:GetObject","s3:PutObject","s3:DeleteObject"], "Resource": "arn:aws:s3:::conflicto-tfstate/*"},
    {"Effect": "Allow", "Action": ["dynamodb:PutItem","dynamodb:GetItem","dynamodb:DeleteItem","dynamodb:DescribeTable"], "Resource": "arn:aws:dynamodb:*:*:table/conflicto-terraform-locks"}
  ]
}
```

You would expand service-by-service with least privilege ARNs as architecture solidifies.

---

## 11. Verifying You Are Targeting the Right Account & Region

Run after each new shell session (especially if you work across multiple clients):

```bash
aws sts get-caller-identity --profile genai-immersion-houston
aws configure list --profile genai-immersion-houston | grep region
```

Optional guard: Put this snippet in your shell profile to display the active AWS account when entering the repo directory.

---

## 12. Security Hygiene Reminders

* Avoid long-lived access keys; prefer SSO & role assumption.
* Enable MFA for the human identities.
* Enforce bucket encryption & versioning (state is sensitive metadata).
* Do not store secrets in Terraform variables; leverage SSM/Secrets Manager.
* Rotate any temporary access keys used during bootstrap once roles are ready.

---

## 13. Bootstrap Execution Plan (High-Level)

1. Confirm decisions in Sections 1, 5, 8.
2. Configure SSO profile locally (`genai-immersion-houston`).
3. Create `bootstrap` Terraform stack using **local** backend to provision:
   * S3 state bucket
   * DynamoDB lock table
   * (Optional) KMS CMK for state encryption
4. Update backend configuration in `bootstrap` to use remote state; run `terraform init -reconfigure`.
5. Create `envs/dev` stack referencing remote backend.
6. Introduce network, compute, and persistence modules incrementally.
7. Replace PowerUser permission set with least‑privilege custom set.

---

## 14. Quick Progress Checklist

| Step | Status (✔/✖) |
|------|--------------|
| Account ID recorded |  |
| Primary region chosen |  |
| SSO enabled |  |
| SSO profile configured locally |  |
| Naming + tagging conventions finalized |  |
| State bucket name decided |  |
| Lock table name decided |  |
| VPC CIDR & subnet plan drafted |  |
| Secrets strategy decided |  |
| Logging/audit plan (CloudTrail/Config) |  |
| Terraform folder scaffold created |  |
| Bootstrap applied (state + lock) |  |
| Least privilege policy drafted |  |
| CI/CD OIDC role planned |  |

---

## 15. Next Immediate Actions

1. Fill in any blanks in the decision tables above.
2. Create a `bootstrap` directory with initial Terraform files.
3. Use your `genai-immersion-houston` profile to run `terraform init` / `apply` locally for bootstrap.
4. Transition Terraform backend to the new S3 bucket + DynamoDB lock.
5. Draft custom least‑privilege policy requirements.

Once complete, you can proceed to author the core infrastructure modules confidently.

---

### Questions / Future Enhancements

* Multi-account landing zone (Control Tower) adoption timeline?
* Centralized logging & security services (e.g., GuardDuty, Security Hub) integration.
* Cost controls (AWS Budgets, cost anomaly detection) early integration.
* GitHub Actions OIDC role & trust policy for CI/CD.

Document updates here as architecture decisions evolve.

---
Last updated: 2025-10-07
