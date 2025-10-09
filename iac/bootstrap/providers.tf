variable "var_region" {
  type        = string
  description = "AWS region for bootstrap resources"
  default     = "us-west-2" # Adjust if different
}

variable "var_profile" {
  type        = string
  description = "Local AWS CLI profile to use (SSO or static)"
  default     = "genai-immersion-houston" # Adjust to your configured profile
}

variable "project_prefix" {
  type        = string
  description = "Base prefix for all resources"
  default     = "conflicto"
}

variable "environment" {
  type        = string
  description = "Environment identifier (e.g. dev, stg, prod)"
  default     = "dev"
}

variable "state_bucket_name" {
  type        = string
  description = "(Globally unique) S3 bucket name for Terraform state"
  default     = "conflicto-tfstate" # Append -dev or account id if needed for uniqueness
}

variable "lock_table_name" {
  type        = string
  description = "DynamoDB table name for Terraform state locking"
  default     = "conflicto-terraform-locks"
}

variable "enable_kms" {
  type        = bool
  description = "Whether to create a customer-managed KMS key for state encryption"
  default     = false
}

provider "aws" {
  region  = var.var_region
  profile = var.var_profile
}

locals {
  common_tags = {
    Project = var.project_prefix
    Env     = var.environment
    Managed = "terraform"
  }
}
