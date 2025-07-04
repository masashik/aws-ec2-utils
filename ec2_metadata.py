#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_ec2_metadata(region):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        response = ec2.describe_instances()
    except ClientError as e:
        logging.error(f"Failed to connect to EC2: {e}")
        return

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]
            instance_type = instance["InstanceType"]
            launch_time = instance["LaunchTime"]
            name_tag = next(
                (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"),
                "NoName"
            )

            instance_info = {
                "InstanceId": instance_id,
                "State": state,
                "Type": instance_type,
                "LaunchTime": str(launch_time),
                "Name": name_tag
            }
            instances.append(instance_info)

    for i in instances:
        print(f"[{i['State'].upper()}] {i['InstanceId']} - {i['Name']} ({i['Type']}) launched at {i['LaunchTime']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List EC2 instances and their metadata.")
    parser.add_argument("--region", required=True, help="AWS region, e.g. us-west-2")
    args = parser.parse_args()

    get_ec2_metadata(args.region)
