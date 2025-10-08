terraform {
  backend "s3" {
    bucket         = "conflicto-tfstate"
    key            = "iam/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "conflicto-terraform-locks"
    encrypt        = true
  }
}
