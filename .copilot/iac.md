---
feature_tag: iac-bootstraping
---

# Caja Infrastructure as Code Plan (Terraform)

Last updated: 2025-10-07 (amended: added bootstrap & domain strategy, caja subdomain naming, incremental execution phases)

This document defines the execution‑ready plan for provisioning Caja platform infrastructure on AWS using Terraform. After approval, modules and environment compositions will be scaffolded exactly as described.

---

## 0. Core Principles & Conventions

**Region:** `us-east-1` (override via variable)

**Environments:** `dev`, `staging`, `prod` (optional `sandbox`)

**State:** Remote S3 backend + DynamoDB locking (separate key per env)

**Naming Convention:** `caja-{env}-{component}` (shorten if AWS limits)

**Global Tag Set:**

- Project = caja
- Environment = {env}
- ManagedBy = terraform
- Owner = platform-engineering
- Confidentiality = internal
- CostCenter = events-eng

**Terraform Version:** >= 1.7 (AWS provider `~> 5.0`)

**Module Philosophy:** Thin root; composable, opinionated internal modules.

**Feature Tag:** #IaC-Bootstrap

---

## 1. Repository & Directory Layout

```text
infrastructure/
  README.md
  (planned) bootstrap/                 # Phase 0: ONLY foundational resources (S3 state, DynamoDB lock, hosted zone)
  modules/                             # Created incrementally (see phase plan)
    domain/                            # Domain + certs (no alias A records until infra exists)
    networking/
    security/
    ecr/
    ecs-cluster/
    ecs-service/
    alb/
    rds-postgres/
    s3-static-site/
    cloudfront/
    route53/ (may be superseded by domain module)
    secrets/
    observability/
    # (future) redis/
  environments/
    dev/                               # Each env root after bootstrap done
    staging/
    prod/
  shared/
    versions.tf (provider + terraform version pinning)
    tags.tf
    locals.common.tf
    variables.common.tf
.github/
  workflows/
    infra-plan-apply.yml               # CI plan/apply (added after initial manual local applies)
```

Each `environments/{env}` directory is its own Terraform root. Remote state object: `env/{env}/terraform.tfstate`.

Example `backend.hcl`:

```hcl
bucket         = "caja-terraform-state"
key            = "env/dev/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "caja-terraform-locks"
encrypt        = true
```

---

## 2. Updated Domain & DNS Strategy (caja Subnamespace)

Base root domain (external registrar: Hover): `dbash.dev`.

Application namespace: `caja` (no separate hosted zone initially; single Route 53 public hosted zone for the root domain).

Primary production hostnames:

- Frontend: `app.caja.dbash.dev`
- API: `api.caja.dbash.dev`

Optional environment hostnames (enabled by `enable_env_subdomains = true`):

- Dev: `app.dev.caja.dbash.dev`, `api.dev.caja.dbash.dev`
- Staging: `app.staging.caja.dbash.dev`, `api.staging.caja.dbash.dev`

Certificates (ACM, region `us-east-1`):

- Frontend cert: SAN list includes all app.* variants
- API cert: SAN list includes all api.* variants

Only MANUAL action: update Hover nameservers to the Route 53 NS values emitted by the bootstrap stack. Everything else is IaC.

Delegation / multi-account future: optionally introduce a delegated hosted zone `caja.dbash.dev` later; not required for MVP.

## 3. Execution Phases (Incremental Plan)

| Phase | Scope | Artifacts Created | Manual Step | Exit Criteria |
|-------|-------|-------------------|-------------|---------------|
| 0 | Bootstrap foundations | S3 state bucket, DynamoDB lock table, Route 53 hosted zone | Hover NS update | `dig NS dbash.dev` shows AWS NS |
| 0.5 | IAM OIDC & deployer roles | GitHub OIDC provider, IAM roles & policies (`caja-terraform-deployer-*`) | None | OIDC `sts:GetCallerIdentity` succeeds in dry-run plan job |
| 1 | Domain & certificates | `modules/domain` ACM certs + DNS validation records (no alias A records yet) | None | Both certs status = Issued |
| 2 | Core network & security | VPC, subnets, NAT, security groups | None | `terraform plan` clean; VPC reachable |
| 3 | Persistence | RDS Postgres + secret (no app yet) | None | DB available; secret populated |
| 4 | Container platform | ECS cluster + ECR repo | None | Cluster empty but healthy |
| 5 | Runtime service + ALB | Task def, ECS service, ALB (HTTPS w/ API cert) | None | Health check 200 at ALB DNS |
| 6 | Static hosting + CDN | S3 static site bucket, CloudFront (frontend cert) | None | CF distribution deployed |
| 7 | DNS application records | Alias A/AAAA for app/api (and env) | None | `curl https://api.caja.../health` OK |
| 8 | Observability | Log retention, alarms, SNS | Optional email confirm | Alarms in OK state |
| 9 | CI/CD pipeline | GitHub Actions workflow, OIDC role docs | None | PR shows plan comment |
| 10 | Hardening | Autoscaling, scaling policies, cost tags | None | Policies active |

Deferrable (later): Redis, WAF, Blue/Green, multi-region, analytics dashboards.

Rollback posture: Each phase idempotent; avoid mixing phases in a single PR.

## 4. Bootstrap Stack (Design Only)

Purpose: Establish remote state + authoritative zone before any other Terraform depends on them.

Resources:

- S3 bucket `caja-terraform-state` (versioned, SSE-S3)
- DynamoDB table `caja-terraform-locks`
- Route 53 hosted zone for `dbash.dev`

Outputs consumed by later env roots:

- `state_bucket_name`
- `dynamodb_lock_table`
- `hosted_zone_id`
- `name_servers` (to copy into Hover)

Manual Step (only one in the entire lifecycle): Update Hover nameservers -> wait for propagation.

Validation checklist:

1. `dig NS dbash.dev` returns the same four NS values as Route 53
2. No extraneous records lost (add any MX/TXT before NS cutover if needed)

## 5. Domain Module Contract (Planned)

Inputs:

- `root_domain` (e.g. `dbash.dev`)
- `zone_id` (from bootstrap)
- `enable_env_subdomains` (bool; default true)
- `environments` (list, default `["dev", "staging"]`)

Behavior:

- Create two ACM certificates (frontend + api) w/ SAN expansion
- Create DNS validation records per domain validation option
- Wait for issuance (`aws_acm_certificate_validation`)
- Output certificate ARNs + ordered domain lists (`app_domains`, `api_domains`)

Non-goals (kept out for separation of concerns):

- Creating alias A records (depends on ALB / CloudFront existence)
- Creating Route 53 hosted zone (bootstrap owns it)

Outputs:

- `frontend_certificate_arn`
- `api_certificate_arn`
- `app_domains` (index 0 = prod primary)
- `api_domains` (index 0 = prod primary)

## 6. DNS Alias Record Strategy

Alias records are created only after infrastructure targets exist:

- `app.caja.dbash.dev` → CloudFront distribution (domain + hosted zone id)
- `api.caja.dbash.dev` → ALB
- Optional env records iterate over remaining domain lists.

Rationale: Avoid circular/fragile dependencies; permit independent re-deploy of networking before certificate issues.

## 7. Updated Module Specifications (Contracts)

### networking

...existing definition (unchanged)...

### security

...existing definition (unchanged)...

### ecr

...existing definition (unchanged)...

### ecs-cluster

...existing definition (unchanged)...

### ecs-service

...existing definition (unchanged)...

### alb

Adjustment: ALB HTTPS listener uses `api_certificate_arn` output from domain module.

### rds-postgres

...existing definition (unchanged)...

### secrets

...existing definition (unchanged)...

### s3-static-site

...existing definition (unchanged)...

### cloudfront

Adjustment: Uses `frontend_certificate_arn` and sets `alternate_domain_names = ["app.caja.dbash.dev"]` (+ env hostnames if feature enabled).

### observability / redis

...existing definition (unchanged)...

## 8. Environment Composition (Dev) – Phase Mapping

Phases 0 (bootstrap) and 0.5 (IAM OIDC + deployer roles) are global, one-time foundations. Environment roots begin applying from Phase 2 onward. Layer application of phases instead of all modules at once:

1. Phase 2: networking + security
2. Phase 3: rds-postgres (+ secrets for DB credentials)
3. Phase 4: ecr, ecs-cluster
4. Phase 5: alb + ecs-service (FastAPI) (wire health check)
5. Phase 6: s3-static-site + cloudfront
6. Phase 7: dns alias records referencing outputs
7. Phase 8: observability (alarms, log retention)

`terraform.tfvars` for dev will include:

```hcl
environment        = "dev"
hosted_zone_id     = "<from bootstrap output>"
root_domain        = "dbash.dev"
enable_env_subdomains = true
backend_image_tag  = "dev-initial"
```

## 9. Risk Adjustments (Domain Strategy)

| Risk | Previous Exposure | Mitigation Now |
|------|-------------------|----------------|
| Cert issuance delay | Combined first-run apply | Isolated domain module (Phase 1) |
| DNS cutover race | Zone and infra interleaved | Bootstrap zone first, pause for propagation |
| Alias pointing to missing targets | Created too early | Defer alias creation to Phase 7 |
| Env sprawl in SANs | Hard to retract | San lists controlled by boolean + list inputs |
| Late IAM/OIDC introduction | Blocks CI pipeline & secure applies | Introduce Phase 0.5 IAM OIDC + deployer roles early |

## 10. Incremental PR Workflow

| PR | Contents | Acceptance Checks |
|----|----------|-------------------|
| #1 | Bootstrap stack docs only (no code run yet) | Plan reviewed (local) |
| #2 | IAM OIDC provider + deployer roles (Phase 0.5) | GitHub Actions dry-run plan assumes role successfully |
| #3 | Domain module code & apply (cert issuance) | Both certs Issued |
| #4 | Networking + security | VPC/Subnets routing validated |
| #5 | RDS + secret | Connection test via temporary script |
| #6 | ECS cluster + ECR + base image push | Repo exists; cluster healthy |
| #7 | ALB + ECS service (API reachable) | `/health` returns 200 via ALB DNS |
| #8 | Static site + CloudFront | CF deploy complete; default index reachable |
| #9 | DNS alias records | `curl https://api.caja.dbash.dev/health` OK |
| #10 | Observability alarms | Alarms show OK states |
| #11 | CI/CD workflow | PR plan comments successfully posted |

## 11. Manual Step Recap (Only One)

"Update Hover nameservers to Route 53 NS (Phase 0)" — no other manual AWS console actions expected for MVP.

## 12. Removal of Premature Terraform Scaffolding

All previously auto-created `.tf` files for bootstrap/domain scaffolding have been removed to keep repository focused on plan-first approach. Implementation will recreate them deliberately during Phase execution.

## 13. Next Actions (After Plan Approval)

1. Approve this updated `iac.md` (add APPROVED marker below).
2. Create PR #1 adding bootstrap stack code (no apply in CI yet; local only).
3. Apply bootstrap locally → update Hover NS → wait propagation.
4. Create PR #2 for Phase 0.5 IAM OIDC provider + deployer roles (enables future automated plans).
5. After role assumption validated, proceed with Phase 1 domain module PR (now PR #3).

## 17. Approval Marker (Incremental Plan)

Add a comment or edit this file with: `APPROVED: <name> <date>` to authorize Phase 0 implementation.

<!-- Removed duplicated original module detailed specs to avoid heading duplication. Original detailed contracts remain earlier in the document. -->

---

## 3. Environment Composition (Example: dev)

Layering order:

1. networking
2. security
3. ecr
4. rds-postgres
5. alb
6. ecs-cluster
7. ecs-service (backend)
8. s3-static-site
9. cloudfront
10. route53
11. observability

Backend service environment variable example:

```bash
DATABASE_URL=postgresql://{user}:{pass}@{endpoint}:5432/appdb
```

Delivered to ECS via secrets (never plain env var containing credentials directly).

---

## 4. Security & Compliance

| Area | Control |
|------|---------|
| IAM | Separate task execution vs task role (least privilege) |
| Secrets | AWS Secrets Manager only (no plaintext) |
| Network | Private ECS/RDS; ALB is sole public ingress |
| Encryption | S3 SSE-S3, RDS encryption, Secrets Manager KMS (AWS-managed) |
| TLS | ACM cert, TLS 1.2 min (ALB & CloudFront) |
| Logging | Structured JSON to CloudWatch; optional ALB/CF logs staging+ |
| WAF | Deferred (Phase 2) |
| Secret Rotation | Deferred (plan via rotation Lambda) |

---

## 5. Scaling & Availability Strategy

| Component | MVP | Scale Path |
|-----------|-----|-----------|
| ECS | 1–3 tasks | Target tracking autoscaling (CPU 60%, memory 70%) |
| RDS | Single AZ dev; Multi-AZ prod | Read replica for analytics |
| Redis | Deferred | Add for caching & rate limiting |
| ALB | 2 AZ | Add WAF + Blue/Green |
| Frontend | S3 + CloudFront | Edge functions / routing logic |
| DNS | Simple A/AAAA | Failover & multi-region later |

Autoscaling cooldowns: scale-out 60s, scale-in 300s.

---

## 6. CI/CD (GitHub Actions)

Workflow file: `.github/workflows/infra-plan-apply.yml`

Triggers:

- PR touching `infrastructure/**`: plan only
- Push to `main`: auto-apply `dev`
- Manual approval for `staging`, manual dispatch for `prod`

Steps:

1. Checkout
2. Setup Terraform
3. Format / validate / (optional) tflint / tfsec / infracost
4. Matrix plan across envs (subset) on PR
5. Upload plan artifact + comment summary
6. Apply with environment protection (approval gates)

Auth: GitHub OIDC → Assume `caja-terraform-deployer-{env}` role.

Image pipeline separation:

- Backend build pushes ECR tags: `sha`, `env-latest`
- Terraform references immutable tag; updating tag triggers plan/apply
- Optional faster deploy path: register new task definition via AWS CLI (outside Terraform) for purely application rollout

---

## 7. Observability Plan

Alarms (initial thresholds):

- ALB 5XX > 5 (5m)
- ECS CPU > 80% (5m)
- ECS Memory > 80% (5m)
- RDS FreeStorage < 10%
- RDS CPU > 80% (10m)
- (Future) p95 latency > 2s (ALB TargetResponseTime)

Retention:

- Dev logs: 30d
- Staging logs: 60d
- Prod logs: 90d

CloudFront & ALB access logs: enable staging+, optional dev cost reduction.

Dashboard (Phase 2): consolidated traffic, latency, error rate, saturation.

---

## 8. Variables (Representative)

```hcl
variable "project" { type = string default = "caja" }
variable "environment" { type = string }
variable "region" { type = string default = "us-east-1" }
variable "domain_name" { type = string }
variable "hosted_zone_id" { type = string default = null }
variable "certificate_arn" { type = string }
variable "backend_image_tag" { type = string }
variable "desired_count" { type = number default = 1 }
variable "db_instance_class" { type = string }
variable "db_allocated_storage" { type = number }
variable "db_max_allocated_storage" { type = number }
variable "db_backup_retention" { type = number }
variable "db_multi_az" { type = bool }
variable "enable_single_nat" { type = bool default = true }
```

---

## 9. Secrets Handling Pattern

- RDS secret JSON: `{ "username": "caja_app", "password": "<generated>" }`
- Terraform builds `DATABASE_URL` from secret + endpoint
- ECS task definition includes secrets via ARN references
- JWT key, session salt, etc. stored as discrete secrets (scope isolation)

---

## 10. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| NAT cost in low env | Higher spend | `enable_single_nat=true` |
| Secret exposure | Credential leak | Use Secrets Manager ARNs only |
| Drift | Inconsistent infra | Scheduled plan checks / no-console policy |
| Deploy downtime | User impact | ECS minHealthyPercent=100 + circuit breaker |
| Scaling lag | Performance | Aggressive scale-out cooldown |
| Expired cert | Outage | ACM DNS validation auto-renew |

---

## 11. Future Enhancements Roadmap

1. WAF + Managed Rule Sets
2. Redis for ephemeral state / rate limiting
3. CodeDeploy Blue/Green for ECS
4. KMS CMKs (S3/RDS/Secrets) for compliance
5. Multi-region replication & failover
6. CloudWatch Synthetics canaries
7. Secret rotation automation
8. Infracost cost diff in PRs
9. OpenTelemetry tracing + X-Ray
10. Lambda@Edge / CloudFront Functions for routing & A/B

---

## 12. Execution Sequence (After Approval)

1. Bootstrap state bucket + lock table (if absent)
2. Scaffold `modules/` (skeleton main/variables/outputs)
3. Implement `networking` + `security`
4. Add `ecr`, `ecs-cluster`, `alb`, `rds-postgres`
5. Compose `environments/dev` and run init/validate/plan
6. Add `s3-static-site`, `cloudfront`, `route53`
7. Add `observability` baseline alarms
8. Introduce GitHub Actions workflow & OIDC docs
9. Produce initial plan artifact for review

---

## 13. Required Inputs Before Apply

Please provide when available:

- Hosted Zone ID (or confirm create new)
- Domain (e.g. `caja.example.com`)
- ACM Certificate ARN(s)
- Alarm notification email(s)
- Desired initial DB sizes/classes per env

If not yet decided, placeholders with TODO markers will be inserted.

---

## 14. Cost-Aware Environment Defaults

| Env | ECS Desired | DB Class | NAT Strategy | Logs Retention |
|-----|-------------|----------|--------------|----------------|
| dev | 1 | t4g.micro | single NAT | 30d |
| staging | 2 | t4g.small | single NAT | 60d |
| prod | 3 (autoscale) | t4g.medium (multi-AZ) | per-AZ NAT | 90d |

---

## 15. Quality Gates Before Production

- `terraform validate` passes
- `tflint` baseline accepted
- `tfsec` critical issues = 0
- Plan reviewed & approved
- Drift check green
- Alarms smoke-tested (e.g., manual metric injection)

---

## 16. Notes

- Activity framework expansion initially scales via autoscaling only.
- WebSockets migration path: API Gateway WebSocket or AppSync under `/ws`.
- Redis introduction is non-breaking (additional module + config variable change).

---

## 17. Approval Marker

Add a comment or edit this file with: `APPROVED: <name> <date>` to authorize scaffolding.

---

End of Plan
