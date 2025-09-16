variable "project" { type = string }
variable "aws_region" { type = string }
variable "vpc_cidr" { type = string }
variable "azs" { type = list(string) }
variable "public_subnet_cidrs" { type = list(string) }
variable "private_subnet_cidrs" { type = list(string) }

variable "kubernetes_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "endpoint_public_access" {
  type    = bool
  default = true
}

variable "endpoint_private_access" {
  type    = bool
  default = true
}

variable "admin_cidr" {
  description = "CIDR allowed to reach public EKS API endpoint"
  type        = string
  default     = "0.0.0.0/0"
}

variable "node_group_name" {
  type    = string
  default = "default"
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t3.large"]
}

variable "node_disk_size" {
  type    = number
  default = 50
}

variable "desired_size" {
  type    = number
  default = 2
}

variable "min_size" {
  type    = number
  default = 1
}

variable "max_size" {
  type    = number
  default = 3
}

