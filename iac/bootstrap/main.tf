#############################################
# Terraform State Backend Bootstrap Module  #
#############################################

# IMPORTANT: Run this stack with LOCAL backend first.
# After apply, add backend block (see README) and re-run terraform init -migrate-state.

# (Optional) Customer managed key for encrypting state (only if enable_kms = true)
resource "aws_kms_key" "tf_state" {
  count                   = var.enable_kms ? 1 : 0
  description             = "KMS key for Terraform state bucket encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  tags                    = local.common_tags
}

# S3 bucket for Terraform state
resource "aws_s3_bucket" "tf_state" {
  bucket = var.state_bucket_name
  tags   = local.common_tags
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "tf_state" {
  bucket                  = aws_s3_bucket.tf_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning for state history & rollback capability
resource "aws_s3_bucket_versioning" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Default encryption (SSE-S3 or SSE-KMS if key enabled)
resource "aws_s3_bucket_server_side_encryption_configuration" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.enable_kms ? "aws:kms" : "AES256"
      kms_master_key_id = var.enable_kms ? aws_kms_key.tf_state[0].arn : null
    }
  }
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "tf_locks" {
  name         = var.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = local.common_tags
}

# Optional lifecycle rules (ADD AFTER DECISION)
# resource "aws_s3_bucket_lifecycle_configuration" "tf_state" {
#   bucket = aws_s3_bucket.tf_state.id
#   rule {
#     id     = "ExpireOldVersions"
#     status = "Enabled"
#     noncurrent_version_expiration {
#       noncurrent_days = 90
#     }
#   }
# }

output "state_bucket_name" {
  value       = aws_s3_bucket.tf_state.bucket
  description = "Terraform remote state bucket name"
}

output "lock_table_name" {
  value       = aws_dynamodb_table.tf_locks.name
  description = "Terraform lock table name"
}

output "kms_key_arn" {
  value       = var.enable_kms ? aws_kms_key.tf_state[0].arn : null
  description = "KMS key ARN used for state encryption (null if not created)"
}
