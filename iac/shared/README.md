# Shared Terraform Locals & Conventions (Issue 47)

This directory provides a lightweight, importable *module* that standardizes naming and tagging across all stacks.

## Exposed Interface

Inputs:

* `project` (string, default `conflicto`)
* `environment` (string, REQUIRED)
* `owner` (string, default `platform`)
* `cost_center` (string, optional)
* `additional_tags` (map(string), optional)
* `aws_region` (string, default `us-east-1`)
* `aws_profile` (string, default local profile)
* `enable_provider` (bool, default false)

Outputs:

* `name_prefix` (e.g. `conflicto-dev`)
* `tags` (merged tagging map)

## Usage Example (Inside a Stack Root)

```hcl
module "shared" {
  source      = "../../shared"
  environment = var.environment
  additional_tags = { Service = "api" }
}

resource "aws_s3_bucket" "example" {
  bucket = "${module.shared.name_prefix}-assets"
  tags   = module.shared.tags
}
```

## Rationale

* Centralizes naming/tag rules so a future change (e.g. add `DataClass`) occurs once.
* Allows early stacks to stay DRY without jumping to Terragrunt.
* Keeps provider enablement optional so root modules can own provider configuration.

## Next Steps

* DNS / ACM stack will consume this for consistent tagging.
* Later: extend with helper locals for common ARNs or partition aware formatting.
