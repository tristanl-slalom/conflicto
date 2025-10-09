bucket         = "conflicto-tfstate"
key            = "stacks/rds/terraform.tfstate"
dynamodb_table = "conflicto-terraform-locks"
region         = "us-west-2"
profile        = "genai-immersion-houston"
encrypt        = true
use_lockfile   = true
