variable "ami" {
  description = "The ami ID to launch the instance in (Ex. ami-0f9cb75652314425a)"
  type        = string
}

variable "instance_type" {
  description = "The instance type to launch the instance in (Ex. t2.micro)"
  type        = string
}

#variable "subnet_id" {
#  description = "The subnet ID to launch the instance in"
#  type        = string
#}
#
variable "key_name" {
  description = "The name of the existing AWS key pair"
  type        = string
}
#
#variable "vpc_security_group_ids" {
#  description = "List of VPC security group IDs"
#  type        = list(string)
#}
#
#variable "vpc_security_group_id" {
#  type        = string
#  description = "SG to attach to EC2"
#}
variable "instance_count" {
  description = "Number of EC2 instances to launch"
  type        = number
}
