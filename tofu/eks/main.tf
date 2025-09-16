module "network" {
  source               = "./modules/network"
  project              = var.project
  vpc_cidr             = var.vpc_cidr
  azs                  = var.azs
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "eks" {
  source                   = "./modules/eks"
  project                  = var.project
  kubernetes_version       = var.kubernetes_version
  subnet_ids               = module.network.private_subnet_ids
  endpoint_public_access   = var.endpoint_public_access
  endpoint_private_access  = var.endpoint_private_access
  public_access_cidrs      = [var.admin_cidr]
}

module "node_group" {
  source            = "./modules/nodegroup"
  project           = var.project
  cluster_name      = module.eks.cluster_name
  subnet_ids        = module.network.private_subnet_ids
  node_group_name   = var.node_group_name
  instance_types    = var.node_instance_types
  disk_size         = var.node_disk_size
  desired_size      = var.desired_size
  min_size          = var.min_size
  max_size          = var.max_size
}

