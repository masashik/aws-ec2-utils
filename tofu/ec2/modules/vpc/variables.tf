variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
}

variable "public_subnet_cidr" {
  type        = string
  description = "CIDR block for the public subnet"
}

variable "az" {
  type        = string
  description = "Availability zone for the public subnet"
}

variable "name_prefix" {
  type        = string
  description = "Prefix to name VPC resources"
}

variable "admin_cidr" {
  description = "Admin source IP for restricted ports"
  type        = string
  default     = "0.0.0.0/0" # Please update this to your IP/32 later.
}

variable "llm_api_cidr" {
  description = "CIDR blocks allowed to access the llm-api server (8000)"
  type        = list(string)
  default     = ["0.0.0.0/0"] # open to public, but it can be updated to var.admin_cidr
}

variable "expose_ollama_pub" {
  description = "Whether to allow external access to Ollama (11434). Default=false"
  type        = bool
  default     = false
}
