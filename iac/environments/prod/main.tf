########################################
# Production Environment Configuration
# Deploys full Conflicto stack for production environment
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
    key            = "environments/prod/terraform.tfstate"
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
      Environment = "prod"
      ManagedBy   = "terraform"
      Owner       = "tristanl-slalom"
    }
  }
}

# Networking Stack
module "network" {
  source      = "../../stacks/network"
  environment = "prod"
}

# RDS Database
module "rds" {
  source      = "../../stacks/rds"
  environment = "prod"

  # Production-specific sizing
  instance_class          = "db.r6g.large"
  allocated_storage       = 100
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  skip_final_snapshot    = false

  # Network dependencies
  vpc_id              = module.network.vpc_id
  private_subnet_ids  = module.network.private_subnet_ids

  depends_on = [module.network]
}

# ECS Services
module "ecs" {
  source      = "../../stacks/ecs"
  environment = "prod"

  # Production configuration
  create_service         = true
  create_ecr_repo       = false  # Use existing GHCR
  container_image       = var.backend_image_uri
  frontend_image_uri    = var.frontend_image_uri

  # CPU/Memory for production (performance optimized)
  backend_cpu           = 1024
  backend_memory        = 2048
  frontend_cpu          = 512
  frontend_memory       = 1024

  # Database connection
  database_url          = module.rds.database_url

  # Network dependencies
  vpc_id              = module.network.vpc_id
  public_subnet_ids   = module.network.public_subnet_ids
  private_subnet_ids  = module.network.private_subnet_ids

  depends_on = [module.network, module.rds]
}

# DNS Configuration
module "dns" {
  source      = "../../stacks/dns"
  environment = "prod"

  # Production domain
  domain_name = "conflicto.app"
  alb_dns_name = module.ecs.alb_dns_name
  alb_zone_id  = module.ecs.alb_zone_id

  depends_on = [module.ecs]
}
