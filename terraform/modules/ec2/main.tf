resource "aws_instance" "dev_ec2" {
  count                  = var.instance_count
  ami                    = var.ami  # Amazon Linux 2 AMI in ca-central-1
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id  # <-- Replace with your subnet ID
  key_name               = var.key_name    # <-- Replace with your SSH key name
  vpc_security_group_ids = var.vpc_security_group_ids
  iam_instance_profile   = "CloudWatchEC2"

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    sudo yum install -y perl-Switch perl-DateTime perl-Sys-Syslog perl-LWP-Protocol-https perl-Digest-SHA.x86_64
    cd /home/ec2-user/
    curl https://aws-cloudwatch.s3.amazonaws.com/downloads/CloudWatchMonitoringScripts-1.2.2.zip -O
    unzip CloudWatchMonitoringScripts-1.2.2.zip
    rm -rf CloudWatchMonitoringScripts-1.2.2.zip
  EOF

  tags = {
    Name = "dev-server"
    env  = "dev"
    auto_shutdown = "true"
  }
}
