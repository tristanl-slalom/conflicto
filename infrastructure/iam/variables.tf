variable "aws_region" {
  description = "AWS region for provider configuration"
  type        = string
  default     = "us-west-2"
}

variable "environments" {
  description = "List of environments for deployer roles"
  type        = list(string)
  default     = ["dev", "staging", "prod"]
}

variable "github_repository" {
  description = "GitHub repository in format owner/repo"
  type        = string
  default     = "tristanl-slalom/conflicto"

  validation {
    condition     = can(regex("^[^/]+/[^/]+$", var.github_repository))
    error_message = "Repository must be in format 'owner/repo'."
  }
}

variable "github_oidc_thumbprint" {
  description = "GitHub OIDC provider thumbprint"
  type        = string
  default     = "6938fd4d98bab03faadb97b34396831e3780aea1"
}

variable "max_session_duration" {
  description = "Maximum CLI/API session duration in seconds (1-12 hours)"
  type        = number
  default     = 3600

  validation {
    condition     = var.max_session_duration >= 3600 && var.max_session_duration <= 43200
    error_message = "Session duration must be between 3600 (1 hour) and 43200 (12 hours)."
  }
}
