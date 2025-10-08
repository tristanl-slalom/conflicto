# Network Stack (Issue 50)

Creates foundational networking for the application environment (dev).

## Resources

- VPC: 10.42.0.0/16
- Subnet tiers (3 AZs):
  - Public: internet ingress, NAT egress
  - App: ECS/Fargate, internal services
  - Data: RDS / ElastiCache
  - Endpoint: Interface endpoints / service mesh / shared infra
- Internet Gateway
- Single cost-optimized NAT Gateway (public subnet AZ0)
- Route tables & associations
- Optional VPC Flow Logs -> CloudWatch Logs (enabled by default)

## Rationale

- /16 chosen for long-term flexibility and consistent /24 subnet pattern.
- Single NAT initially limits cost; can evolve to per-AZ by toggling `single_nat_gateway=false` (will force new NATs & routing changes).
- Separate data tier to simplify future tighter egress controls and security groups.
- Endpoint subnets prevent crowding app tier when many interface endpoints arrive.

## Usage

```bash
cd iac/stacks/network
make init
make plan
make apply
make outputs
```

## Key Variables

| Name | Default | Purpose |
|------|---------|---------|
| vpc_cidr | 10.42.0.0/16 | Primary VPC CIDR |
| az_count | 3 | Number of AZs to span |
| single_nat_gateway | true | Cost optimization (one NAT) |
| enable_flow_logs | true | Toggle flow logs |
| flow_logs_retention_days | 14 | CloudWatch retention |

## Adjusting Later

- Switch to per-AZ NAT: set `single_nat_gateway=false` (plan will show additional NAT + route tables per AZ).
- Add secondary CIDR for EKS pod networking later (not included yet).
- Add gateway/privatelink endpoints: extend endpoint subnets & create `aws_vpc_endpoint` resources.

## Outputs

- `vpc_id`
- `public_subnet_ids`
- `app_subnet_ids`
- `data_subnet_ids`
- `endpoint_subnet_ids`

## Future Enhancements

- VPC Reachability Analyzer / Network ACL refinement
- Private Hosted Zone & interface endpoints
- Security Group baseline module
- Flow log export to S3 + Athena partitioning (long-term retention)
