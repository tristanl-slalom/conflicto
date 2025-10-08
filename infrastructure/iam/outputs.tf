output "oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider"
  value       = aws_iam_openid_connect_provider.github_actions.arn
}

output "deployer_role_arns" {
  description = "Map of environment to deployer role ARN"
  value = {
    for env in var.environments :
    env => aws_iam_role.terraform_deployer[env].arn
  }
}

output "deployer_role_arn_dev" {
  description = "ARN of dev deployer role (for easy reference)"
  value       = aws_iam_role.terraform_deployer["dev"].arn
}

output "deployer_role_arn_staging" {
  description = "ARN of staging deployer role (for easy reference)"
  value       = aws_iam_role.terraform_deployer["staging"].arn
}

output "deployer_role_arn_prod" {
  description = "ARN of prod deployer role (for easy reference)"
  value       = aws_iam_role.terraform_deployer["prod"].arn
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "github_repository" {
  description = "GitHub repository with access"
  value       = var.github_repository
}
