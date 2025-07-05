#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Shutdown all EC2 instances in a specified region.
def shutdown_ec2_instances(region):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        response = ec2.describe_instances()
    except ClientError as e:
        logging.error(f"Failed to connect to EC2: {e}")
        return

    instance_IDs = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_IDs.append(instance_id)

    try:
        ec2 = boto3.client("ec2", region_name=region)
        response = ec2.stop_instances(InstanceIds=instance_IDs)
    except ClientError as e:
        logging.error(f"Failed to connect to EC2: {e}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List EC2 instances and their metadata.")
    parser.add_argument("--region", required=True, help="AWS region, e.g. us-west-2")
    args = parser.parse_args()

    shutdown_ec2_instances(args.region)
