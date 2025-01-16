resource "aws_s3_bucket" "terraform_state_bucket" {
  bucket = "mi-terraform-backend-${random_string.suffix.result}"

  tags = {
    Name = "Terraform State Bucket"
  }
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.terraform_state_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

output "backend_bucket_name" {
  value = aws_s3_bucket.terraform_state_bucket.bucket
}

output "backend_region" {
  value = "us-east-1" # Región fija en este ejemplo
}

output "backend_key" {
  value = "terraform/state/terraform.tfstate"
}

