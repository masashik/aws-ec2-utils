variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
}

variable "public_subnet_cidr" {
  type        = string
  description = "CIDR block for the public subnet"
}

variable "az" {
  type        = string
  description = "Availability zone for the public subnet"
}

variable "name_prefix" {
  type        = string
  description = "Prefix to name VPC resources"
}
