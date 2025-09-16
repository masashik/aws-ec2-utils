variable "project" { type = string }
variable "cluster_name" { type = string }
variable "subnet_ids" { type = list(string) }
variable "node_group_name" { type = string }
variable "instance_types" { type = list(string) }
variable "disk_size" { type = number }
variable "desired_size" { type = number }
variable "min_size" { type = number }
variable "max_size" { type = number }

