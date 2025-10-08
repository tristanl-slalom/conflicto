terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # NOTE: Do NOT add the backend block until after first apply.
  # After resources exist, add:
  # backend "s3" {}
}
