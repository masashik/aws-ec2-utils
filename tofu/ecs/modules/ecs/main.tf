resource "aws_ecs_cluster" "this" {
  name = var.cluster_name
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/ecs/${var.project}"
  retention_in_days = 14
}

# IAM roles
resource "aws_iam_role" "task_execution" {
  name               = "${var.project}-task-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
}

data "aws_iam_policy_document" "ecs_tasks_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { type = "Service" identifiers = ["ecs-tasks.amazonaws.com"] }
  }
}

resource "aws_iam_role_policy_attachment" "execution_ecr" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task" {
  name               = "${var.project}-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
}

# Allow reading the DB secret
resource "aws_iam_policy" "read_secret" {
  name   = "${var.project}-read-secret"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = ["secretsmanager:GetSecretValue"],
      Resource = var.db_secret_arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "task_read_secret" {
  role       = aws_iam_role.task.name
  policy_arn = aws_iam_policy.read_secret.arn
}

# Task definition
resource "aws_ecs_task_definition" "this" {
  family                   = "${var.project}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = "app",
      image     = var.container_image,
      essential = true,
      portMappings = [{
        containerPort = var.container_port,
        hostPort      = var.container_port,
        protocol      = "tcp"
      }],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.this.name,
          awslogs-region        = var.project == "" ? "" : null,
          awslogs-stream-prefix = "app"
        }
      },
      secrets = [
        { name = "DB_SECRET_JSON", valueFrom = var.db_secret_arn }
      ],
      environment = [
        { name = "SPRING_DATASOURCE_URL", value = "jdbc:postgresql://${jsondecode(nonsensitive(data.aws_secretsmanager_secret_version.db.secret_string)).host}:5432/${jsondecode(nonsensitive(data.aws_secretsmanager_secret_version.db.secret_string)).dbname}" }
      ]
    }
  ])
}

# Fetch secret at plan time only for template (will not expose at state as valueFrom is used)
data "aws_secretsmanager_secret_version" "db" {
  secret_id = var.db_secret_arn
}

resource "aws_ecs_service" "this" {
  name            = "${var.project}-svc"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_task_sg_id]
    assign_public_ip = var.assign_public_ip
  }

  load_balancer {
    target_group_arn = var.alb_target_group_arn
    container_name   = "app"
    container_port   = var.container_port
  }

  lifecycle { ignore_changes = [task_definition] }
}
