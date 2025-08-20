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

# root variables.tf
variable "admin_cidr" {
  description = "Admin source IP (/32) for SSH, Grafana, Prometheus, etc."
  type        = string
}

variable "llm_api_cidr" {
  description = "CIDR blocks allowed to access llm-api (8000)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "expose_ollama_pub" {
  description = "Temporarily expose Ollama (11434) to admin_cidr"
  type        = bool
  default     = false
}
