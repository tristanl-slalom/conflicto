# Backend configuration for remote state (apply AFTER first local apply)
# Usage:
#   terraform init -migrate-state -backend-config=backend.hcl

bucket         = "conflicto-tfstate"             # Keep in sync with var.state_bucket_name
dynamodb_table = "conflicto-terraform-locks"     # (Terraform 1.9+ deprecates this in favor of use_lockfile, still works for now)
region         = "us-east-1"
profile        = "genai-immersion-houston"
encrypt        = true
key            = "bootstrap/terraform.tfstate"   # State object path inside bucket (explicit to avoid init prompt)
use_lockfile   = true                             # Future-proof locking (can coexist during transition)
