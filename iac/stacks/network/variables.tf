variable "environment" {
  type        = string
  description = "Environment identifier (dev/prod/shared)"
  default     = "dev"
}

variable "aws_profile" {
  type        = string
  description = "Local AWS CLI profile"
  default     = "genai-immersion-houston"
}

variable "aws_region" {
  type        = string
  description = "AWS region for networking stack"
  default     = "us-west-2"
}

variable "vpc_cidr" {
  type        = string
  description = "Primary VPC CIDR block"
  default     = "10.42.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of AZs to span (2 or 3)"
  default     = 3
  validation {
    condition     = var.az_count == 2 || var.az_count == 3
    error_message = "az_count must be 2 or 3"
  }
}

variable "enable_flow_logs" {
  type        = bool
  description = "Enable VPC Flow Logs"
  default     = true
}

variable "flow_logs_existing_role_arn" {
  type        = string
  description = "Optional pre-existing IAM role ARN for VPC Flow Logs (use if caller lacks iam:CreateRole). If set, module will not create a role."
  default     = ""
}

variable "flow_logs_retention_days" {
  type        = number
  description = "CloudWatch Log retention in days for flow logs"
  default     = 14
}

variable "single_nat_gateway" {
  type        = bool
  description = "If true, provision only one NAT Gateway in the first public subnet to save cost"
  default     = true
}
