# DNS & ACM Stack (Issue 49)

Provides Terraform management for the existing Route 53 hosted zone `dbash.dev` and provisions an ACM certificate for `conflicto.dbash.dev` + additional subdomains.

## Contents
- `aws_route53_zone.root` (import only; zone already exists)
- `aws_acm_certificate.app` + DNS validation records
- Outputs: zone id, certificate ARN, validation record map

## First-Time Setup

1. Initialize backend:
   ```bash
   terraform init -backend-config=backend.hcl
   ```
2. Import existing hosted zone (replace ZONEID):
   ```bash
   aws route53 list-hosted-zones --query "HostedZones[?Name=='dbash.dev.'].Id" --output text --profile genai-immersion-houston
   terraform import aws_route53_zone.root ZXXXXXXXXXXXX
   ```
3. (Optional) First import / plan with validation records deferred (default):
   The variable `defer_cert_validation_records` defaults to `true`, so the first
   plan will show only the certificate resource being created. This avoids the
   classic `Invalid for_each argument` error during `terraform import` because
   we are not yet trying to enumerate validation records.

   ```bash
   terraform plan -var defer_cert_validation_records=true
   ```

4. Apply certificate only (still deferring records):

   ```bash
   terraform apply -auto-approve -var defer_cert_validation_records=true -target=aws_acm_certificate.app
   ```

   After this, ACM has produced the per-domain validation options.

5. Enable validation records & finalize:

   ```bash
   terraform apply -auto-approve -var defer_cert_validation_records=false
   ```

   This creates the DNS `CNAME` validation records and the `aws_acm_certificate_validation` resource.

6. Wait for validation to complete (few minutes). Then:

   ```bash
   terraform refresh
   terraform output certificate_arn
   ```

 
## Variables

See `variables.tf` for customization (add more subdomains via `app_subdomains`).

Key variable introduced to ease initial import:

- `defer_cert_validation_records` (bool, default `true`): set to `false` only after the certificate has been created so Terraform can render stable for_each keys and create DNS validation records.

## Safety

- `prevent_destroy` on hosted zone to avoid accidental deletion.
- Certificate uses `create_before_destroy` to enable seamless rotation.

## Future Enhancements

- Add root/apex ALIAS records for app endpoints once ALB/CloudFront exist.
- Separate wildcard certificate if needed (`*.conflicto.dbash.dev`).
- DNS query logging / resolver rules (future issue).
