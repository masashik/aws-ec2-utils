# Automated deployment of LLM Inference API on AWS EC2 with full observability (Prometheus/Grafana) and backend switching (Ollama ↔ OpenAI)

[![Auto Shutdown EC2](https://github.com/masashik/aws-ec2-utils/actions/workflows/auto_shutdown.yml/badge.svg)](https://github.com/masashik/aws-ec2-utils/actions/workflows/auto_shutdown.yml)
[![IaC Plan (safe)](https://github.com/masashik/aws-ec2-utils/actions/workflows/iac-plan.yml/badge.svg)](https://github.com/masashik/aws-ec2-utils/actions/workflows/iac-plan.yml)
[![IaC Apply (manual)](https://github.com/masashik/aws-ec2-utils/actions/workflows/iac-apply.yml/badge.svg)](https://github.com/masashik/aws-ec2-utils/actions/workflows/iac-apply.yml)
![CI Status](https://github.com/masashik/aws-ec2-utils/actions/workflows/ci.yml/badge.svg)
![GitHub release (latest by semver)](https://img.shields.io/github/v/release/masashik/aws-ec2-utils)
![GitHub](https://img.shields.io/github/license/masashik/aws-ec2-utils)
![GitHub issues](https://img.shields.io/github/issues/masashik/aws-ec2-utils)
[![codecov](https://codecov.io/gh/masashik/aws-ec2-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/masashik/aws-ec2-utils)


<img width="1176" height="669" alt="LLM Inference API on AWS EC2 with full observability and CICD" src="https://github.com/user-attachments/assets/fb2023ba-c49c-4d01-ab45-f0cbf2ff2667" />

# Quick Start

```bash
# Provisioning infrastructure
ADMIN_IP="$(curl -fsS https://checkip.amazonaws.com || curl -fsS https://ifconfig.me)"
tofu apply \
  -var="ami=ami-0f9cb75652314425a" \
  -var="instance_count=1" \
  -var="instance_type=t2.xlarge" \
  -var="key_name=aws-canada-backend-1" \
  -var="admin_cidr=${ADMIN_IP}/32" \
  -auto-approve

# Updating and instsalling software components
ansible-playbook -i ansible/inventory.ini ansible/deploy_llm_stack.yml

# Ollama response
curl -s -X POST http://<EC2 Public IP>:8000/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from EC2!","backend":"ollama","model":"llama3.1:8b"}' | jq .

# OpenAI response
curl -s -X POST http://<EC2 Public IP>:8000/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Ping from EC2","backend":"openai","model":"gpt-4o-mini"}' | jq .
```


Automated provisioning and deployment of Java-based microservices on AWS ECS (Fargate) or EC2 — user-selectable at deploy time.

| Mode              | Best For                                   | Infra                                            | Scaling   | Cost                    | Notes                 |
| ----------------- | ------------------------------------------ | ------------------------------------------------ | --------- | ----------------------- | --------------------- |
| **EC2**           | Low-level VM management & SSH experiments  | EC2 instances                          | Manual    | Pay for instance uptime | Full OS control       |
| **ECS (Fargate)** | Modern, serverless container orchestration | ECS Cluster, Service, Task Definitions, ALB, RDS, Secrets Manager | Automatic | Pay per task runtime    | No server maintenance |

It enables **automated deployment and scaling of a containerized Java microservice with a PostgreSQL backend on AWS ECS and EC2**. 
By combining **OpenTofu (Terraform-compatible)** for infrastructure provisioning, **Ansible** for application configuration, and a custom **Python CLI (Boto3)** for EC2 operations, this toolkit offers a fully reproducible cloud environment for developers building and testing backend services.

With this setup, users can

- Provision multiple EC2 instances on-demand using a single OpenTofu command.
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
- **RESTful Java DB-backed microservice**: A simple CRUD Java microservice and exposed DB data over REST endpoint.
  - A zero-touch, reproducible dev environment for Java REST API development.
  - Full lifecycle automation: from provisioning to deployment to operation.
  - Support for infrastructure validation, CI testing, and optional self-healing workflows.
- **ECS Fargate**: OpenTofu provisions ECS cluster, services, ALB, and RDS. Docker images are pushed to ECR, then deployed without managing EC2 hosts.


## Quick Selector

- Deploy on ECS → [ECS Route - Steps](#ecs-route--steps)
- Deploy on EC2 → [EC2 Route - Steps](#ec2-route--steps)

## Definition of Done (DoD)

- Fresh deployment completes without manual edits.
- For ECS: service rollout is COMPLETED and ALB endpoint returns HTTP 200.
- For EC2: the instance serves HTTP 200 on the expected endpoint.
- Cleanup instructions lower costs when the environment is idle.

## ECS Route — Steps

### Prerequisites

- CLI tools: AWS CLI, OpenTofu/Terraform, Docker (with Buildx), jq
- AWS permissions for: ECR, ECS, ALB, RDS, Secrets Manager, IAM (for PassRole to task execution role)
- Region: <your-region> (example: ca-central-1)

### Environment Variables (example)
```bash
export AWS_REGION=ca-central-1
export ECR_REGISTRY=<123456789012.dkr.ecr.${AWS_REGION}.amazonaws.com>
export ECR_REPO=<aws-ec2-utils/java-web-data-postgres-db>
export ECS_CLUSTER=<aws-utils-cluster>
export ECS_SERVICE=<aws-utils-ecs-service>
```

### Build & Push Container (if needed)

Multi-arch is useful when your Fargate platform or local dev varies.

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ${ECR_REGISTRY}/${ECR_REPO}:latest \
  --push .
```

### Provision / Update with IaC
```bash
cd <path-to-ecs-iac>   # e.g., tofu/ecs
tofu init
tofu apply -auto-approve
```

### Discover ALB DNS & Smoke Test
```bash
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?contains(LoadBalancerName, 'ecs')].DNSName" \
  --output text --region ${AWS_REGION})

curl -i "http://${ALB_DNS}/v1/organization/<sample-id>/license/" | head -n 20
```

### Service Rollout Check
```bash
aws ecs describe-services \
  --cluster "${ECS_CLUSTER}" --services "${ECS_SERVICE}" \
  --query 'services[0].{running:runningCount,desired:desiredCount,rollout:deployments[0].rolloutState}' \
  --region ${AWS_REGION}
# Expect: {"running":1,"desired":1,"rollout":"COMPLETED"}
```

### Known Pitfalls
- Missing iam:PassRole on the service update prevents new task definitions from running.
- Secrets Manager name/ARN mismatches cause DB connection failures.
- Ensure Buildx is enabled; otherwise multi-arch builds won’t work.

### Cleanup / Cost Controls

```bash
# Pause test traffic to reduce costs
aws ecs update-service \
  --cluster "${ECS_CLUSTER}" --service "${ECS_SERVICE}" \
  --desired-count 0 --region ${AWS_REGION}

# Destroy ephemeral helpers (e.g., bastion) via IaC when not needed
# Review ECR for unused images before the week ends
```

### Cost Management (Daily/Weekly)

- Daily: After validation, set ECS desiredCount=0 for non-production services.
- Weekly: Review Target Groups, unattached EIPs/EBS, and unused ECR images.
- Consider automated cleanup scripts and tagging policies for ephemeral resources.

Important:
If you imported an existing Secrets Manager secret (e.g., aws-ec2-utils/db) and you don’t want destroy to delete it, make the module “read-only” (create_secret = false) or remove the secret resource from the stack before destroy.
Do not destroy your state backend (S3 bucket / DynamoDB lock table) if it’s shared by other environments.


### Changelog (for this split)
- feat(readme): split ECS/EC2 routes with reproducible steps and cost guardrails
- Added example GitHub Actions workflow for ECS CD.

## EC2 Route — Steps

### Prerequisites

- CLI tools: AWS CLI, OpenTofu/Terraform, Ansible
- RDS (PostgreSQL) recommended (can be shared with the ECS route)
- Security Group(s) and Key Pair prepared for EC2 access

### Provision Infra
```bash
cd <path-to-ec2-iac>   # e.g., tofu/ec2
tofu init
tofu apply -auto-approve
```

### Configure & Deploy App (Ansible)
```bash
cd <path-to-ansible>   # e.g., ansible/ec2
ansible-playbook -i inventories/<env>/hosts site.yml
```

### Smoke Test
```bash
curl -i "http://<ec2-public-dns>:8080/v1/organization/<sample-id>/license/" | head -n 20
```

### Cleanup / Cost Controls
```bash
# For test-only environments, tear down to avoid charges
tofu destroy -auto-approve
```

## 📐 Architecture (EC2)
<img width="949" height="704" alt="Screenshot 2025-08-05 at 1 05 40 PM" src="https://github.com/user-attachments/assets/87ab7a83-0191-4095-9c2d-dd24736bcd24" />

## 📐 Architecture (ECS)

<img width="964" height="675" alt="aws-ecs-utils-arch" src="https://github.com/user-attachments/assets/534e1e98-a6b5-4190-85e0-996880594531" />

## 🧩 Use Cases

| Icon | Scenario | Description |
|------|----------|-------------|
| 🧪 | Backend Development Sandbox | Easily deploy a Java-based CRUD microservice with PostgreSQL on EC2 for prototyping and testing REST APIs. |
| 🛠️ | DevOps Automation Practice | Hands-on experience integrating OpenTofu and Ansible to provision and configure scalable infrastructure. |
| 🔁 | CI/CD Demonstration | Use GitHub Actions for automated linting, testing, and pipeline validation with Ansible and Python. |
| 🧠 | LLM-Based Self-Healing Infrastructure | Simulate a self-healing architecture using LLMs (e.g., Ollama/OpenAI) for automated incident remediation. |
| ☁️ | Cloud Infrastructure Learning | End-to-end reproducible AWS infrastructure including VPC, security groups, EC2, and IAM roles. |
| 🔧 | Infrastructure as Code Showcase | Demonstrates clean IaC practices with modular OpenTofu and declarative Ansible playbooks. |
| 🚀 | Scalable Microservice Deployment | Deploy containerized Java microservices and PostgreSQL DBs across multiple EC2 instances. |
| 👨‍💻 | Job Portfolio Project | High-quality, production-grade DevOps project ready to present to employers for SRE/Platform roles. |

## Samples

```bash
$ curl -X 'GET' 'http://<EC2_PUBLIC_IP>:8080/v1/organization/d898a142-de44-466c-8c88-9ceb2c2429d3/license/f2a9c9d4-d2c0-44fa-97fe-724d77173c62' -H 'accept: application/json' | jq
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
export AWS_EC2_SSH_KEY_NAME=your-key-name # key pair name, not the .pem file
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
### Step 2: Choose to provision infrastructure in EC2 or ECS
```bash
# EC2
cd tofu/ec2
tofu init -backend-config=../backend/ec2.hcl
tofu plan -input=false

# ECS
cd ../ecs
tofu init -backend-config=../backend/ecs.hcl
tofu plan -input=false
```

> ⚠️ Note: Make sure the AMI ID is valid in your AWS region.
>  This AMI (ami-0f9cb75652314425a) corresponds to Amazon Linux 2 in ca-central-1.
> Please replace it with a valid AMI ID in your AWS region if needed.


To tear down:
```bash
tofu destroy -input=false
```


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
- OpenTofu-provisioned ECS Cluster, ALB, and RDS
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


## GitHub Actions — ECS Continuous Delivery (Example)

Goal: When code is pushed to main, automatically build & push to ECR and update the ECS service.

#### Required GitHub Secrets / Variables
- AWS_REGION
- AWS_ROLE_ARN (for GitHub OIDC → STS AssumeRole)
- ECR_REGISTRY, ECR_REPO
- ECS_CLUSTER, ECS_SERVICE

#### Trust Policy (AWS IAM Role for OIDC)
- Issuer: token.actions.githubusercontent.com
- Condition: aud=sts.amazonaws.com
- Repo scope condition is recommended (restrict to this repo)

#### Minimal Workflow: .github/workflows/deploy-ecs.yml
```yaml
name: Deploy to ECS
on:
  push:
    branches: ["main"]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION || secrets.AWS_REGION }}

      - name: Login to ECR
        id: ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build & Push Image (multi-arch)
        run: |
          docker buildx create --use || true
          IMAGE="${{ secrets.ECR_REGISTRY }}/${{ secrets.ECR_REPO }}:latest"
          docker buildx build \
            --platform linux/amd64,linux/arm64 \
            -t "$IMAGE" --push .

      - name: Register Task Definition
        run: |
          # Update your task definition JSON with the new image digest if needed
          # Example shows a placeholder; adapt to your environment
          echo "Registering new task definition (placeholder)…"

      - name: Update ECS Service
        run: |
          aws ecs update-service \
            --cluster "${{ secrets.ECS_CLUSTER }}" \
            --service "${{ secrets.ECS_SERVICE }}" \
            --force-new-deployment \
            --region "${{ vars.AWS_REGION || secrets.AWS_REGION }}"

      - name: Wait for Rollout
        run: |
          aws ecs wait services-stable \
            --cluster "${{ secrets.ECS_CLUSTER }}" \
            --services "${{ secrets.ECS_SERVICE }}"
```
