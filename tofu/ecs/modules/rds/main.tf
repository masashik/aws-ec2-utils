resource "aws_db_subnet_group" "this" {
  name       = "${var.project}-db-subnet-group"
  subnet_ids = var.private_subnet_ids
}

resource "random_password" "this" {
  length  = 20
  special = true
  upper   = true
  lower   = true
  numeric = true
  override_characters = "!@#-_+="
}

locals {
  final_password = var.db_password != "" ? var.db_password : random_password.this.result
}

resource "aws_db_instance" "this" {
  identifier                 = "${var.project}-postgres"
  engine                     = "postgres"
  engine_version             = "16"
  instance_class             = var.db_instance_class
  allocated_storage          = var.db_allocated_storage
  db_name                    = var.db_name
  username                   = var.db_username
  password                   = local.final_password
  db_subnet_group_name       = aws_db_subnet_group.this.name
  vpc_security_group_ids     = [var.rds_sg_id]
  skip_final_snapshot        = true
  deletion_protection        = false
  publicly_accessible        = false
  storage_encrypted          = true
  backup_retention_period    = 7
  apply_immediately          = true
}
