########################################
# DNS & ACM Stack (Issue 49)            #
#  - Imports existing hosted zone       #
#  - Provisions ACM certificate (DNS)  #
########################################

module "shared" {
  source      = "../../shared"
  environment = var.environment
  additional_tags = { Stack = "dns" }
}

# Existing hosted zone for the root domain. We import this after first init.
resource "aws_route53_zone" "root" {
  name    = var.root_domain
  comment = "Primary public hosted zone for ${var.root_domain} (imported)"
  tags    = module.shared.tags

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [comment]
  }
}

# Consolidate SANs list (filter any dupes)
locals {
  certificate_sans = distinct(var.app_subdomains)
}

resource "aws_acm_certificate" "app" {
  domain_name       = var.primary_app_domain
  validation_method = "DNS"
  subject_alternative_names = local.certificate_sans
  tags = merge(module.shared.tags, { Purpose = "app-certificate" })

  lifecycle {
    create_before_destroy = true
  }
}

# Create validation records for each domain validation option
resource "aws_route53_record" "cert_validation" {
  for_each = { for dvo in aws_acm_certificate.app.domain_validation_options : dvo.domain_name => dvo }
  zone_id  = aws_route53_zone.root.zone_id
  name     = each.value.resource_record_name
  type     = each.value.resource_record_type
  ttl      = 300
  records  = [each.value.resource_record_value]
  allow_overwrite = true
}

resource "aws_acm_certificate_validation" "app" {
  certificate_arn         = aws_acm_certificate.app.arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

output "zone_id" {
  value       = aws_route53_zone.root.zone_id
  description = "Hosted zone ID"
}

output "certificate_arn" {
  value       = aws_acm_certificate.app.arn
  description = "ACM certificate ARN (becomes valid after validation resource completes)"
}

output "validation_records" {
  value       = { for k, r in aws_route53_record.cert_validation : k => { name = r.name, fqdn = r.fqdn } }
  description = "Map of validation record names/FQDNs"
}
