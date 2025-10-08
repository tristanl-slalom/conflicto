terraform {
  backend "s3" {
    bucket         = "conflicto-terraform-state-418389084763"
    key            = "iam/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "conflicto-terraform-locks"
    encrypt        = true
  }
}
