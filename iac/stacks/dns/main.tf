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
  # SANs (exclude the primary which is the CN)
  certificate_sans = distinct(var.app_subdomains)
  # All domains that will receive validation records (primary + SANs)
  certificate_domains = distinct(concat([var.primary_app_domain], var.app_subdomains))
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
##
# Validation DNS records
#
# Previous implementation attempted to drive for_each directly from
# aws_acm_certificate.app.domain_validation_options which are *unknown until after
# the certificate resource is created*. That caused `terraform import` (and an
# initial plan) to fail with: "Invalid for_each argument".
#
# Solution: make the for_each keys STATIC using the intended list of domains
# (primary + SANs). The individual record attributes (name, type, value) are
# then derived via list comprehensions that filter the eventual
# domain_validation_options. Prior to the certificate being created those
# expressions are simply unknown values, which Terraform can plan just fine.
# Once the certificate exists, a subsequent apply (or even the same apply when
# not importing) resolves them and creates the records.
##
resource "aws_route53_record" "cert_validation" {
  for_each = { for d in local.certificate_domains : d => d }

  zone_id = aws_route53_zone.root.zone_id

  # Each of these list comprehensions will produce a single-element list once
  # the certificate's validation options are known. Index [0] extracts it.
  name = [
    for dvo in aws_acm_certificate.app.domain_validation_options :
    dvo.resource_record_name if dvo.domain_name == each.key
  ][0]

  type = [
    for dvo in aws_acm_certificate.app.domain_validation_options :
    dvo.resource_record_type if dvo.domain_name == each.key
  ][0]

  ttl = 300

  records = [
    [
      for dvo in aws_acm_certificate.app.domain_validation_options :
      dvo.resource_record_value if dvo.domain_name == each.key
    ][0]
  ]

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
