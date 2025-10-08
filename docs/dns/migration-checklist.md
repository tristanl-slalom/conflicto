# DNS Root Zone Migration Checklist (Option 1)

Use this to migrate `dbash.dev` fully into Route 53 safely.

## 1. Inventory Existing Records (Current Provider)

Record each (fill before change):

| Type | Name | Value / Target | TTL | Notes |
|------|------|----------------|-----|-------|
| A    | dbash.dev |                |     | Root site / landing |
| A/AAAA | www.dbash.dev |            |     | Redirect / site |
| TXT  | dbash.dev |                |     | SPF / verification |
| MX   | dbash.dev |                |     | Mail provider |
| TXT  | _dmarc.dbash.dev |          |     | DMARC |
| CNAME| selector1._domainkey.dbash.dev | | | DKIM key 1 |
| CNAME| selector2._domainkey.dbash.dev | | | DKIM key 2 |
| SRV  | (any) |                  |     | Optional services |
| ...  |      |                  |     | Add lines as needed |

Optional: reduce TTLs (>= 3600 -> 300) a few hours before switching to speed propagation.

## 2. Create Route 53 Hosted Zone

1. Route 53 → Hosted zones → Create hosted zone.
2. Domain name: `dbash.dev` (Public hosted zone).
3. Add tags: `Project=conflicto`, `Env=shared`, `ManagedBy=terraform` (later import).
4. Note the 4 NS values.

## 3. Recreate Records in Route 53

Replicate all inventoried records exactly (adjust TTLs if you lowered them earlier). For root ALIAS to CloudFront/ALB later, you can temporarily point to the existing target.

## 4. Update Registrar Nameservers

Replace existing nameservers with the 4 from the hosted zone. Save.

## 5. Propagation Validation

Use multiple resolvers:

```bash
dig NS dbash.dev
dig @1.1.1.1 NS dbash.dev
dig +trace dbash.dev | grep -i awsdns
```

Expect only the AWS set. Update `scripts/expected_ns.conf` and run:

```bash
./scripts/check_nameservers.sh dbash.dev ./scripts/expected_ns.conf
```
Exit code 0 = success.

## 6. Post-Migration Hardening

- Restore TTLs to sane values (e.g. 300–900 for dynamic, 3600+ for static).
- Add / verify SPF, DKIM, DMARC if mail in use.
- Enable DNS query logging (optional) via CloudWatch Logs (future).

## 7. Terraform Adoption (Later Issue)

Inside DNS stack:

```hcl
resource "aws_route53_zone" "root" {
  name = "dbash.dev"
  tags = module.shared.tags
}
```
Import:

```bash
terraform import aws_route53_zone.root Z1234567890ABCDEF
```
Generate state and confirm `terraform plan` is no-op.

## 8. ACM Certificate Strategy Preview

For app endpoints:

- Short-term: request certificate for `conflicto.dbash.dev` (and maybe `api.conflicto.dbash.dev`).
- Later: wildcard `*.dbash.dev` if many subdomains emerge.

## 9. Rollback Plan

If something breaks (e.g., email):

- Revert registrar nameservers to original set (keep their list handy from inventory step).
- Propagation reversal usually < 1 hour with lowered TTLs.

## 10. Sign-Off

| Item | Done (Y/N) | Notes |
|------|------------|-------|
| Inventory complete |  |  |
| Route 53 zone created |  |  |
| Records recreated |  |  |
| Registrar NS updated |  |  |
| Propagation verified |  |  |
| Script check passed |  |  |
| Import into Terraform (later) |  |  |

---
Last updated: 2025-10-08
