# ECS Stack (Issue 52)

Phase 4 baseline per Issue 52 originally focused on provisioning the container platform primitives (ECS Cluster + optional ECR). This branch now completes the service enablement with ALB, optional HTTPS, and optional database secret injection.

## Resources (controlled by flags)

- Always: ECS Cluster
- Optional (default true): ECR repository (`create_ecr_repo`)
- Conditional (when `create_service=true`):
  - CloudWatch Log Group
  - Task Execution Role & Task Definition
  - Security Groups (ALB + app, includes conditional 443 ingress when HTTPS enabled)
  - Application Load Balancer, Target Group, HTTP(80) + optional HTTPS(443) listeners (HTTP redirects to HTTPS when `enable_https=true` & cert provided)
  - Route53 A record alias to ALB
  - Optional database secret injection (`inject_db_secret=true` & `db_secret_arn` provided)

## Assumptions / Simplifications

- Default execution of Issue 52 sets `create_service=false` (cluster + repo only).
- HTTP only (when enabled); HTTPS/ACM added in follow-on phase.
- If no `container_image` provided and repo created, you can push `:latest` then re-plan with `create_service=true`.

## Usage

```bash
cd iac/stacks/ecs
make init
terraform plan \
  -var vpc_id=<vpc-id> \
  -var 'public_subnet_ids=["subnet-pubA","subnet-pubB","subnet-pubC"]' \
  -var 'app_subnet_ids=["subnet-appA","subnet-appB","subnet-appC"]' \
  -var hosted_zone_id=<zone-id> \
  -var app_domain=conflicto.dbash.dev
terraform apply -auto-approve \
  -var vpc_id=<vpc-id> \
  -var 'public_subnet_ids=["subnet-pubA","subnet-pubB","subnet-pubC"]' \
  -var 'app_subnet_ids=["subnet-appA","subnet-appB","subnet-appC"]' \
  -var hosted_zone_id=<zone-id> \
  -var app_domain=conflicto.dbash.dev

# Later (enable service & ALB)
terraform apply -auto-approve \
  -var vpc_id=<vpc-id> \
  -var 'public_subnet_ids=["subnet-pubA","subnet-pubB","subnet-pubC"]' \
  -var 'app_subnet_ids=["subnet-appA","subnet-appB","subnet-appC"]' \
  -var hosted_zone_id=<zone-id> \
  -var app_domain=conflicto.dbash.dev \
  -var create_service=true
```

Push container image (if using created repo):

```bash
ECR_URI=$(terraform output -raw alb_dns_name | sed 's/.*/$local_image_placeholder/') # placeholder; adjust after repo creation
```

## Variables Added

| Name | Purpose |
|------|---------|
| `enable_https` | Toggle creation of 443 listener & HTTP->HTTPS redirect. |
| `certificate_arn` | ACM cert for domain; required if `enable_https=true`. |
| `inject_db_secret` | Whether to expose DB secret JSON keys as container secrets. |
| `db_secret_arn` | ARN of Secrets Manager secret created by RDS stack. |

## Secret Injection

When `inject_db_secret=true` and `db_secret_arn` is passed, the container receives the following secret-based environment variables (ECS secrets):

```bash
DB_USERNAME
DB_PASSWORD
DB_HOST
DB_PORT
DB_DB_NAME
DB_CONNECTION_URL
```

These are sourced from JSON keys `username`, `password`, `host`, `port`, `db_name`, `url` stored in the secret created by the RDS stack (`<name_prefix>/db`).

An inline IAM policy granting only `secretsmanager:GetSecretValue` on `db_secret_arn` is attached to the task execution role when secret injection is enabled.

## Outputs

| Output | Description |
|--------|-------------|
| `cluster_name` | ECS cluster name |
| `cluster_arn` | ECS cluster ARN |
| `ecr_repository_url` | ECR repo URL (if created) |
| `service_name` | ECS service name (if created) |
| `alb_dns_name` | ALB DNS name (if service created) |
| `https_enabled` | Boolean indicating HTTPS listener active |
| `https_listener_arn` | ARN of HTTPS listener (if enabled) |

## Remaining Future Enhancements

- WAFv2 WebACL association.
- Autoscaling policies (CPU/RequestCount) and target tracking.
- Service discovery / private namespace.
- Blue/Green or canary deployments (CodeDeploy or ECS deployment circuit breaker).
- Add ECS Exec conditional IAM permissions if enable_execute_command=true.
