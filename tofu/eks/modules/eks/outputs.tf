output "cluster_name" { value = aws_eks_cluster.this.name }
output "cluster_endpoint" { value = aws_eks_cluster.this.endpoint }
output "cluster_ca" { value = aws_eks_cluster.this.certificate_authority[0].data }
output "cluster_security_group_id" {
  value = try(aws_eks_cluster.this.vpc_config[0].cluster_security_group_id, null)
}

# Base64 CA data from the control plane
# Provide BOTH names for compatibility
output "cluster_certificate_authority_data" {
  value = aws_eks_cluster.this.certificate_authority[0].data
}

