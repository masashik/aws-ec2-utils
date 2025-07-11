resource "aws_instance" "dev_ec2" {
  ami                    = var.ami  # Amazon Linux 2 AMI in ca-central-1
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id  # <-- Replace with your subnet ID
  key_name               = var.key_name    # <-- Replace with your SSH key name
  vpc_security_group_ids = var.vpc_security_group_ids

  tags = {
    Name = "test-server-5"
    env  = "dev"
  }
}
