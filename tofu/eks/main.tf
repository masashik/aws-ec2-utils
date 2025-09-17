locals {
  tags = {
    Project     = var.project
    Environment = "dev"
  }
}

# 1) VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "${var.project}-vpc"
  cidr = var.vpc_cidr

  azs             = var.azs
  public_subnets  = var.public_subnet_cidrs
  private_subnets = var.private_subnet_cidrs

  enable_nat_gateway = true
  single_nat_gateway = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }
  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"          = "1"
  }

  tags = local.tags
}

# Identify the IAM principal running Terraform
data "aws_caller_identity" "current" {}

# Grant cluster access to that principal
resource "aws_eks_access_entry" "me" {
  cluster_name   = module.eks.cluster_name
  principal_arn  = data.aws_caller_identity.current.arn
  type           = "STANDARD"
  # Optional: keep this so kubectl works even without the policy association
  #kubernetes_groups = ["system:masters"]

  depends_on = [module.eks]
}

# Associate the built-in ClusterAdmin access policy
resource "aws_eks_access_policy_association" "me_admin" {
  cluster_name  = module.eks.cluster_name
  principal_arn = data.aws_caller_identity.current.arn

  policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"  # full-cluster admin
  }

  depends_on = [aws_eks_access_entry.me]
}

#module "aws_auth" {
#  source  = "terraform-aws-modules/eks/aws//modules/aws-auth"
#  version = "~> 20.12"
#
#  cluster_name = module.eks.cluster_name
#
#  # 実行主体が "ユーザー" の場合
#  map_users = [{
#    userarn  = data.aws_caller_identity.current.arn
#    username = "admin"
#    groups   = ["system:masters"]
#  }]
#
#  # 実行主体が "ロール(assumed-role)" の場合は上ではなくこちらを使う:
#  # map_roles = [{
#  #   rolearn  = data.aws_caller_identity.current.arn
#  #   username = "admin"
#  #   groups   = ["system:masters"]
#  # }]
#}

# 2) EKS (managed nodegroup, AL2023 / Bottlerocket)
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.12"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = var.public_access_cidrs

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      ami_type        = var.node_ami_family == "BOTTLEROCKET" ? "BOTTLEROCKET_x86_64" : "AL2023_x86_64_STANDARD"
      instance_types  = var.node_instance_types
      min_size        = var.node_min_size
      max_size        = var.node_max_size
      desired_size    = var.node_desired_size
      capacity_type   = var.capacity_type # SPOT or ON_DEMAND
      labels          = { workload = "general" }
      taints          = []
      tags            = local.tags
    }
  }

  enable_irsa = true
  tags        = local.tags
}

# 3) ECR for your API image
resource "aws_ecr_repository" "api" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  encryption_configuration { encryption_type = "AES256" }
  tags = local.tags
}

# 4) IRSA + IAM for AWS Load Balancer Controller
module "lb_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.39"

  role_name = "${var.project}-lb-controller"

  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }

  tags = local.tags
}

# 5) Helm: AWS Load Balancer Controller (uses existing SA via IRSA)
resource "kubernetes_service_account" "aws_lb_controller" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "aws-load-balancer-controller"
    namespace = "kube-system"
    annotations = {
      "eks.amazonaws.com/role-arn" = module.lb_irsa.iam_role_arn
    }
    labels = { "app.kubernetes.io/component" = "controller" }
  }
  depends_on = [ module.eks, aws_eks_access_entry.me, aws_eks_access_policy_association.me_admin ]
}

resource "helm_release" "aws_load_balancer_controller" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  name       = "aws-load-balancer-controller"
  namespace  = "kube-system"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = "1.10.1" # pick a current version compatible with your EKS

  # Reuse the existing SA (don't let Helm create one)
  set {
    name  = "serviceAccount.create"
    value = "false"
  }

  # set {
  #   name = "serviceAccount.create"
  #   value = "true"
  # }

  set {
    name = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }
  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.lb_irsa.iam_role_arn
  }
  set {
    name  = "serviceAccount.name"
    value = kubernetes_service_account.aws_lb_controller[0].metadata[0].name
  }
  set {
    name  = "clusterName"
    value = module.eks.cluster_name
  }
  set {
    name  = "region"
    value = var.aws_region
  }
  set {
    name  = "vpcId"
    value = module.vpc.vpc_id
  }

  depends_on = [module.eks, aws_eks_access_entry.me, aws_eks_access_policy_association.me_admin]
}

# 6) K8s: namespace
resource "kubernetes_namespace" "llm" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata { name = var.k8s_namespace }
  depends_on = [module.eks, aws_eks_access_entry.me, aws_eks_access_policy_association.me_admin]
}


# 7) K8s: Secrets / ConfigMap
resource "kubernetes_secret" "llm_secrets" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "llm-secrets"
    namespace = kubernetes_namespace.llm[0].metadata[0].name
  }
  data = {
    OPENAI_API_KEY = var.openai_api_key
  }
  type = "Opaque"
}

resource "kubernetes_config_map" "llm_config" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "llm-config"
    namespace = kubernetes_namespace.llm[0].metadata[0].name
  }
  data = {
    OLLAMA_API_URL = "http://ollama:11434/api/generate"
    OLLAMA_MODEL   = var.ollama_model
  }
}

# 8) K8s: Ollama (Deployment + Service)
resource "kubernetes_deployment" "ollama" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "ollama"
    namespace = kubernetes_namespace.llm[0].metadata[0].name
    labels    = { app = "ollama" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "ollama" } }
    template {
      metadata { labels = { app = "ollama" } }
      spec {
        container {
          name  = "ollama"
          image = "ollama/ollama:latest"
          port { container_port = 11434 }
          env {
            name  = "OLLAMA_KEEP_ALIVE"
            value = var.ollama_keep_alive
          }
          env {
            name  = "MODEL_NAME"
            value = var.ollama_model
          }
          resources {
            requests = {
              cpu    = var.ollama_resources.requests_cpu
              memory = var.ollama_resources.requests_memory
            }
            limits = {
              cpu    = var.ollama_resources.limits_cpu
              memory = var.ollama_resources.limits_memory
            }
          }
          lifecycle {
            post_start {
              exec {
                command = ["/bin/sh", "-lc", "sleep 2; ollama pull \"${var.ollama_model}\" || true"]
              }
            }
          }
          liveness_probe {
            http_get {
              path = "/"
              port = 11434
            }
            initial_delay_seconds = 10
            period_seconds        = 20
          }
          readiness_probe {
            http_get {
              path = "/"
              port = 11434
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
          volume_mount {
            name       = "ollama-data"
            mount_path = "/root/.ollama"
          }
        }
        volume {
          name = "ollama-data"
          empty_dir {}
        }
      }
    }
  }
}

resource "kubernetes_service" "ollama" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "ollama"
    namespace = kubernetes_namespace.llm[0].metadata[0].name
  }
  spec {
    selector = { app = "ollama" }
    port {
      name        = "http"
      port        = 11434
      target_port = 11434
    }
    type = "ClusterIP"
  }
}

# 9) K8s: LLM API (Deployment + Service)
resource "kubernetes_deployment" "llm_server" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "llm-server"
    namespace = kubernetes_namespace.llm[0].metadata[0].name
    labels    = { app = "llm-server" }
  }
  spec {
    replicas = var.llm_server_replicas
    selector { match_labels = { app = "llm-server" } }
    template {
      metadata {
        labels = { app = "llm-server" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/path"   = "/metrics"
          "prometheus.io/port"   = "8000"
        }
      }
      spec {
        container {
          name  = "app"
          image = "${aws_ecr_repository.api.repository_url}:${var.llm_server_image_tag}"
          port  { container_port = 8000 }

          env {
            name = "OPENAI_API_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.llm_secrets[0].metadata[0].name
                key  = "OPENAI_API_KEY"
              }
            }
          }
          env {
            name = "OLLAMA_API_URL"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.llm_config[0].metadata[0].name
                key  = "OLLAMA_API_URL"
              }
            }
          }
          env {
            name = "OLLAMA_MODEL"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.llm_config[0].metadata[0].name
                key  = "OLLAMA_MODEL"
              }
            }
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 10
            period_seconds        = 20
          }
          resources {
            requests = {
              cpu = "250m",
              memory = "512Mi"
            }
            limits   = {
              cpu = "1",
              memory = "1Gi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "llm_server" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "llm-server"
    namespace = kubernetes_namespace.llm[0].metadata[0].name
  }
  spec {
    selector = { app = "llm-server" }
    port {
      name        = "http"
      port        = 80
      target_port = 8000
    }
    type = "ClusterIP"
  }
}

# 10) K8s: ALB Ingress (L7, internet-facing, pod IP targets)
resource "kubernetes_ingress_v1" "llm_server" {
  count = try(tobool(var.enable_k8s_phase), false) ? 1 : 0
  metadata {
    name      = "llm-server"
    namespace = kubernetes_namespace.llm[0].metadata[0].name
    annotations = {
      "kubernetes.io/ingress.class"              = "alb"
      "alb.ingress.kubernetes.io/scheme"         = "internet-facing"
      "alb.ingress.kubernetes.io/target-type"    = "ip"
      "alb.ingress.kubernetes.io/healthcheck-path" = "/health"
    }
  }
  spec {
    rule {
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.llm_server[0].metadata[0].name
              port { number = 80 }
            }
          }
        }
      }
    }
  }
  depends_on = [helm_release.aws_load_balancer_controller]
}
