# ![CI](https://github.com/masashik/aws-ec2-utils/actions/workflows/ci.yml/badge.svg) AWS EC2 automation of provisioning and configuration management with Python3/Terraform/Ansible 

## A problem to solve

Simplifying the provisioning EC2 instances and configuration management of toolchain 
and controlling EC2 instances without complex AWS UI interactions. Everything is in CLI!

## Features
 - EC2 automation with Terraform
 - Basic Ansible provisioning
 - Python CLI tools with Boto3
 - CI with GitHub Actions
 - Containerization with Docker
 - Auto-generated inventory


## A role of each tool
 - Terraform 
    - Provisioning EC2 instances declared and defined states.
 - Ansible 
    - Configuration management of each EC2 instance installing necessary toolchain and imperative and incremental updates.
 - Python CLI 
    - Controlling on EC2 instances like starting and stopping a group of servers.

## How-to-use
### Provisioning EC2 Instance
```
brew install terraform
terraform init
terraform plan
terraform apply -auto-approve
```

### Configuration management
```
brew install ansible
ansible-playbook -i ansible/inventory.ini ansible/playbook.yaml
```

### Controlling EC2 instances
```
git clone https://github.com/masashik/aws-ec2-utils
cd aws-ec2-utils
pip3 install -r requirements.txt
ec2-start --region ca-central-1 --tag-key env --tag-value dev --dry-run
```

### Controlling EC2 instances in docker container (environment free)
```
git clone https://github.com/masashik/aws-ec2-utils
cd aws-ec2-utils
docker build -t aws-ec2-utils .
docker run -v ~/.aws:/root/.aws:ro aws-ec2-utils python3 ec2_metadata.py --region ca-central-1 --tag-key env --tag-value dev --dry-run
```

## Example output and logs.

### Terraform
```
terraform init

Initializing the backend...
Initializing provider plugins...
- Reusing previous version of hashicorp/aws from the dependency lock file
- Installing hashicorp/aws v6.2.0...

terraform plan

aws_instance.dev_ec2: Refreshing state... [id=i-0b0d582fbffb1c04b]

Note: Objects have changed outside of Terraform

Terraform detected the following changes made outside of Terraform since the last "terraform
apply" which may have affected this plan:

# aws_instance.dev_ec2 has changed
~ resource "aws_instance" "dev_ec2" {
    id                                   = "i-0b0d582fbffb1c04b"
        - public_ip                            = "16.52.72.254" -> null
        tags                                 = {
            "Name" = "test-server-4"
                "env"  = "dev"
        }
# (37 unchanged attributes hidden)

# (8 unchanged blocks hidden)
}


Unless you have made equivalent changes to your configuration, or ignored the relevant
attributes using ignore_changes, the following plan may include actions to undo or respond to
these changes.

──────────────────────────────────────────────────────────────────────────────────────────────

Changes to Outputs:
- instance_ip = "16.52.72.254" -> null
~ public_ip   = "16.52.72.254" -> ""


terraform apply

aws_instance.dev_ec2: Refreshing state... [id=i-0b0d582fbffb1c04b]

Note: Objects have changed outside of Terraform

Terraform detected the following changes made outside of Terraform since the last "terraform
apply" which may have affected this plan:

# aws_instance.dev_ec2 has changed
~ resource "aws_instance" "dev_ec2" {
    id                                   = "i-0b0d582fbffb1c04b"
        - public_ip                            = "16.52.72.254" -> null
        tags                                 = {
            "Name" = "test-server-4"
                "env"  = "dev"
        }
# (37 unchanged attributes hidden)

# (8 unchanged blocks hidden)
}


Unless you have made equivalent changes to your configuration, or ignored the relevant
attributes using ignore_changes, the following plan may include actions to undo or respond to
these changes.

──────────────────────────────────────────────────────────────────────────────────────────────

Changes to Outputs:
- instance_ip = "16.52.72.254" -> null
~ public_ip   = "16.52.72.254" -> ""

You can apply this plan to save these new output values to the Terraform state, without
changing any real infrastructure.

Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

instance_id = "i-0b0d582fbffb1c04b"
public_ip = "15.223.54.139"
```

### Ansible
```
~/Project/aws-ec2-utils$bash scripts/gen_inventory.sh 
[OK] Inventory generated at ansible/inventory.ini

ansible-playbook -i ansible/inventory.ini ansible/playbook.yaml

PLAY [Configure EC2 instance] *************************************************

TASK [Gathering Facts] ********************************************************
    ok: [15.223.54.139]

    TASK [Update apt packages (for Ubuntu) or yum (Amazon Linux)] *************
    ok: [15.223.54.139]

    TASK [Install base packages] **********************************************
    ok: [15.223.54.139]

    TASK [Copy setup script (optional)] ***************************************
    changed: [15.223.54.139]

    TASK [Run setup script] ***************************************************
    fatal: [15.223.54.139]: FAILED! => 
    {"changed": true, "cmd": "/tmp/setup.sh", "delta": "0:00:00.951257", 
    "end": "2025-07-10 20:05:45.470343", "msg": "non-zero return code", 
    PLAY RECAP ****************************************************************
    15.223.54.139 : ok=4    changed=1    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0
```

### Python CLI
```
1. No argument is provided.

$ ec2-start

usage: ec2-start [-h] --region REGION [--tag-key TAG_KEY] [--tag-value TAG_VALUE] [--dry-run] [--log-file LOG_FILE] [--verbose] [--state STATE] [--min-uptime-hours MIN_UPTIME_HOURS]
ec2-start: error: the following arguments are required: --region

2. Proper arguments are provided.

$ ec2-start --region ca-central-1 --tag-key env --tag-value dev --log-file start.log --verbose

cat start.log

2025-07-09 16:03:37,914 - DEBUG - Changing event name from creating-client-class.iot-data to creating-client-class.iot-data-plane
2025-07-09 16:03:37,915 - DEBUG - Changing event name from before-call.apigateway to before-call.api-gateway
2025-07-09 16:03:37,916 - DEBUG - Changing event name from request-created.machinelearning.Predict to request-created.machine-learning.Predict
...........
.......
.....
2025-07-09 16:03:39,062 - DEBUG - Event needs-retry.ec2.StartInstances: calling handler <botocore.retryhandler.RetryHandler object at 0x7f9528e6e0a0>
2025-07-09 16:03:39,062 - DEBUG - No retry needed.
2025-07-09 16:03:39,063 - INFO - Started ['i-062d074hjk3jk95dbxxx3e']

3. Checking the current status of the group of EC2 instances.

~/Project/aws-ec2-utils$python3 ec2_metadata.py --region ca-central-1
INFO: Found credentials in shared credentials file: ~/.aws/credentials
[PENDING] i-06adfewb3e- {i['Name']} ({i['Type']}) launched at {i['LaunchTime']}
[STOPPED] i-0a18601fd7- {i['Name']} ({i['Type']}) launched at {i['LaunchTime']}
[STOPPED] i-0fccfcaa97- {i['Name']} ({i['Type']}) launched at {i['LaunchTime']}
[PENDING] i-0b0d51c04b- {i['Name']} ({i['Type']}) launched at {i['LaunchTime']}
```
