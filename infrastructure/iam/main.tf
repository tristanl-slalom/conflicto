terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

# GitHub Actions OIDC Provider
resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    var.github_oidc_thumbprint
  ]

  tags = {
    Name        = "github-actions-oidc"
    Project     = "conflicto"
    ManagedBy   = "terraform"
    Description = "OIDC provider for GitHub Actions CI/CD"
  }
}

# Terraform Deployer Roles (per environment)
resource "aws_iam_role" "terraform_deployer" {
  for_each = toset(var.environments)

  name        = "conflicto-terraform-deployer-${each.key}"
  description = "GitHub Actions role for Terraform deployments to ${each.key} environment"

  max_session_duration = var.max_session_duration

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "GitHubActionsOIDC"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "conflicto-terraform-deployer-${each.key}"
    Environment = each.key
    Project     = "conflicto"
    ManagedBy   = "terraform"
    Purpose     = "ci-cd-terraform-deployment"
  }
}

# Permission policies for Terraform deployment
resource "aws_iam_role_policy" "terraform_deployer_policy" {
  for_each = toset(var.environments)

  name = "conflicto-terraform-deployer-${each.key}-policy"
  role = aws_iam_role.terraform_deployer[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Remote State Access
      {
        Sid    = "TerraformStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::conflicto-tfstate",
          "arn:aws:s3:::conflicto-tfstate/*"
        ]
      },
      {
        Sid    = "TerraformLockAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/conflicto-terraform-locks"
      },

      # Networking (Phase 1)
      {
        Sid    = "NetworkingManagement"
        Effect = "Allow"
        Action = [
          "ec2:*Vpc*",
          "ec2:*Subnet*",
          "ec2:*Route*",
          "ec2:*Gateway*",
          "ec2:*SecurityGroup*",
          "ec2:*NetworkAcl*",
          "ec2:*Address*",
          "ec2:Describe*",
          "ec2:CreateTags",
          "ec2:DeleteTags"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to VPC tags or specific VPC ARNs
      },

      # DNS & Certificates (Phase 2)
      {
        Sid    = "Route53Management"
        Effect = "Allow"
        Action = [
          "route53:ChangeResourceRecordSets",
          "route53:GetChange",
          "route53:GetHostedZone",
          "route53:ListHostedZones",
          "route53:ListResourceRecordSets",
          "route53:ListTagsForResource"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to specific hosted zone ARN
      },
      {
        Sid    = "CertificateManagement"
        Effect = "Allow"
        Action = [
          "acm:RequestCertificate",
          "acm:DescribeCertificate",
          "acm:ListCertificates",
          "acm:DeleteCertificate",
          "acm:AddTagsToCertificate",
          "acm:ListTagsForCertificate"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to certificates with Project=conflicto tag
      },

      # Database (Phase 3)
      {
        Sid    = "RDSManagement"
        Effect = "Allow"
        Action = [
          "rds:*"
        ]
        Resource = "*"
        # TODO Phase 10: Replace with granular actions and DB instance ARN pattern
      },
      {
        Sid    = "SecretsManagement"
        Effect = "Allow"
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:TagResource"
        ]
        Resource = "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:conflicto-*"
      },

      # Compute (Phases 4-5)
      {
        Sid    = "ECSManagement"
        Effect = "Allow"
        Action = [
          "ecs:*Cluster*",
          "ecs:*Service*",
          "ecs:*TaskDefinition*",
          "ecs:*Task",
          "ecs:Describe*",
          "ecs:List*",
          "ecs:TagResource",
          "ecs:UntagResource"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* cluster and service ARN patterns
      },
      {
        Sid    = "ECRManagement"
        Effect = "Allow"
        Action = [
          "ecr:*"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* repository ARN pattern
      },
      {
        Sid    = "LoadBalancerManagement"
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:*"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* load balancer and target group ARN patterns
      },

      # Observability
      {
        Sid    = "CloudWatchManagement"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:DeleteLogGroup",
          "logs:TagLogGroup",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:DeleteAlarms",
          "cloudwatch:DescribeAlarms"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to /aws/ecs/conflicto-* log group pattern
      },
      {
        Sid    = "SNSManagement"
        Effect = "Allow"
        Action = [
          "sns:CreateTopic",
          "sns:DeleteTopic",
          "sns:Subscribe",
          "sns:Unsubscribe",
          "sns:SetTopicAttributes",
          "sns:GetTopicAttributes",
          "sns:ListTopics",
          "sns:TagResource"
        ]
        Resource = "*"
        # TODO Phase 10: Scope to conflicto-* topic ARN pattern
      },

      # IAM (Limited PassRole only)
      {
        Sid    = "ECSTaskRolePassRole"
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/conflicto-*-ecs-exec",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/conflicto-*-ecs-task"
        ]
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}
