variable "project"               { type = string }
variable "aws_region"            { type = string }
variable "vpc_cidr"              { type = string }
variable "azs"                   { type = list(string) }
variable "public_subnet_cidrs"   { type = list(string) }
variable "private_subnet_cidrs"  { type = list(string) }

variable "cluster_name"          {
  type = string
  default = "llm-eks"
}
variable "cluster_version"       {
  type = string
  default = "1.33"
}

variable "node_instance_types"   {
  type = list(string)
  default = ["t3.large"]
}
variable "node_desired_size"     {
  type = number
  default = 2
}
variable "node_min_size"         {
  type = number
  default = 2
}
variable "node_max_size"         {
  type = number
  default = 4
}
variable "capacity_type"         {
  type = string
  default = "SPOT"
} # "ON_DEMAND" ok too

# AL2023 (recommended) or "BOTTLEROCKET"
variable "node_ami_family"       {
  type = string
  default = "AL2023"
}

# Restrict who can reach the EKS endpoint (must be real CIDRs, not TEST-NET)
variable "public_access_cidrs"   {
  type = list(string)
  default = ["0.0.0.0/0"]
}

# ECR
variable "ecr_repo_name"         {
  type = string
  default = "llm-api-server"
}

# App config
variable "k8s_namespace"         {
  type = string
  default = "llm"
}
variable "ollama_model"          {
  type = string
  default = "llama3.2:3b-instruct-q4_K_M"
}
variable "ollama_keep_alive"     {
  type = string
  default = "10m"
}
variable "ollama_resources" {
  type = object({
    requests_cpu    = string
    requests_memory = string
    limits_cpu      = string
    limits_memory   = string
  })
  default = {
    requests_cpu    = "500m"
    requests_memory = "1Gi"
    limits_cpu      = "2"
    limits_memory   = "4Gi"
  }
}
variable "llm_server_image_tag"  {
  type = string
  default = "v1"
}
variable "llm_server_replicas"   {
  type = number
  default = 2
}
variable "openai_api_key"        {
  type = string
  sensitive = true
}
