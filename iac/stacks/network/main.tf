########################################
# Network Stack (Issue 50)
#  - VPC (10.42.0.0/16)
#  - Public / Private / Data / Endpoint subnets (3 AZs)
#  - IGW, single NAT (cost-optimized) unless disabled
#  - Route tables & associations
#  - Optional VPC Flow Logs to CloudWatch
########################################

module "shared" {
  source      = "../../shared"
  environment = var.environment
  additional_tags = { Stack = "network" }
}

# Discover AZs (limit to az_count)
data "aws_availability_zones" "available" {
  state = "available"
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required", "opted-in"]
  }
}

locals {
  selected_azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)

  # Subnet CIDR allocations (static deterministic mapping)
  public_subnet_cidrs  = [for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, i)]                # 10.42.0.0/24, 10.42.1.0/24, ...
  app_subnet_cidrs     = [for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, 10 + i)]          # 10.42.10.x/24
  data_subnet_cidrs    = [for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, 20 + i)]          # 10.42.20.x/24
  endpoint_subnet_cidrs= [for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, 30 + i)]          # 10.42.30.x/24
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-vpc" })
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-igw" })
}

# Public subnets
resource "aws_subnet" "public" {
  for_each = { for idx, az in local.selected_azs : az => {
    cidr = local.public_subnet_cidrs[idx]
    idx  = idx
  } }
  vpc_id                  = aws_vpc.main.id
  availability_zone       = each.key
  cidr_block              = each.value.cidr
  map_public_ip_on_launch = true
  tags = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-pub-${each.value.idx}", Tier = "public" })
}

# Application (private) subnets
resource "aws_subnet" "app" {
  for_each = { for idx, az in local.selected_azs : az => {
    cidr = local.app_subnet_cidrs[idx]
    idx  = idx
  } }
  vpc_id            = aws_vpc.main.id
  availability_zone = each.key
  cidr_block        = each.value.cidr
  tags = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-app-${each.value.idx}", Tier = "app" })
}

# Data subnets (RDS / ElastiCache)
resource "aws_subnet" "data" {
  for_each = { for idx, az in local.selected_azs : az => {
    cidr = local.data_subnet_cidrs[idx]
    idx  = idx
  } }
  vpc_id            = aws_vpc.main.id
  availability_zone = each.key
  cidr_block        = each.value.cidr
  tags = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-data-${each.value.idx}", Tier = "data" })
}

# Endpoint / intra subnets
resource "aws_subnet" "endpoint" {
  for_each = { for idx, az in local.selected_azs : az => {
    cidr = local.endpoint_subnet_cidrs[idx]
    idx  = idx
  } }
  vpc_id            = aws_vpc.main.id
  availability_zone = each.key
  cidr_block        = each.value.cidr
  tags = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-endpoint-${each.value.idx}", Tier = "endpoint" })
}

# Elastic IP for single NAT (if enabled)
resource "aws_eip" "nat" {
  count      = var.single_nat_gateway ? 1 : 0
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
  tags = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-nat-eip" })
}

resource "aws_nat_gateway" "nat" {
  count         = var.single_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = values(aws_subnet.public)[0].id
  tags          = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-nat" })
  depends_on    = [aws_internet_gateway.igw]
}

# Route tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = merge(module.shared.tags, { Name = "${module.shared.name_prefix}-public-rt" })
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_assoc" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

# Private route table(s)
# If single NAT: one shared private RT; else one RT per AZ for NAT in each AZ
resource "aws_route_table" "private" {
  count = var.single_nat_gateway ? 1 : var.az_count
  vpc_id = aws_vpc.main.id
  tags = merge(module.shared.tags, { Name = var.single_nat_gateway ? "${module.shared.name_prefix}-priv-rt" : "${module.shared.name_prefix}-priv-rt-${count.index}" })
}

resource "aws_route" "private_nat" {
  count                   = var.single_nat_gateway ? 1 : var.az_count
  route_table_id          = element(aws_route_table.private.*.id, count.index)
  destination_cidr_block  = "0.0.0.0/0"
  nat_gateway_id          = aws_nat_gateway.nat[0].id
  depends_on              = [aws_nat_gateway.nat]
}

# Associate app & endpoint subnets with private RT(s)
resource "aws_route_table_association" "app_assoc" {
  for_each = aws_subnet.app
  subnet_id = each.value.id
  # If single NAT use first RT else align idx
  route_table_id = var.single_nat_gateway ? aws_route_table.private[0].id : element(aws_route_table.private.*.id, index(local.selected_azs, each.key))
}

resource "aws_route_table_association" "endpoint_assoc" {
  for_each = aws_subnet.endpoint
  subnet_id = each.value.id
  route_table_id = var.single_nat_gateway ? aws_route_table.private[0].id : element(aws_route_table.private.*.id, index(local.selected_azs, each.key))
}

# Data subnets get same outbound path (may refine later for stricter egress)
resource "aws_route_table_association" "data_assoc" {
  for_each = aws_subnet.data
  subnet_id = each.value.id
  route_table_id = var.single_nat_gateway ? aws_route_table.private[0].id : element(aws_route_table.private.*.id, index(local.selected_azs, each.key))
}

############################
# Flow Logs (optional)
############################
resource "aws_cloudwatch_log_group" "flow" {
  count             = var.enable_flow_logs ? 1 : 0
  name              = "/vpc/flow/${module.shared.name_prefix}"
  retention_in_days = var.flow_logs_retention_days
  tags              = module.shared.tags
}

resource "aws_iam_role" "flow_logs" {
  count = var.enable_flow_logs && var.flow_logs_existing_role_arn == "" ? 1 : 0
  name  = "${module.shared.name_prefix}-vpc-flow-logs"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "vpc-flow-logs.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
  tags = module.shared.tags
}

resource "aws_iam_role_policy" "flow_logs" {
  count = var.enable_flow_logs && var.flow_logs_existing_role_arn == "" ? 1 : 0
  role  = aws_iam_role.flow_logs[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["logs:CreateLogStream", "logs:PutLogEvents"],
      Resource = "${aws_cloudwatch_log_group.flow[0].arn}:*"
    }]
  })
}

resource "aws_flow_log" "vpc" {
  count                = var.enable_flow_logs ? 1 : 0
  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.flow[0].arn
  iam_role_arn         = var.flow_logs_existing_role_arn != "" ? var.flow_logs_existing_role_arn : aws_iam_role.flow_logs[0].arn
  vpc_id               = aws_vpc.main.id
  traffic_type         = "ALL"
  tags                 = module.shared.tags
}

output "vpc_id" { value = aws_vpc.main.id }
output "public_subnet_ids" { value = [for s in aws_subnet.public : s.id] }
output "app_subnet_ids" { value = [for s in aws_subnet.app : s.id] }
output "data_subnet_ids" { value = [for s in aws_subnet.data : s.id] }
output "endpoint_subnet_ids" { value = [for s in aws_subnet.endpoint : s.id] }
