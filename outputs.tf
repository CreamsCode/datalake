output "config_server_ip" {
  value = aws_instance.config_server.public_ip
}

output "mongos_ip" {
  value = aws_instance.mongos_router.public_ip
}

output "shard_ips" {
  value = aws_instance.shard[*].public_ip
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
