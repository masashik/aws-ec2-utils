output "db_endpoint" { value = aws_db_instance.this.address }
output "db_name" { value = var.db_name }
output "db_username" { value = var.db_username }
output "db_password" {
  value     = local.final_password
  sensitive = true
}
