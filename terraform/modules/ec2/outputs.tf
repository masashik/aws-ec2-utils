#output "instance_id" {
#  value = aws_instance.dev_ec2.id
#}
#output "public_ip" {
#  value = aws_instance.dev_ec2.public_ip
#}
output "instance_ids" {
  description = "IDs of all EC2 instances"
  value = [for instance in aws_instance.dev_ec2 : instance.id]
}
output "instance_ips" {
  description = "Public IPs of all EC2 instances"
  value = [for instance in aws_instance.dev_ec2 : instance.public_ip]
}
