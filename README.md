# ![CI](https://github.com/masashik/aws-ec2-utils/actions/workflows/ci.yml/badge.svg) AWS EC2 Utilities


Python CLI tools for managing EC2 instances using Boto3.

## A problem to solve

Simplifying the provisioning EC2 instances and controlling of starting and stopping the EC2 instances without complicated AWS UI interactions.

## Features in progress
- Provision EC2 server instances from Terraform
- Manage prepared python script to control EC2 server instances from Ansible playbook.
  - start and stop specific groups of EC2s by tags to choose region, environment(dev/test/stage/prod)
- Logging support
- Dry-run safety
- Unit tested
- Containerized

## Installation
```bash
git clone https://github.com/masashik/aws-ec2-utils

cd aws-ec2-utils

pip3 install -r requirements.txt
```

## CLI execution
```
ec2-start --region ca-central-1 --tag-key env --tag-value dev --dry-run
```

## Docker
```bash
docker run -v ~/.aws:/root/.aws:ro aws-ec2-utils python3 ec2_metadata.py --region ca-central-1 --tag-key env --tag-value dev --dry-run
```

## Example output and logs.
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

3. Checking the 

$ python3 ./ec2_metadata.py --region ca-central-1
INFO: Found credentials in shared credentials file: ~/.aws/credentials
[RUNNING] i-062d074hjk3jk95dbxxx3e- {i['Name']} ({i['Type']}) launched at {i['LaunchTime']}
```