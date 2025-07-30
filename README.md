# IaC development infrastructure provisioning in Cloud
![CI](https://github.com/masashik/aws-ec2-utils/actions/workflows/ci.yml/badge.svg)

## Problems

Too much overhead for developers who just want to deploy new application to experiment:tasks like configuring subnets, setting up security groups, and attaching instances to public networks can be time-consuming and error-prone to provision an entire cloud infrastructure — including virtual servers, networking, routing tables, and internet gateways
Even after deployment. Many developers struggle to maintain their experimental environments when infrastructure enters an unhealthy or inconsistent state, it can block their development flow.

## The solution

Ready made development environment setup. This project provides an end-to-end Infrastructure as Code (IaC) for experimental cloud development environments provisioning using OpenTofu, imperative configuration management with Ansible, and Python CLI (with Boto3 SDK)

- OpenTofu - provision the entire infrastructure and keep the state from terraform files.
- Ansible - each or group of software component can be updated defined in inventory YAML files.
- PythonCLI - This CLI directly access to EC2 for controlling the instances like start/stop/status/terminate.
- Ollama (LLM inference) - Providing self-healing mechanisms to resolve common issues like triage too high and too low CPU utilization.

## Prerequisite

- Your AWS accout is created, and you need to download AWS API credentials to your machine.

```bash
~$cat ~/.aws/config 
[default]
region = ca-central-1
output = json

~$cat ~/.aws/credentials 
[default]
aws_access_key_id = YOUR_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```

## This is what you get after successful install, setup, and execution of provisioning scripts.
![Image](https://github.com/user-attachments/assets/401ebe1e-abb1-47fc-9dd4-dce1138d7506)


This is Automated EC2 Infrastructure Provisioning and Configuration Pipeline. It provisions a complete AWS environment:

- Custom VPC, subnets, route tables, and internet gateway
- Multiple EC2 instances deployed with consistent configurations
- Ansible roles to configure and update apps (e.g., NGINX, web apps)

## Let's setup

You need the following toolchain to enable controlling this automated infrastructure provisioning and configuration management.

### 1. Install provisioning tool - OpenTofu
https://opentofu.org/docs/intro/install/
```
brew update
brew install opentofu
```
### 2. Install configuration management tool - Ansible

https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pipx-install
```
brew update
brew install ansible
```
### 3. Install CLI runtime - Python3

https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pipx-install
```
brew update
brew install python3
```

## Usage

Please think the usage like this:


At first, you need a house to host your guests (=software components). Once the house it built, then let's check that bolts and nuts are properly tighten to keep a good condition of the house with Ansible. Then, let's remotely turn on and off the air conditioning and see the current house condtions through the CLI.

### 1. Git clone the project
```bash
git clone https://github.com/masashik/aws-ec2-utils

cd aws-ec2-utils

aws-ec2-utils $ls

Architecture Diagram.drawio          README.md                            build                                prometheus                           tests
Dockerfile                           ansible                              ec2_utils                            requirements.txt                     tofu
Jenkins pipeline architecture.drawio aws-ec2-utils-iac-arch.drawio        llm-infra-automation                 scripts
LICENSE                              aws_ec2_utils.egg-info               llm_server                           setup.py

*Please confirm these files in the cloned project, otherwise delete the project and try cloing again just in case.
```

### 2. Provisioning infrastructure in cloud by OpenTofu (The house)
```bash
cd tofu

$ pwd
aws-ec2-utils/tofu

tofu init

tofu apply -var="ami=ami-0f9cb75652314425a" -var="instance_count=2" -var="instance_type=t2.micro" -var="key_name=your-key-name" -auto-approve
```
*Please choose your OS image for ami (Amazon Machine Image.)

- **ami-0f9cb75652314425a** is the Amazon linux distro.
- **instance_count** is the number of EC2 instances you want.
- **instance_type** is the EC2 instance type you want, and please reference AWS EC2 page for the up-to-date list of available EC2 instance types.
- **key_name** is the asymmetric key to ssh to the EC2 instances.

Upon successful provisioning, you will see the following message in the terminal.
```bash
Apply complete! Resources: 9 added, 0 changed, 0 destroyed.

Outputs:

instance_ips = [
  "35.182.213.206",
  "3.99.169.153",
]

Destroy complete! Resources: 9 destroyed.
```

If you want to just dispose entire environment
```bash
$ pwd
aws-ec2-utils/tofu

tofu destroy

Destroy complete! Resources: 9 destroyed.
```

### 3. Map the output IP addresses to Ansible's inventory file to list the provisioned EC2 instances.
```bash
$ cd aws-ec2-utils/scripts

$ pwd
aws-ec2-utils/scripts

$ bash gen_inventory.sh
[OK] Inventory generated at ansible/inventory.ini

$ cat aws-ec2-utils/ansible/inventory.ini
[dev]
16.52.92.8 ansible_user=ec2-user ansible_ssh_private_key_file=~/.ssh/aws-canada-backend-1.pem
35.183.124.58 ansible_user=ec2-user ansible_ssh_private_key_file=~/.ssh/aws-canada-backend-1.pem
```

### 4. Configuration management with Ansible (Checking the bolts and nuts of the just built house)
```bash
$ cd aws-ec2-utils/ansible

$ pwd
aws-ec2-utils/ansible

ansible-playbook -i inventory.ini site.yaml
```

### 5. Controlling the EC2 instances via CLI (Turn on and off air-conditioning)
```bash
$ cd aws-ec2-utils/

$ ls setup.py
setup.py <-- Make sure that you have this file in the directory of aws-ec2-utils.

*Install dependency python modules.
$ pip3 install -r requirements.txt

* Install the Python CLI
(ec2-start/ec2-stop/ec2-status)

$ pip3 install .

Building wheels for collected packages: aws-ec2-utils
  ...
Successfully built aws-ec2-utils
Installing collected packages: aws-ec2-utils
Successfully installed aws-ec2-utils-0.1.0
```

To verify if the CLI is properly installed and available, run the intalled CLI.

```bash
$ ec2-start

usage: ec2-start [-h] --region REGION [--tag-key TAG_KEY] [--tag-value TAG_VALUE] [--dry-run] [--log-file LOG_FILE] [--verbose] [--state STATE]
                 [--min-uptime-hours MIN_UPTIME_HOURS]
ec2-start: error: the following arguments are required: --region
```
This is successfully installed and ready to use.

## Automated EC2 Monitoring & Self-Healing Workflow

 In addition to provisioning, the project introduces **automated infrastructure maintenance (This is still in progress)**, including:

- **GitHub Actions cron job** (every 15 minutes) to trigger `workflow_orchestrator.py`: orchestrates the health check and remediation process
1. `healthcheck.py` on all EC2 instances
2. `llm_consult.py`: consults a local LLM (Ollama) to interpret issues
3. `apply_remediation.py`: takes automated action like restarting servers if problems are persistent.

### Architecture
![Image](https://github.com/user-attachments/assets/1b430fa8-2335-4223-810b-c84c55fed9ff)

This ensures:
- Less manual maintenance during development
- Immediate resolution of common EC2 issues
- Consistent infrastructure state for all developers
- Seamless environment resets for faster experimentation

## Features availble now
 - Fully coded and automated development infrastructure provisioning from scratch with OpenTofu, Ansible, and Python console CLI.
 - Auto-shutdown idling EC2 instances running more than 6 hours by GitHub Actions to save cost. 6 hours is currently set default time window for allowing experimental development.
 - Incremental configuration update with Ansible.
 - Python CLI utilizing Boto3 to start, shutdown, terminate, and status-checking of EC2 instances.
 - CI enabled with auto syntax checking and testing when new commits made with GitHub Actions.
 - Auto-generating host inventory upon successful EC2 instances provisioning.