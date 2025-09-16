variable "project" { type = string }
variable "kubernetes_version" { type = string }
variable "subnet_ids" { type = list(string) }
variable "endpoint_public_access" { type = bool }
variable "endpoint_private_access" { type = bool }
variable "public_access_cidrs" { type = list(string) }

