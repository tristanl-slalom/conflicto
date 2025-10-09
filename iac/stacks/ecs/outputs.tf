# ECS Stack Outputs

# Cluster Information
output "cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.this.name
}

output "cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.this.arn
}

# Service Information (for deployment automation)
output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = var.create_service ? aws_ecs_service.app[0].name : ""
}

output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = var.create_service && var.frontend_image_uri != "" ? aws_ecs_service.frontend[0].name : ""
}

output "service_name" {
  description = "Name of the main ECS service"
  value       = var.create_service ? aws_ecs_service.app[0].name : ""
}

output "service_arn" {
  description = "ARN of the main ECS service"
  value       = var.create_service ? aws_ecs_service.app[0].id : ""
}

# Task Definition Information
output "task_definition_family" {
  description = "Family name of the task definition"
  value       = var.create_service ? aws_ecs_task_definition.app[0].family : ""
}

output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = var.create_service ? aws_ecs_task_definition.app[0].arn : ""
}

# Load Balancer Information
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = var.create_service ? aws_lb.app[0].dns_name : ""
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = var.create_service ? aws_lb.app[0].zone_id : ""
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = var.create_service ? aws_lb.app[0].arn : ""
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = var.create_service ? aws_lb_target_group.app[0].arn : ""
}

# Security Group Information
output "app_security_group_id" {
  description = "ID of the app security group (for database access)"
  value       = var.create_service ? aws_security_group.app[0].id : ""
}

# HTTPS Configuration
output "https_enabled" {
  description = "Whether HTTPS is enabled"
  value       = var.create_service && var.enable_https && var.certificate_arn != ""
}

output "https_listener_arn" {
  description = "ARN of the HTTPS listener"
  value       = var.create_service && var.enable_https && var.certificate_arn != "" ? aws_lb_listener.https[0].arn : ""
}

# ECR Repository
output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = var.create_ecr_repo ? aws_ecr_repository.app[0].repository_url : ""
}
