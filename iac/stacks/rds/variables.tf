variable "environment" {
  type        = string
  description = "Environment name (dev/prod/shared)"
  default     = "dev"
}

variable "aws_profile" {
  type        = string
  description = "AWS CLI profile"
  default     = "genai-immersion-houston"
}

variable "aws_region" {
  type        = string
  description = "Region"
  default     = "us-west-2"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where RDS will reside"
}

variable "data_subnet_ids" {
  type        = list(string)
  description = "List of data subnet IDs (at least 2)"
}

variable "db_engine_version" {
  type        = string
  description = "PostgreSQL engine version (use aws rds describe-db-engine-versions --engine postgres to list)."
  default     = "15.14"
}

variable "instance_class" {
  type        = string
  description = "RDS instance class (use burstable for dev)"
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  type        = number
  description = "Initial storage in GB"
  default     = 20
}

variable "max_allocated_storage" {
  type        = number
  description = "Autoscaling storage max"
  default     = 100
}

variable "deletion_protection" {
  type        = bool
  description = "Enable deletion protection (disable for ephemeral/dev)"
  default     = false
}

variable "multi_az" {
  type        = bool
  description = "Multi-AZ deployment (false for dev cost savings)"
  default     = false
}

variable "backup_retention_days" {
  type        = number
  description = "Backup retention days"
  default     = 3
}

variable "performance_insights" {
  type        = bool
  description = "Enable Performance Insights"
  default     = false
}

variable "enable_rds_proxy" {
  type        = bool
  description = "Create an RDS Proxy (future toggle)"
  default     = false
}

variable "db_name" {
  type        = string
  description = "Initial database name"
  default     = "conflicto"
}

variable "username" {
  type        = string
  description = "Master username"
  default     = "appuser"
}

variable "secret_rotation_days" {
  type        = number
  description = "Placeholder for future secret rotation integration"
  default     = 0
}

variable "publicly_accessible" {
  type        = bool
  description = "Should the instance be publicly accessible (dev only if absolutely required)"
  default     = false
}

variable "allow_app_cidr_blocks" {
  type        = list(string)
  description = "Optional list of CIDR blocks allowed inbound to DB SG (in addition to app SG). Leave empty normally."
  default     = []
}
