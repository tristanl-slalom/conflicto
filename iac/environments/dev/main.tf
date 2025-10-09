########################################
# Development Environment Configuration
# Deploys full Conflicto stack for dev environment
########################################

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "conflicto-terraform-state"
    key            = "environments/dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "conflicto"
      Environment = "dev"
      ManagedBy   = "terraform"
      Owner       = "tristanl-slalom"
    }
  }
}

# Networking Stack
module "network" {
  source      = "../../stacks/network"
  environment = "dev"
}

# RDS Database
module "rds" {
  source      = "../../stacks/rds"
  environment = "dev"

  # Development-specific sizing
  instance_class          = "db.t4g.micro"
  allocated_storage       = 20
  backup_retention_period = 1
  skip_final_snapshot     = true

  # Network dependencies
  vpc_id              = module.network.vpc_id
  private_subnet_ids  = module.network.private_subnet_ids
}

# ECS Services
module "ecs" {
  source      = "../../stacks/ecs"
  environment = "dev"

  # Development configuration
  create_service            = true
  create_ecr_repo          = false  # Use existing GHCR
  create_frontend_ecr_repo = true   # Create ECR repo for frontend
  container_image          = var.backend_image_uri
  frontend_image_uri       = var.frontend_image_uri

  # CPU/Memory for dev environment (cost optimized)
  backend_cpu           = 256
  backend_memory        = 512
  frontend_cpu          = 256
  frontend_memory       = 512

  # Database connection
  database_url          = module.rds.database_url

  # Network dependencies
  vpc_id              = module.network.vpc_id
  public_subnet_ids   = module.network.public_subnet_ids
  private_subnet_ids  = module.network.private_subnet_ids
}

# DNS Configuration
module "dns" {
  source      = "../../stacks/dns"
  environment = "dev"

  # Development domain
  domain_name = "dev.conflicto.app"
  alb_dns_name = module.ecs.alb_dns_name
  alb_zone_id  = module.ecs.alb_zone_id
}

# Security Group Rule: Allow ECS App to connect to RDS
resource "aws_security_group_rule" "app_to_database" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = module.rds.db_security_group_id
  source_security_group_id = module.ecs.app_security_group_id
  description              = "Allow ECS app to connect to RDS database"

  depends_on = [module.rds, module.ecs]
}
