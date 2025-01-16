variable "bucket_name" {
  default     = "terraform-backend"
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
      bucket_name=${var.bucket_name}-${random_string.suffix.result}
      if aws s3api head-bucket --bucket $bucket_name 2>/dev/null; then
        echo "El bucket $bucket_name ya existe. No se necesita crear nuevamente."
      else
        echo "Creando el bucket $bucket_name..."
        aws s3api create-bucket --bucket $bucket_name --region ${var.region}
      fi
    EOT
  }
}

output "backend_bucket_name" {
  value = "${var.bucket_name}-${random_string.suffix.result}"
}

output "backend_region" {
  value = var.region
}

output "backend_key" {
  value = "terraform/state/terraform.tfstate"
}
