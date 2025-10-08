########################################
# ECS Stack (Issue 52)
# - ECS Cluster (Fargate)
# - (Optional) ECR Repository
# - Task Definition & Service
# - ALB + Target Group + Listener (HTTPS assumed later; HTTP now)
# - DNS A record (alias to ALB)
########################################

module "shared" {
  source      = "../../shared"
  environment = var.environment
  additional_tags = { Stack = "ecs" }
}

locals {
  name_prefix    = module.shared.name_prefix
  ecr_repo_name  = "${local.name_prefix}-backend"
  effective_image = var.create_service ? (var.container_image != "" ? var.container_image : (var.create_ecr_repo ? aws_ecr_repository.app[0].repository_url : "")) : "" # only relevant if service created
}

# ECR Repository (optional)
resource "aws_ecr_repository" "app" {
  count = var.create_ecr_repo ? 1 : 0
  name  = local.ecr_repo_name
  image_scanning_configuration { scan_on_push = true }
  tags = module.shared.tags
}

resource "aws_cloudwatch_log_group" "app" {
  count             = var.create_service ? 1 : 0
  name              = "/ecs/${local.name_prefix}-app"
  retention_in_days = 14
  tags              = module.shared.tags
}

resource "aws_ecs_cluster" "this" {
  name = "${local.name_prefix}-cluster"
  configuration {
    execute_command_configuration {
      logging = "DEFAULT"
    }
  }
  tags = module.shared.tags
}

# Security groups
resource "aws_security_group" "alb" {
  count  = var.create_service ? 1 : 0
  name   = "${local.name_prefix}-alb-sg"
  vpc_id = var.vpc_id
  tags   = merge(module.shared.tags, { Name = "${local.name_prefix}-alb-sg" })
}

resource "aws_security_group_rule" "alb_http_in" {
  count            = var.create_service ? 1 : 0
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.alb[0].id
  description       = "Allow HTTP"
}

resource "aws_security_group_rule" "alb_https_in" {
  count            = var.create_service && var.enable_https && var.certificate_arn != "" ? 1 : 0
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.alb[0].id
  description       = "Allow HTTPS"
}

resource "aws_security_group_rule" "alb_egress_all" {
  count            = var.create_service ? 1 : 0
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.alb[0].id
  description       = "Egress"
}

resource "aws_security_group" "app" {
  count  = var.create_service ? 1 : 0
  name   = "${local.name_prefix}-app-sg"
  vpc_id = var.vpc_id
  tags   = merge(module.shared.tags, { Name = "${local.name_prefix}-app-sg" })
}

resource "aws_security_group_rule" "app_from_alb" {
  count                    = var.create_service ? 1 : 0
  type                     = "ingress"
  from_port                = var.container_port
  to_port                  = var.container_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.app[0].id
  source_security_group_id = aws_security_group.alb[0].id
  description              = "ALB to app"
}

resource "aws_security_group_rule" "app_egress_all" {
  count            = var.create_service ? 1 : 0
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.app[0].id
}

# ALB
resource "aws_lb" "app" {
  count              = var.create_service ? 1 : 0
  name               = substr(replace("${local.name_prefix}-alb", "_", "-"), 0, 32)
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb[0].id]
  subnets            = var.public_subnet_ids
  idle_timeout       = var.alb_idle_timeout
  tags               = module.shared.tags
}

resource "aws_lb_target_group" "app" {
  count       = var.create_service ? 1 : 0
  name        = substr(replace("${local.name_prefix}-tg", "_", "-"), 0, 32)
  port        = var.container_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check {
    path                = var.health_check_path
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200-399"
  }
  tags = module.shared.tags
}

resource "aws_lb_listener" "http" {
  count             = var.create_service ? 1 : 0
  load_balancer_arn = aws_lb.app[0].arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type            = var.enable_https && var.certificate_arn != "" ? "redirect" : "forward"
    # target_group_arn only relevant when forwarding; null ignored when redirecting
    target_group_arn = var.enable_https && var.certificate_arn != "" ? null : aws_lb_target_group.app[0].arn
    dynamic "redirect" {
      for_each = var.enable_https && var.certificate_arn != "" ? [1] : []
      content {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = var.create_service && var.enable_https && var.certificate_arn != "" ? 1 : 0
  load_balancer_arn = aws_lb.app[0].arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app[0].arn
  }
}

# IAM roles for task execution (optional creation)
resource "aws_iam_role" "task_exec" {
  count = var.create_service && var.existing_task_execution_role_arn == "" ? 1 : 0
  name = "${local.name_prefix}-task-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
  tags = module.shared.tags
}

resource "aws_iam_role_policy_attachment" "task_exec_policy" {
  count      = var.create_service && var.existing_task_execution_role_arn == "" ? 1 : 0
  role       = aws_iam_role.task_exec[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Minimal Secrets Manager access when secret injection enabled (only if we created the role)
resource "aws_iam_role_policy" "task_exec_secrets" {
  count = var.create_service && var.inject_db_secret && var.db_secret_arn != "" && var.existing_task_execution_role_arn == "" ? 1 : 0
  name  = "${local.name_prefix}-task-exec-secrets"
  role  = aws_iam_role.task_exec[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = var.db_secret_arn
      }
    ]
  })
}

# Task definition
resource "aws_ecs_task_definition" "app" {
  count                    = var.create_service ? 1 : 0
  family                   = "${local.name_prefix}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.cpu)
  memory                   = tostring(var.memory)
  execution_role_arn       = var.existing_task_execution_role_arn != "" ? var.existing_task_execution_role_arn : aws_iam_role.task_exec[0].arn
  task_role_arn            = var.existing_task_execution_role_arn != "" ? var.existing_task_execution_role_arn : aws_iam_role.task_exec[0].arn
  container_definitions = jsonencode([
    merge({
      name      = "app"
      image     = local.effective_image
      essential = true
      portMappings = [{ containerPort = var.container_port, hostPort = var.container_port, protocol = "tcp" }]
      environment = []
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app[0].name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "app"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}${var.health_check_path} || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 10
      }
    }, var.inject_db_secret && var.db_secret_arn != "" ? {
      secrets = [
        for key in ["username","password","host","port","db_name","url"] : {
          name      = upper("DB_${key == "url" ? "CONNECTION_URL" : key}")
          valueFrom = "${var.db_secret_arn}:${key}::" # arn:...:secret:...:json-key:: (default stage)
        }
      ]
    } : {})
  ])
  tags = module.shared.tags
}

# Service
resource "aws_ecs_service" "app" {
  count           = var.create_service ? 1 : 0
  name            = "${local.name_prefix}-svc"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app[0].arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  enable_execute_command = var.enable_execute_command
  network_configuration {
    subnets         = var.app_subnet_ids
    security_groups = [aws_security_group.app[0].id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.app[0].arn
    container_name   = "app"
    container_port   = var.container_port
  }
  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200
  depends_on = [aws_lb_listener.http, aws_lb_listener.https]
  tags = module.shared.tags
}

# DNS record
resource "aws_route53_record" "app" {
  count   = var.create_service ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = var.app_domain
  type    = "A"
  alias {
    name                   = aws_lb.app[0].dns_name
    zone_id                = aws_lb.app[0].zone_id
    evaluate_target_health = true
  }
}

output "cluster_name" { value = aws_ecs_cluster.this.name }
output "cluster_arn" { value = aws_ecs_cluster.this.arn }
output "ecr_repository_url" { value = var.create_ecr_repo ? aws_ecr_repository.app[0].repository_url : "" }
output "service_name" { value = var.create_service ? aws_ecs_service.app[0].name : "" }
output "alb_dns_name" { value = var.create_service ? aws_lb.app[0].dns_name : "" }
output "https_enabled" { value = var.create_service && var.enable_https && var.certificate_arn != "" }
output "https_listener_arn" { value = var.create_service && var.enable_https && var.certificate_arn != "" ? aws_lb_listener.https[0].arn : "" }
output "task_definition_family" { value = var.create_service ? aws_ecs_task_definition.app[0].family : "" }
