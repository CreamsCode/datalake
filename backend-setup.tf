variable "bucket_name" {
  default     = "mi-terraform-backend-${random_string.suffix.result}"
  description = "Nombre del bucket S3"
}

variable "region" {
  default     = "us-east-1"
  description = "Región de AWS"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "null_resource" "create_bucket_and_upload" {
  provisioner "local-exec" {
    command = <<EOT
      if aws s3api head-bucket --bucket ${var.bucket_name} 2>/dev/null; then
        echo "El bucket ${var.bucket_name} ya existe. No se necesita crear nuevamente."
      else
        echo "Creando el bucket ${var.bucket_name}..."
        aws s3api create-bucket --bucket ${var.bucket_name} --region ${var.region} --create-bucket-configuration LocationConstraint=${var.region}
        aws s3api put-bucket-versioning --bucket ${var.bucket_name} --versioning-configuration Status=Enabled
      fi
    EOT
  }
}

output "backend_bucket_name" {
  value = var.bucket_name
}

output "backend_region" {
  value = var.region
}

output "backend_key" {
  value = "terraform/state/terraform.tfstate"
}
