module "vpc" {
  source             = "./modules/vpc"
  vpc_cidr           = "10.0.0.0/16"
  public_subnet_cidr = "10.0.1.0/24"
  az                 = "ca-central-1a"
  name_prefix        = "dev"
  admin_cidr         = var.admin_cidr
  llm_api_cidr       = var.llm_api_cidr
  expose_ollama_pub  = var.expose_ollama_pub
}

module "ec2" {
  source                 = "./modules/ec2"
  instance_count         = var.instance_count
  ami                    = var.ami
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [module.vpc.dev_sg_id]
  subnet_id              = module.vpc.public_subnet_id
}

#module "ec2" {
#  source = "./modules/ec2"
#
#  ami                    = var.ami
#  instance_type          = var.instance_type
#  subnet_id              = var.subnet_id
#  key_name               = var.key_name
#  vpc_security_group_ids = var.vpc_security_group_ids
#  name                   = "dev-instance"
#  env                    = "dev"
#}

#variable "ami" {
#  description = "The subnet ID to launch the instance in"
#  type        = string
#}
#
#variable "instance_type" {
#  description = "The subnet ID to launch the instance in"
#  type        = string
#}
#
#variable "subnet_id" {
#  description = "The subnet ID to launch the instance in"
#  type        = string
#}
#
#variable "key_name" {
#  description = "The name of the existing AWS key pair"
#  type        = string
#}
#
#variable "vpc_security_group_ids" {
#  description = "List of VPC security group IDs"
#  type        = list(string)
#}

provider "aws" {
  region = "ca-central-1"
}

#output "instance_id" {
#  value = module.c2.instance_id
#}

#output "public_ip" {
#  value = module.ec2_instance.public_ip
#}

output "instance_ips" {
  value = module.ec2.instance_ips
}

data "aws_iam_role" "ec2_role" {
  name = "CloudWatchEC2"
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = data.aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}
