#############################
# Shared Locals & Tag Logic #
#############################

variable "project" {
  type        = string
  description = "Global project identifier used as prefix"
  default     = "conflicto"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, stg, prod, shared, global)"
}

variable "owner" {
  type        = string
  description = "Owner or team tag"
  default     = "platform"
}

variable "cost_center" {
  type        = string
  description = "Optional cost center tag"
  default     = ""
}

variable "additional_tags" {
  type        = map(string)
  description = "Additional arbitrary tags to merge"
  default     = {}
}

locals {
  # Standardized naming helper (component only; caller appends env if needed)
  # Usage example: "${module.shared.name_prefix}-vpc" -> conflicto-dev-vpc
  name_prefix = "${var.project}-${var.environment}"

  base_tags = {
    Project    = var.project
    Env        = var.environment
    ManagedBy  = "terraform"
    Owner      = var.owner
  }

  merged_tags = merge(local.base_tags, var.cost_center == "" ? {} : { CostCenter = var.cost_center }, var.additional_tags)
}

output "name_prefix" {
  value       = local.name_prefix
  description = "Standard resource naming prefix"
}

output "tags" {
  value       = local.merged_tags
  description = "Merged common tags"
}
