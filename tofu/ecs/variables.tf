variable "project" { type = string }
variable "aws_region" { type = string }
variable "vpc_cidr" { type = string }
variable "azs" { type = list(string) }
variable "public_subnet_cidrs" { type = list(string) }
variable "private_subnet_cidrs" { type = list(string) }

variable "container_image" { type = string }

variable "container_port" {
  type    = number
  default = 8080
}

variable "health_check_path" {
  type    = string
  default = "/actuator/health"
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "db_name" {
  type    = string
  default = "ostock_dev"
}

variable "db_username" {
  type    = string
  default = "appuser"
}
# If empty, a random password will be generated and stored in Secrets Manager
variable "db_password" {
  type    = string
  default = ""
}
variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}
variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "bastion_instance_type" {
  default = "t3.micro"
}

variable "bastion_subnet_id" {
  description = "Private subnet ID for bastion"
  default     = null
}

variable "bastion_key_name" {
  description = "Optional SSH key pair name"
  default     = null
}
