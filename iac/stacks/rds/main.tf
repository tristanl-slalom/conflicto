########################################
# RDS Stack (Issue 51)
#  - PostgreSQL instance
#  - Subnet group (data subnets)
#  - Security groups (DB + ingress from app tier)
#  - Secrets Manager secret (username/password + URL)
########################################

module "shared" {
  source      = "../../shared"
  environment = var.environment
  additional_tags = { Stack = "rds" }
}

locals {
  name_prefix = module.shared.name_prefix
  db_identifier = "${local.name_prefix}-db"
}

# Random password
resource "random_password" "db" {
  length  = 20
  special = true
}

# Subnet group
resource "aws_db_subnet_group" "db" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = var.data_subnet_ids
  tags       = merge(module.shared.tags, { Name = "${local.name_prefix}-db-subnets" })
}

# Security Group for DB
resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db-sg"
  description = "Postgres access for ${local.name_prefix}"
  vpc_id      = var.vpc_id
  tags        = merge(module.shared.tags, { Name = "${local.name_prefix}-db-sg" })
}

# Placeholder app security group (could be passed later); for now a self rule + optional CIDRs
resource "aws_security_group" "db_ingress_extra" {
  count       = length(var.allow_app_cidr_blocks) > 0 ? 1 : 0
  name        = "${local.name_prefix}-db-extra-ingress"
  description = "Extra CIDR ingress for dev/testing"
  vpc_id      = var.vpc_id
  tags        = merge(module.shared.tags, { Name = "${local.name_prefix}-db-extra-ingress" })
}

resource "aws_security_group_rule" "db_allow_self" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.db.id
  source_security_group_id = aws_security_group.db.id
  description              = "Self reference (migrations, internal tooling)"
}

resource "aws_security_group_rule" "db_allow_cidrs" {
  count             = length(var.allow_app_cidr_blocks)
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.db.id
  cidr_blocks       = [element(var.allow_app_cidr_blocks, count.index)]
  description       = "Temporary CIDR ingress"
}

# Egress all (app connections out, patching, etc.)
resource "aws_security_group_rule" "db_egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.db.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Egress for system updates"
}

# Parameter group (customization placeholder)
resource "aws_db_parameter_group" "pg" {
  name        = "${local.name_prefix}-pg${replace(var.db_engine_version, ".", "")}" 
  family      = "postgres${substr(var.db_engine_version,0,2)}" # e.g. 15 -> postgres15
  description = "Parameter group for ${local.name_prefix}"

  # Add future parameter overrides here
}

# RDS Instance
resource "aws_db_instance" "db" {
  identifier              = local.db_identifier
  engine                  = "postgres"
  engine_version          = var.db_engine_version
  instance_class          = var.instance_class
  username                = var.username
  password                = random_password.db.result
  db_name                 = var.db_name
  allocated_storage       = var.allocated_storage
  max_allocated_storage   = var.max_allocated_storage
  storage_encrypted       = true
  deletion_protection     = var.deletion_protection
  multi_az                = var.multi_az
  db_subnet_group_name    = aws_db_subnet_group.db.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  backup_retention_period = var.backup_retention_days
  apply_immediately       = true
  performance_insights_enabled = var.performance_insights
  publicly_accessible     = var.publicly_accessible
  skip_final_snapshot     = true
  parameter_group_name    = aws_db_parameter_group.pg.name

  tags = merge(module.shared.tags, { Name = local.db_identifier })

  lifecycle {
    ignore_changes = [password]
  }
}

# Secrets Manager secret (JSON with creds & URL)
resource "aws_secretsmanager_secret" "db" {
  name = "${local.name_prefix}/db"
  tags = module.shared.tags
}

locals {
  connection_url = "postgresql://${var.username}:${random_password.db.result}@${aws_db_instance.db.address}:5432/${var.db_name}"
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({
    username = var.username
    password = random_password.db.result
    host     = aws_db_instance.db.address
    port     = 5432
    db_name  = var.db_name
    url      = local.connection_url
  })
}

output "db_endpoint" { value = aws_db_instance.db.address }
output "db_port"     { value = aws_db_instance.db.port }
output "db_secret_arn" { value = aws_secretsmanager_secret.db.arn }
output "db_connection_url" { value = local.connection_url sensitive = true }
