# RDS Stack (Issue 51)

Provisions a PostgreSQL instance for the application (dev environment) plus supporting components.

## Resources

- RDS Instance (PostgreSQL)
- DB Subnet Group (data subnets)
- Security Group (self + optional CIDR ingress)
- Parameter Group (placeholder for tuning)
- Secrets Manager secret (credentials + connection URL)

## Usage

```bash
cd iac/stacks/rds
make init
terraform plan -var vpc_id=... -var 'data_subnet_ids=["subnet-aaa","subnet-bbb"]'
terraform apply -auto-approve -var vpc_id=... -var 'data_subnet_ids=["subnet-aaa","subnet-bbb"]'
make outputs
```

## Variables (key)

| Name | Purpose | Default |
|------|---------|---------|
| db_engine_version | PostgreSQL engine version | 15.4 |
| instance_class | Instance class | db.t4g.micro |
| allocated_storage | Initial storage GB | 20 |
| max_allocated_storage | Autoscale ceiling | 100 |
| multi_az | High availability | false |
| deletion_protection | Prevent destroy | false |
| backup_retention_days | Snapshot retention | 3 |
| publicly_accessible | Public endpoint | false |

## Secrets

Secret path: `<name_prefix>/db` containing JSON with:

```json
{
  "username": "...",
  "password": "...",
  "host": "...",
  "port": 5432,
  "db_name": "conflicto",
  "url": "postgresql://user:pass@host:5432/conflicto"
}
```

## Next Enhancements

### Engine Version Troubleshooting
If creation fails with `Cannot find version X.Y for postgres`, list available versions:

```bash
aws rds describe-db-engine-versions \
  --engine postgres \
  --query 'DBEngineVersions[].EngineVersion' \
  --profile genai-immersion-houston \
  --region us-east-1
```

Update `-var db_engine_version=...` or the `dev.auto.tfvars` accordingly and re-apply.

- Add SG rule referencing future app ECS/ALB SG instead of self.
- Add RDS Proxy optional resource.
- Enable Performance Insights / Enhanced Monitoring if needed.
- Add CloudWatch alarms (CPU, free storage, connections) and SNS topic.
- Incorporate secret rotation Lambda (AWS Secrets Manager rotation) if required.
