############################
# Shared Provider Wrapper #
############################

variable "aws_region" {
  type        = string
  description = "Primary AWS region"
  default     = "us-east-1"
}

variable "aws_profile" {
  type        = string
  description = "Local AWS CLI profile (for human runs)"
  default     = "genai-immersion-houston"
}

# Allow callers to disable default provider (e.g., when inherited via root module)
variable "enable_provider" {
  type        = bool
  description = "Whether to configure an AWS provider in this shared module"
  default     = false
}

# Conditional provider - most stacks will define their own root provider; this is here for dev/local reuse
provider "aws" {
  count   = var.enable_provider ? 1 : 0
  region  = var.aws_region
  profile = var.aws_profile
}
