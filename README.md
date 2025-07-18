# IaC development infrastructure provisioning in Cloud
![CI](https://github.com/masashik/aws-ec2-utils/actions/workflows/ci.yml/badge.svg)

## A problem to solve

Infrastructure as Code (IaC) - simplifying setting up development infrastructure with EC2, OpenTofu, Ansible, and Python CLI with Boto3 AWS SDK. Running EC2 servers ready accept any application deployment for experiment.

## Architecture of provisioned AWS-EC2-Utils

![Image](https://github.com/user-attachments/assets/9abcae41-3b1c-4663-a9d5-e3e9e6412edc)

## Features
 - Fully coded and automated development infrastructure provisioning from scratch with OpenTofu.
 - Idling EC2 instances shutdown with GitHub Actions to save cost.
 - Incremental configuration update with Ansible.
 - Python CLI utilizing Boto3 to start, shutdown, terminate, and status-checking of EC2 instances.
 - CI enabled with auto syntax checking and testing when new commits made with GitHub Actions.
 - Containerization to isolate runtime dependency.
 - Auto-generating host inventory.

## A role of each tool
 - OpenTofu
    - Provisioning entire development infrastructure in AWS with EC2 instances.
 - Ansible
    - Configuration management of each EC2 instance installing necessary toolchain and imperative and incremental updates.
 - Python CLI
    - Controlling on EC2 instances like start, shutdown, terminate, and status-checking of EC2 instances.

## How-to-setup
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
### 3. Install CLI dev tools - Python3

https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pipx-install
```
brew update
brew install python3
```

## How-to-use
### Provisioning development infrastructure in cloud
```bash
git clone https://github.com/masashik/aws-ec2-utils

cd aws-ec2-utils/terraform

tofu init

tofu apply -var="ami=ami-0f9cb75652314425a" -var="instance_count=2" -var="instance_type=t2.micro" -var="key_name=your-key-name" -auto-approve
```
*Please choose your OS image for ami (Amazon Machine Image.)
*ami-0f9cb75652314425a is Amazon linux distro.

### Python3 CLI with Boto3
```bash
git clone https://github.com/masashik/aws-ec2-utils

cd aws-ec2-utils/

*Install dependency python modules.
pip3 install -r requirements.txt

* Install the Python CLI
(ec2-start/ec2-stop/ec2-status)
pip install .
```

To verify if the CLI is properly installed and available, run the intalled CLI.

```bash
$ ec2-start

usage: ec2-start [-h] --region REGION [--tag-key TAG_KEY] [--tag-value TAG_VALUE] [--dry-run] [--log-file LOG_FILE] [--verbose] [--state STATE]
                 [--min-uptime-hours MIN_UPTIME_HOURS]
ec2-start: error: the following arguments are required: --region

This is successfully installed and ready to use.
```

### Ansible
```bash
git clone https://github.com/masashik/aws-ec2-utils

cd aws-ec2-utils/ansible

ansible-playbook -i inventory.ini site.yaml
```

### Containerized version
```
git clone https://github.com/masashik/aws-ec2-utils

cd aws-ec2-utils

docker build -t aws-ec2-utils .

docker run -v ~/.aws:/root/.aws:ro aws-ec2-utils python3 ec2_metadata.py --region ca-central-1 --tag-key env --tag-value dev --dry-run
```

## Example

### Terraform

```
$ tofu apply -var="ami=ami-0f9cb75652314425a" -var="instance_count=2" -var="instance_type=t2.micro" -var="key_name=your-aws-key-here" -auto-approve


Plan: 2 to add, 0 to change, 0 to destroy.
module.ec2.aws_instance.dev_ec2[1]: Creating...
module.ec2.aws_instance.dev_ec2[0]: Creating...
module.ec2.aws_instance.dev_ec2[0]: Still creating... [10s elapsed]
module.ec2.aws_instance.dev_ec2[1]: Still creating... [10s elapsed]
module.ec2.aws_instance.dev_ec2[0]: Creation complete after 16s [id=i-09243cf69c709f459]
module.ec2.aws_instance.dev_ec2[1]: Still creating... [20s elapsed]
module.ec2.aws_instance.dev_ec2[1]: Creation complete after 22s [id=i-05875a471e8ba565d]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

```

### Ansible
```
$ ansible-playbook -i ansible/inventory.ini ansible/playbook.yaml


PLAY [Configure EC2 instance] *************************************************

TASK [Gathering Facts] *************************************************
    ok: [15.223.54.139]

TASK [Update apt packages (for Ubuntu) or yum (Amazon Linux)] *************
ok: [15.223.54.139]

TASK [Install base packages] **********************************************
ok: [15.223.54.139]

TASK [Copy setup script (optional)] ***************************************
changed: [15.223.54.139]

TASK [Run setup script] *************************************************
fatal: [15.223.54.139]: FAILED! => 
{"changed": true, "cmd": "/tmp/setup.sh", "delta": "0:00:00.951257", 
"end": "2025-07-10 20:05:45.470343", "msg": "non-zero return code", }

PLAY RECAP **************************************************
15.223.54.139 : ok=4    changed=1    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0
```

### Python CLI

1. No argument

```bash
$ ec2-start

usage: ec2-start [-h] --region REGION [--tag-key TAG_KEY] [--tag-value TAG_VALUE] [--dry-run] [--log-file LOG_FILE] [--verbose] [--state STATE] [--min-uptime-hours MIN_UPTIME_HOURS]
ec2-start: error: the following arguments are required: --region
```

2. With arguments

```bash
$ ec2-start --region ca-central-1 --tag-key env --tag-value dev --log-file start.log --verbose

cat start.log

2025-07-09 16:03:39,062 - DEBUG - No retry needed.
2025-07-09 16:03:39,063 - INFO - Started ['i-062d074hjk3jk95dbxxx3e']
```

3. Checking the current status of the group of EC2 instances.

```bash
~/Project/aws-ec2-utils$python3 ec2_metadata.py --region ca-central-1
INFO: Found credentials in shared credentials file: ~/.aws/credentials
```
