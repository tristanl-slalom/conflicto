# ECS Stack (Issue 52)

Phase 4 baseline per Issue 52 focuses on provisioning the container platform primitives (ECS Cluster + optional ECR). A toggle (`create_service`) allows progressing into service + ALB resources when ready, but defaults off to keep scope aligned with the issue.

## Resources (controlled by flags)

- Always: ECS Cluster
- Optional (default true): ECR repository (`create_ecr_repo`)
- Conditional (when `create_service=true`):
  - CloudWatch Log Group
  - Task Execution Role & Task Definition
  - Security Groups (ALB + app)
  - Application Load Balancer, Target Group, Listener (HTTP 80 now; 443 later)
  - Route53 A record alias to ALB

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

## Future Enhancements

- Add HTTPS listener + ACM cert ARN (already provisioned in dns stack) via `aws_lb_listener` on 443.
- WAFv2 WebACL association.
- Autoscaling policies (CPU/RequestCount) and target tracking.
- RDS secret injection via task definition environment or AWS Secrets Manager integration.
- Service discovery / private namespace.
- Blue/Green or canary deployments (CodeDeploy or ECS deployment circuit breaker).
- Add ECS Exec conditional IAM permissions if enable_execute_command=true.
