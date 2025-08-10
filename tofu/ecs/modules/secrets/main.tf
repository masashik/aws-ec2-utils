resource "aws_secretsmanager_secret" "db" {
  name = "${var.project}/db"
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({
    username = var.db_username,
    password = var.db_password,
    host     = var.db_host,
    dbname   = var.db_name,
    port     = 5432,
    url      = "jdbc:postgresql://${var.db_host}:5432/${var.db_name}"
  })
}
