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

provider "aws" {
  region = "ca-central-1"
}

resource "aws_instance" "dev_ec2" {
  ami                    = var.ami  # Amazon Linux 2 AMI in ca-central-1
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id  # <-- Replace with your subnet ID
  key_name               = var.key_name    # <-- Replace with your SSH key name

  tags = {
    Name = "dev-instance"
    env  = "dev"
  }
}

output "instance_id" {
  value = aws_instance.dev_ec2.id
}

output "public_ip" {
  value = aws_instance.dev_ec2.public_ip
}
