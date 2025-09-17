output "ecr_repo_url" {
  value = aws_ecr_repository.api.repository_url
}

output "alb_dns" {
  description = "ALB DNS for the LLM API"
  # value       = kubernetes_ingress_v1.llm_server.status[0].load_balancer[0].ingress[0].hostname
  value = try(kubernetes_ingress_v1.llm_server[0].status[0].load_balancer[0].ingress[0].hostname, null)
}

output "cluster_version" {
  value = module.eks.cluster_version
}

