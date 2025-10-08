# Terraform Bootstrap Stack

This directory provisions the remote state backend resources used by ALL other Terraform stacks in this repository.

## Contents

- `versions.tf` – Terraform & provider version constraints (no backend block initially)
- `providers.tf` – Provider & input variables (profile, region, naming)
- `main.tf` – S3 bucket + DynamoDB table (+ optional KMS key) definitions
- `backend.hcl` – Parameters for S3 backend (used after initial apply)

## Usage

1. (First run uses local state)

   ```bash
   tfdir=iac/bootstrap
   cd "$tfdir"
   terraform init
   terraform plan -out plan.bootstrap
   terraform apply plan.bootstrap
   ```

2. Verify resources exist:

   ```bash
   aws s3 ls --profile genai-immersion-houston | grep tfstate
   aws dynamodb describe-table --table-name conflicto-terraform-locks --profile genai-immersion-houston >/dev/null && echo OK
   ```

3. Enable remote backend:

   - Add backend stanza (already documented in main README Section 7) OR keep `backend "s3" {}` in `versions.tf` and re-init:

   ```bash
   terraform init -migrate-state -backend-config=backend.hcl
   ```

4. Confirm state migrated:

   ```bash
   aws s3 ls s3://conflicto-tfstate --profile genai-immersion-houston | grep terraform.tfstate
   ```

## Customization

- Change defaults in `providers.tf` (profile, region, bucket names) BEFORE first apply.
- Set `enable_kms = true` if a customer-managed KMS key is required.
- Add lifecycle rules once retention policy is approved.
- Use a unique bucket name if collision occurs (e.g. append account id).

## Outputs

Run `terraform output` after apply to see bucket and lock table names (feed into other stacks if desired).

## Safety / Cleanup

- Do NOT delete the bucket or table while other stacks are active.
- Enable MFA delete manually if compliance requires (Terraform cannot manage MFA delete).
- Versioning allows state rollback; treat object versions as sensitive.

## Next Steps

Create `iac/envs/dev` with its own configuration, using the remote backend referencing this bucket and table.
