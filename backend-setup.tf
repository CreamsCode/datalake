resource "aws_s3_bucket" "terraform_state_bucket" {
  bucket = "mi-terraform-backend"
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name = "Terraform State Bucket"
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "Terraform Locks Table"
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

