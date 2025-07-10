variable "ami" {
  description = "The subnet ID to launch the instance in"
  type        = string
}


variable "instance_type" {
  description = "The subnet ID to launch the instance in"
  type        = string
}


variable "subnet_id" {
  description = "The subnet ID to launch the instance in"
  type        = string
}

variable "key_name" {
  description = "The name of the existing AWS key pair"
  type        = string
}

variable "vpc_security_group_ids" {
  description = "List of VPC security group IDs"
  type        = list(string)
}

provider "aws" {
  region = "ca-central-1"
}

resource "aws_instance" "dev_ec2" {
  ami                    = var.ami  # Amazon Linux 2 AMI in ca-central-1
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id  # <-- Replace with your subnet ID
  key_name               = var.key_name    # <-- Replace with your SSH key name
  vpc_security_group_ids = var.vpc_security_group_ids

  tags = {
    Name = "test-server-4"
    env  = "dev"
  }
}

output "instance_id" {
  value = aws_instance.dev_ec2.id
}

output "public_ip" {
  value = aws_instance.dev_ec2.public_ip
}
