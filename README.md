# AWS EC2 Infrastructure Automation Toolkit

![CI Status](https://github.com/masashik/aws-ec2-utils/actions/workflows/ci.yml/badge.svg)

This project provides a fully automated infrastructure setup for experimental cloud environments using **OpenTofu**, **Ansible**, and a **Python-based CLI (Boto3)**. It is designed to eliminate the repetitive and error-prone process of manually provisioning and maintaining cloud infrastructure for testing and development.

---

## 🔧 Problems Addressed

Many developers face friction when experimenting in the cloud:

- Provisioning VPCs, subnets, route tables, and EC2 instances is time-consuming.
- Environments frequently become inconsistent or unhealthy, interrupting work.
- Maintaining SSH keys, inventory files, and security group settings adds complexity.

---

## ✅ Solution Overview

This toolkit automates the full lifecycle:

- **OpenTofu**: Infrastructure provisioning and state management.
- **Ansible**: App-level configuration management across EC2 hosts.
- **Python CLI (Boto3)**: Operational control (start, stop, terminate, status).
- **Ollama LLM** (optional): Self-healing and automated troubleshooting via local inference.

---

## 📐 Architecture

![Diagram](https://github.com/user-attachments/assets/401ebe1e-abb1-47fc-9dd4-dce1138d7506)

---

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

### Step 2: Provision Infrastructure with OpenTofu

```bash
cd tofu
tofu init
tofu apply \
  -var="ami=ami-0f9cb75652314425a" \
  -var="instance_count=2" \
  -var="instance_type=t2.micro" \
  -var="key_name=your-key-name" \
  -auto-approve
```

> 💡 Note: Make sure the AMI ID is valid in your AWS region.

To tear down:
```bash
tofu destroy
```

---

### Step 3: Generate Ansible Inventory
```bash
cd ../scripts
bash gen_inventory.sh
cat ../ansible/inventory.ini
```

---

### Step 4: Run Configuration with Ansible
```bash
cd ../ansible
ansible-playbook -i inventory.ini site.yaml
```

---

### Step 5: Use the CLI to Manage EC2 Instances

Install dependencies and CLI:
```bash
cd ..
pip3 install -r requirements.txt
pip3 install .
```

Sample usage:
```bash
ec2-start --region ca-central-1 --tag-key env --tag-value dev
```

---

## 🛡️ Self-Healing Workflow (Optional)

This project includes a prototype of a self-healing automation system using GitHub Actions and local LLM inference (via Ollama):

1. `workflow_orchestrator.py` runs every 15 minutes via cron.
2. `healthcheck.py` assesses EC2 health status.
3. `llm_consult.py` interprets issues using an LLM.
4. `apply_remediation.py` performs actions (e.g., restarts).

![Self-Healing](https://github.com/user-attachments/assets/1b430fa8-2335-4223-810b-c84c55fed9ff)

---

## ✨ Features

- End-to-end IaC setup for AWS EC2 dev environments
- Zero-touch provisioning with OpenTofu
- Post-provision configuration with Ansible
- Python CLI tools for EC2 operations (start/stop/status/terminate)
- Auto-shutdown idle EC2s via GitHub Actions (default: 6h uptime)
- Inventory auto-generation on provisioning
- CI pipeline with lint/test checks via GitHub Actions

---

## 📦 Version

**v1.0.0 – Stable**

---

## 📄 License

MIT — see [LICENSE](./LICENSE)

---

## 👤 Maintainer

[masashik](https://github.com/masashik)

---

## 🛠️ Upcoming Features
- v1.1.0: ECS Fargate deployment with Docker & GitHub Actions
- v1.2.0: Kubernetes-based deployment with EKS & LLM inference
- Follow the repo for updates!
