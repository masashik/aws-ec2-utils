variable "ami" {}
variable "instance_type" {}
variable "subnet_id" {}
variable "key_name" {}
variable "vpc_security_group_ids" {
  type = list(string)
}
variable "name" {
  default = "dev-instance"
}
variable "env" {
  default = "dev"
}
