terraform {
  backend "s3" {
    bucket         = "conflicto-tfstate"
    key            = "iam/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "conflicto-terraform-locks"
    encrypt        = true
  }
}
