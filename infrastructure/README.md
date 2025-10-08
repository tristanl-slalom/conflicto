# Infrastructure

Terraform infrastructure for the Conflicto application.

## Structure

- `bootstrap/` - Remote state backend (S3 + DynamoDB)
- `iam/` - GitHub Actions OIDC and deployer roles
- `modules/` - Reusable infrastructure modules

## CI/CD Authentication

GitHub Actions workflows authenticate using IAM roles via OIDC.

**Stack:** `infrastructure/iam/`

**Roles:**
- `conflicto-terraform-deployer-dev`
- `conflicto-terraform-deployer-staging`
- `conflicto-terraform-deployer-prod`

**Trust:** Restricted to repository `tristanl-slalom/conflicto`

See `infrastructure/iam/README.md` for details.

## Getting Started

### Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Remote state backend provisioned (see `bootstrap/`)

### Deployment

Each stack can be deployed independently:

```bash
cd infrastructure/{stack-name}
terraform init
terraform plan
terraform apply
```

## Remote State

All stacks use S3 remote state backend:

- **Bucket:** `conflicto-terraform-state-{account-id}`
- **Lock Table:** `conflicto-terraform-locks`
- **Region:** `us-east-1`

Provisioned via `bootstrap/` stack.
