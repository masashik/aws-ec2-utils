module "network" {
  source               = "./modules/network"
  project              = var.project
  vpc_cidr             = var.vpc_cidr
  azs                  = var.azs
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "security" {
  source       = "./modules/security"
  project      = var.project
  vpc_id       = module.network.vpc_id
  alb_vpc_cidr = var.vpc_cidr
}

module "rds" {
  source               = "./modules/rds"
  project              = var.project
  vpc_id               = module.network.vpc_id
  private_subnet_ids   = module.network.private_subnet_ids
  rds_sg_id            = module.security.rds_sg_id
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
  db_instance_class    = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
}

module "secrets" {
  source      = "./modules/secrets"
  project     = var.project
  db_username = module.rds.db_username
  db_password = module.rds.db_password
  db_name     = module.rds.db_name
  db_host     = module.rds.db_endpoint
}

module "alb" {
  source            = "./modules/alb"
  project           = var.project
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  alb_sg_id         = module.security.alb_sg_id
  target_port       = var.container_port
  health_check_path = var.health_check_path
}

module "ecs" {
  source               = "./modules/ecs"
  project              = var.project
  cluster_name         = "${var.project}-cluster"
  private_subnet_ids   = module.network.private_subnet_ids
  ecs_task_sg_id       = module.security.ecs_task_sg_id
  alb_target_group_arn = module.alb.target_group_arn
  container_image      = var.container_image
  container_port       = var.container_port
  desired_count        = var.desired_count
  assign_public_ip     = false
  db_secret_arn        = module.secrets.db_secret_arn
  aws_region           = var.aws_region
}

# Wire SG dependencies: allow only ALB -> ECS (port 8080), ECS -> RDS (5432)
resource "aws_security_group_rule" "alb_to_ecs" {
  type                     = "ingress"
  from_port                = var.container_port
  to_port                  = var.container_port
  protocol                 = "tcp"
  security_group_id        = module.security.ecs_task_sg_id
  source_security_group_id = module.security.alb_sg_id
}

resource "aws_security_group_rule" "ecs_to_rds" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = module.security.rds_sg_id
  source_security_group_id = module.security.ecs_task_sg_id
}

# --- Bastion Security Group ---
resource "aws_security_group" "bastion" {
  name        = "${var.project}-bastion-sg"
  description = "Bastion host SG"
  vpc_id      = module.network.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group_rule" "allow_bastion_to_rds" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.bastion.id
  security_group_id        = module.security.rds_sg_id
}

# --- IAM Role for SSM ---
data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "bastion_ssm" {
  name               = "${var.project}-bastion-ssm-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

resource "aws_iam_role_policy_attachment" "bastion_ssm_attach" {
  role       = aws_iam_role.bastion_ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "bastion_ssm_profile" {
  name = "${var.project}-bastion-ssm-profile"
  role = aws_iam_role.bastion_ssm.name
}

# --- EC2 Instance ---
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.amazon_linux_2.id
  instance_type               = var.bastion_instance_type
  subnet_id                   = coalesce(var.bastion_subnet_id, element(module.network.private_subnet_ids, 0))
  vpc_security_group_ids      = [aws_security_group.bastion.id]
  iam_instance_profile        = aws_iam_instance_profile.bastion_ssm_profile.name
  associate_public_ip_address = false
  key_name                    = var.bastion_key_name

  tags = {
    Name = "${var.project}-bastion"
  }
}
