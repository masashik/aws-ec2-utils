# AWS EC2/ECS Infrastructure Automation Toolkit

![CI Status](https://github.com/masashik/aws-ec2-utils/actions/workflows/ci.yml/badge.svg)
![GitHub release (latest by semver)](https://img.shields.io/github/v/release/masashik/aws-ec2-utils)
![GitHub](https://img.shields.io/github/license/masashik/aws-ec2-utils)
![GitHub issues](https://img.shields.io/github/issues/masashik/aws-ec2-utils)
[![codecov](https://codecov.io/gh/masashik/aws-ec2-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/masashik/aws-ec2-utils)

Automated provisioning and deployment of Java-based microservices on AWS ECS (Fargate) or EC2 — user-selectable at deploy time.

| Mode              | Best For                                   | Infra                                            | Scaling   | Cost                    | Notes                 |
| ----------------- | ------------------------------------------ | ------------------------------------------------ | --------- | ----------------------- | --------------------- |
| **EC2**           | Low-level VM management & SSH experiments  | EC2 instances                          | Manual    | Pay for instance uptime | Full OS control       |
| **ECS (Fargate)** | Modern, serverless container orchestration | ECS Cluster, Service, Task Definitions, ALB, RDS, Secret Manager | Automatic | Pay per task runtime    | No server maintenance |

It enables **automated deployment and scaling of a containerized Java microservice with a PostgreSQL backend on AWS ECS and EC2**. 
By combining **Terraform (OpenTofu)** for infrastructure provisioning, **Ansible** for application configuration, and a custom **Python CLI (Boto3)** for EC2 operations, this toolkit offers a fully reproducible cloud environment for developers building and testing backend services.

With this setup, users can

- Provision multiple EC2 instances on-demand using a single Terraform command.
- Deploy the same containerized Java REST API to multiple EC2 nodes using Ansible.
- Access the deployed microservices via public IPs and verify database-backed API responses from each server.
- Instantly start, stop, or destroy environments with a simple CLI command.
- ✅ Verified: All EC2 instances successfully return PostgreSQL data via REST API calls. Infrastructure is ready for Java-based backend development experiments.


---

## 🔧 Problems Addressed

Many developers face friction when experimenting in the cloud:

- Provisioning VPCs, subnets, route tables, and EC2 instances is time-consuming.
- Environments frequently become inconsistent or unhealthy, interrupting work.
- Maintaining SSH keys, inventory files, and security group settings adds complexity.
- Scaling out testing environments is slow and fragile.
- Developers lack reproducible sandboxes for backend experiments.

---

## Solution Overview

This toolkit automates the full lifecycle:

- **OpenTofu**: Infrastructure provisioning and state management.
- **Ansible**: App-level configuration management across EC2 hosts.
- **Python CLI (Boto3)**: Operational control (start, stop, terminate, status).
- **Ollama LLM** (optional): Self-healing and automated troubleshooting via local inference.
- **RESTful Java DB backed microservice**: A simple CRUD Java microservice and exposed DB data over REST endpoint.
  - A zero-touch, reproducible dev environment for Java REST API development.
  - Full lifecycle automation: from provisioning to deployment to operation.
  - Support for infrastructure validation, CI testing, and optional self-healing workflows.
- **ECS Fargate**: Terraform provisions ECS cluster, services, ALB, and RDS. Docker images are pushed to ECR, then deployed without managing EC2 hosts.

## 📐 Architecture (EC2)
<img width="949" height="704" alt="Screenshot 2025-08-05 at 1 05 40 PM" src="https://github.com/user-attachments/assets/87ab7a83-0191-4095-9c2d-dd24736bcd24" />

## 📐 Architecture (ECS)

<img width="964" height="675" alt="aws-ecs-utils-arch" src="https://github.com/user-attachments/assets/534e1e98-a6b5-4190-85e0-996880594531" />

## 🧩 Use Cases

| Icon | Scenario | Description |
|------|----------|-------------|
| 🧪 | Backend Development Sandbox | Easily deploy a Java-based CRUD microservice with PostgreSQL on EC2 for prototyping and testing REST APIs. |
| 🛠️ | DevOps Automation Practice | Hands-on experience integrating Terraform and Ansible to provision and configure scalable infrastructure. |
| 🔁 | CI/CD Demonstration | Use GitHub Actions for automated linting, testing, and pipeline validation with Ansible and Python. |
| 🧠 | LLM-Based Self-Healing Infrastructure | Simulate a self-healing architecture using LLMs (e.g., Ollama/OpenAI) for automated incident remediation. |
| ☁️ | Cloud Infrastructure Learning | End-to-end reproducible AWS infrastructure including VPC, security groups, EC2, and IAM roles. |
| 🔧 | Infrastructure as Code Showcase | Demonstrates clean IaC practices with modular Terraform and declarative Ansible playbooks. |
| 🚀 | Scalable Microservice Deployment | Deploy containerized Java microservices and PostgreSQL DBs across multiple EC2 instances. |
| 👨‍💻 | Job Portfolio Project | High-quality, production-grade DevOps project ready to present to employers for SRE/Platform roles. |

## Samples

```bash
$ curl -X 'GET' 'http<EC2_PUBLIC_IP>:8080/v1/organization/d898a142-de44-466c-8c88-9ceb2c2429d3/license/f2a9c9d4-d2c0-44fa-97fe-724d77173c62' -H 'accept: application/json' | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   729    0   729    0     0    579      0 --:--:--  0:00:01 --:--:--   579
{
  "licenseId": "f2a9c9d4-d2c0-44fa-97fe-724d77173c62",
  "description": "Software Product",
  "organizationId": "d898a142-de44-466c-8c88-9ceb2c2429d3",
  "productName": "Ostock",
  "licenseType": "complete",
  "comment": "I AM DEV",
  "_links": {
    "self": {
      "href": "http://<EC2_PUBLIC_IP>:8080/v1/organization/d898a142-de44-466c-8c88-9ceb2c2429d3/license/f2a9c9d4-d2c0-44fa-97fe-724d77173c62"
    },
    "createLicense": {
      "href": "http://<EC2_PUBLIC_IP>:8080/v1/organization/{organizationId}/license",
      "templated": true
    },
    "updateLicense": {
      "href": "http://<EC2_PUBLIC_IP>:8080/v1/organization/{organizationId}/license",
      "templated": true
    },
    "deleteLicense": {
      "href": "http://<EC2_PUBLIC_IP>:8080/v1/organization/{organizationId}/license/f2a9c9d4-d2c0-44fa-97fe-724d77173c62",
      "templated": true
    }
  }
}
```

## ⚙️ Prerequisites

1. An AWS account with access credentials configured:
```bash
# ~/.aws/config
[default]
region = ca-central-1
output = json

# ~/.aws/credentials
[default]
aws_access_key_id = YOUR_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```

2. Export your EC2 SSH key name:
```bash
export AWS_EC2_SSH_KEY_NAME=your-key-name.pem
```

3. (Optional) Export your OpenAI API Key:
```bash
export OPENAI_API_KEY=sk-...
```

---

## 🧰 Installation

### 1. Install Toolchain

Install [OpenTofu](https://opentofu.org/docs/intro/install/):
```bash
brew update && brew install opentofu
```

Install [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/):
```bash
brew update && brew install ansible
```

Install Python 3 and pip:
```bash
brew update && brew install python3
```

---
## Try in 5 minutes for ECS (EC2 follows)

#### 0) Prereqs: AWS CLI is authenticated; region is set (e.g., ca-central-1)

#### 1) Clone & enter
```
git clone https://github.com/masashik/aws-ec2-utils
cd aws-ec2-utils
```

#### 2) Initialize ECS IaC (S3+DynamoDB backend, if configured)
```
cd tofu/ecs
tofu init -reconfigure -backend-config=../backend/ecs.hcl
```

#### 3) Plan & apply
```
tofu plan
tofu apply -auto-approve
```

Verify it’s live:

#### Get an ALB DNS name (pick the first if multiple)
```
ALB_DNS=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[0].DNSName' --output text)
echo "ALB: http://$ALB_DNS"
```

#### Target health should show "healthy"
```
TG_ARN=$(aws elbv2 describe-target-groups --query 'TargetGroups[0].TargetGroupArn' --output text)
aws elbv2 describe-target-health --target-group-arn "$TG_ARN" --query 'TargetHealthDescriptions[].TargetHealth.State'
```

#### ECS service rollout should be COMPLETED
```
CLUSTER_ARN=$(aws ecs list-clusters --query 'clusterArns[0]' --output text)
SERVICE_ARN=$(aws ecs list-services --cluster "$CLUSTER_ARN" --query 'serviceArns[0]' --output text)
aws ecs describe-services --cluster "$CLUSTER_ARN" --services "$SERVICE_ARN" \
  --query 'services[0].{running:runningCount,desired:desiredCount,rollout:deployments[0].rolloutState}'
```

## 🚀 Quick Start

### Step 1: Clone the Repository
```bash
git clone https://github.com/masashik/aws-ec2-utils
cd aws-ec2-utils
```

Ensure key files are present:
- `tofu/`, `ansible/`, `ec2_utils/`, `scripts/`
- `setup.py`, `requirements.txt`

---
### Step 2: Choose Provision Infrastructure in EC2 or ECS
```bash
cd tofu
ls
ec2 ecs
```
For ec2,
```
cd ec2
tofu init
tofu apply \
  -var="ami=ami-0f9cb75652314425a" \
  -var="instance_count=2" \
  -var="instance_type=t2.micro" \
  -var="key_name=your-key-name" \
  -auto-approve
```

For ecs,
```
cd ecs
tofu init
tofu apply
```

> ⚠️ Note: Make sure the AMI ID is valid in your AWS region.
>  This AMI (ami-0f9cb75652314425a) corresponds to Amazon Linux 2 in ca-central-1.
> Please replace it with a valid AMI ID in your AWS region if needed.


To tear down:
```bash
tofu destroy
```

## 💸 Cost & Cleanup

AWS resources incur charges while they exist. Notable cost drivers in this project include ALB (billed hourly + LCUs), RDS (Postgres), ECS tasks, ECR storage, Secrets Manager, and S3. ALB cannot be “stopped”—only deleted—so don’t leave stacks running unintentionally.

Tear down ECS stack:
```
cd tofu/ecs
tofu destroy -auto-approve
```
If you also created the EC2 stack:
```
cd ../ecs
tofu destroy -auto-approve
```
Optional cleanups:

```
# Remove ECR images if you pushed any
aws ecr describe-repositories --query 'repositories[].repositoryName' --output text
# Example:
# aws ecr batch-delete-image --repository-name <name> --image-ids imageTag=latest
```

Important:
If you imported an existing Secrets Manager secret (e.g., aws-ec2-utils/db) and you don’t want destroy to delete it, make the module “read-only” (create_secret = false) or remove the secret resource from the stack before destroy.
Do not destroy your state backend (S3 bucket / DynamoDB lock table) if it’s shared by other environments.

---

### Step 3: Generate Ansible Inventory (Only for EC2)
```bash
cd ../scripts
bash gen_inventory.sh
cat ../ansible/inventory.ini
```

---

### Step 4: Run Configuration with Ansible (Only for EC2)
```bash
cd ../ansible
ansible-playbook -i inventory.ini site.yaml
```

---

### Step 5: Use the CLI to Manage EC2 Instances (Only for EC2)

Install dependencies and CLI:
```bash
cd ..
pip3 install -r requirements.txt
pip3 install .
```
> ⚠️ Note: The requirements include boto3, click, and other utility packages used by the Python CLI.

Sample usage:
```bash
~$ ec2-start --region ca-central-1
2025-07-30 18:38:07,920 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2025-07-30 18:38:09,177 - INFO - Started ['i-07ed02df9f569d9ec', 'i-06a6e170d5ce8bebd']

~$ec2-stop --region ca-central-1
2025-07-30 18:38:48,082 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2025-07-30 18:38:48,906 - INFO - Stopped ['i-07ed02df9f569d9ec', 'i-06a6e170d5ce8bebd']

~$ ec2-remove --region ca-central-1
2025-07-30 18:39:35,275 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
Terminating…
2025-07-30 18:39:36,624 - INFO - Terminated ['i-07ed02df9f569d9ec', 'i-06a6e170d5ce8bebd']

~$ ec2-status --region ca-central-1
INFO: Found credentials in shared credentials file: ~/.aws/credentials
[TERMINATED] i-07ed02df9f569d9ec dev-server (t2.micro) launched at 2025-07-30 22:38:09+00:00
[TERMINATED] i-06a6e170d5ce8bebd dev-server (t2.micro) launched at 2025-07-30 22:38:09+00:00

~$ ec2-remove (no region and tag is provided)
usage: ec2-remove [-h] --region REGION [--tag-key TAG_KEY] [--tag-value TAG_VALUE] [--dry-run] [--log-file LOG_FILE] [--verbose]
ec2-remove: error: the following arguments are required: --region

```
> ⚠️ Note: The ec2-start and related commands are installed via setup.py using entry_points, making them available globally after installation.


---

## 🛡️ Self-Healing Workflow (Optional)

[This project](https://github.com/masashik/aws-ec2-utils/issues/29) includes a prototype of a self-healing automation system using GitHub Actions and local LLM inference (via Ollama):



1. `workflow_orchestrator.py` runs every 15 minutes via cron.
2. `healthcheck.py` assesses EC2 health status.
3. `llm_consult.py` interprets issues using an LLM.
4. `apply_remediation.py` performs actions (e.g., restarts).

![Self-Healing](https://github.com/user-attachments/assets/1b430fa8-2335-4223-810b-c84c55fed9ff)

> ⚠️ Note: To use the self-healing features, ensure Ollama is installed locally and your model is available. More setup details will be provided in a future release.

---

## ✨ Features

- End-to-end IaC setup for AWS EC2 dev environments
- Zero-touch provisioning with OpenTofu
- Post-provision configuration with Ansible
- Python CLI tools for EC2 operations (start/stop/status/terminate)
- Auto-shutdown idle EC2s via GitHub Actions (default: 6h uptime)
- Inventory auto-generation on provisioning
- CI pipeline with lint/test checks via GitHub Actions
- Terraform-provisioned ECS Cluster, ALB, and RDS
- ECR integration for container image deployment
- Serverless scaling with Fargate — no instance maintenance


---

## 📦 Version

**v1.0.0 – Stable**
**v1.1.0: ECS Fargate deployment with Docker & GitHub Actions**

---

## 📄 License

MIT — see [LICENSE](./LICENSE)

---

## 👤 Maintainer

[masashik](https://github.com/masashik)

---

## 🛠️ Upcoming Features
- v1.2.0: Kubernetes-based deployment with EKS & LLM inference
- Follow the repo for updates!

## 🧭 EC2 → ECS → EKS Roadmap
This toolkit began with EC2 for low-level control (SSH, OS-level experiments), then advanced to ECS Fargate for serverless container orchestration (no instance management, ALB + Secrets Manager + RDS). The next step is EKS to run multiple services with Kubernetes primitives (managed node groups, autoscaling, IAM Roles for Service Accounts, external secrets, and an ALB Ingress Controller), plus a standard observability stack (Prometheus/Grafana) and progressive delivery via GitHub Actions. The goal: a reproducible path from VM-based prototypes → ECS workloads → production-ready EKS with the same app, image, and CI flow.
