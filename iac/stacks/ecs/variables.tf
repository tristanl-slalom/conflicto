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
