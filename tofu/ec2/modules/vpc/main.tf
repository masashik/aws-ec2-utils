resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "${var.name_prefix}-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.name_prefix}-igw"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.az
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.name_prefix}-subnet-public"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.name_prefix}-rt-public"
  }
}

resource "aws_route" "default_route" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_subnet" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "dev_sg" {
  name        = "${var.name_prefix}-sg"
  description = "Allow SSH and HTTP inbound"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # ----- LLM API (FastAPI 8000) -----
  dynamic "ingress" {
    for_each = var.llm_api_cidr //llm_api_cidr = ["0.0.0.0/0"] for opening the Web API to public.
    content {
      from_port   = 8000
      to_port     = 8000
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
      description = "llm-api"
    }
  }

  # ----- Prometheus 9090 / Grafana 3000 limiting to my localhost IP-----
  ingress {
    from_port = 9090
    to_port = 9090
    protocol = "tcp"
    cidr_blocks = [var.admin_cidr]
    description = "prometheus"
  }

  ingress {
    from_port = 3000
    to_port = 3000
    protocol = "tcp"
    cidr_blocks = [var.admin_cidr]
    description = "grafana"
  }

  # ----- Ollama 11434 is private and only ECS tasks can access and SG persmission is provided in B
  # expose_ollama_pub=true
  dynamic "ingress" {
    for_each = var.expose_ollama_pub ? [1] : []
    content {
      from_port   = 11434
      to_port     = 11434
      protocol    = "tcp"
      cidr_blocks = [var.admin_cidr]
      description = "ollama (temporary)"
    }
  }

  # egress open to public.
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.name_prefix}-sg" }
}
