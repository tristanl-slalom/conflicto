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
3. Plan:
   ```bash
   terraform plan
   ```
   Expect: create certificate + validation records; zone shows no changes.
4. Apply:
   ```bash
   terraform apply
   ```
5. Wait for validation to complete (can take a few minutes). Re-run:
   ```bash
   terraform refresh
   terraform output certificate_arn
   ```

## Variables
See `variables.tf` for customization (add more subdomains via `app_subdomains`).

## Safety
- `prevent_destroy` on hosted zone to avoid accidental deletion.
- Certificate uses `create_before_destroy` to enable seamless rotation.

## Future Enhancements
- Add root/apex ALIAS records for app endpoints once ALB/CloudFront exist.
- Separate wildcard certificate if needed (`*.conflicto.dbash.dev`).
- DNS query logging / resolver rules (future issue).
