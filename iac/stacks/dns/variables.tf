variable "environment" {
  type        = string
  description = "Logical environment tag (shared/dev/prod)"
  default     = "shared"
}

variable "root_domain" {
  type        = string
  description = "Root domain name hosted in Route 53 (already created)"
  default     = "dbash.dev"
}

variable "app_subdomains" {
  type        = list(string)
  description = "Additional app subdomains to include on the certificate (besides primary)."
  default     = ["api.conflicto.dbash.dev"]
}

variable "primary_app_domain" {
  type        = string
  description = "Primary application FQDN for certificate common name"
  default     = "conflicto.dbash.dev"
}

variable "aws_profile" {
  type        = string
  description = "Local AWS CLI profile for manual runs"
  default     = "genai-immersion-houston"
}

variable "aws_region" {
  type        = string
  description = "Primary region (also certificate region). Use us-east-1 for CloudFront compatibility."
  default     = "us-east-1"
}
