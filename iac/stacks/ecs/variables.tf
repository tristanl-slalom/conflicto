variable "environment" {
	type    = string
	default = "dev"
}

variable "aws_profile" {
	type    = string
	default = "genai-immersion-houston"
}

variable "aws_region" {
	type    = string
	default = "us-east-1"
}

variable "vpc_id" {
	type        = string
	description = "VPC ID"
}

variable "public_subnet_ids" {
	type        = list(string)
	description = "Public subnets for ALB"
}

variable "app_subnet_ids" {
	type        = list(string)
	description = "Private app subnets for ECS tasks"
}

variable "container_image" {
	type        = string
	description = "Full image URI (ECR or public)"
	default     = ""
}

variable "create_ecr_repo" {
	type    = bool
	default = true
}

variable "create_service" {
	type        = bool
	default     = false
	description = "If true, create ALB, task definition, service, DNS record (future phase)."
}

variable "existing_task_execution_role_arn" {
	type        = string
	default     = ""
	description = "If provided, reuse this IAM role ARN for ECS task execution/task role instead of creating one (must include AmazonECSTaskExecutionRolePolicy and any secrets permissions)."
}

variable "enable_https" {
	type        = bool
	default     = true
	description = "If true and a certificate_arn is provided, create an HTTPS listener on 443 and redirect HTTP->HTTPS."
}

variable "certificate_arn" {
	type        = string
	default     = ""
	description = "ACM certificate ARN for the app domain (required if enable_https=true)."
	validation {
	  condition     = !var.enable_https || length(var.certificate_arn) > 0
	  error_message = "enable_https is true but certificate_arn is empty. Provide ACM cert ARN or set enable_https=false."
	}
}

variable "inject_db_secret" {
	type        = bool
	default     = false
	description = "If true, inject RDS database secret values as container secrets (requires db_secret_arn)."
}

variable "db_secret_arn" {
	type        = string
	default     = ""
	description = "Secrets Manager ARN containing JSON with keys username,password,host,port,db_name,url."
	validation {
	  condition     = !var.inject_db_secret || length(var.db_secret_arn) > 0
	  error_message = "inject_db_secret is true but db_secret_arn is empty. Provide secret ARN or disable inject_db_secret."
	}
}

variable "cpu" {
	type    = number
	default = 256
}

variable "memory" {
	type    = number
	default = 512
}

variable "desired_count" {
	type    = number
	default = 1
}

variable "container_port" {
	type    = number
	default = 8000
}

variable "health_check_path" {
	type    = string
	default = "/api/v1/health"
}

variable "alb_idle_timeout" {
	type    = number
	default = 60
}

variable "enable_execute_command" {
	type    = bool
	default = true
}


variable "app_domain" {
	type        = string
	description = "FQDN (e.g. conflicto.dbash.dev)"
}

variable "hosted_zone_id" {
	type        = string
	description = "Public hosted zone id"
}
