#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import argparse
import logging
from ec2_utils.ec2_ops import get_ec2_instances
from ec2_utils.filters import filter_instances

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_ec2_metadata():
    parser = argparse.ArgumentParser(description="List EC2 instances and their metadata.")
    parser.add_argument("--region", required=True, help="AWS region, e.g. us-west-2")
    parser.add_argument("--tag-key", help="Tag key to filter")
    parser.add_argument("--tag-value", help="Tag value to filter")
    parser.add_argument("--dry-run", action="store_true", help="Dry run only")
    args = parser.parse_args()

    instances = get_ec2_instances(args.region)
    filtered = filter_instances(instances, args.tag_key, args.tag_value)

    instance_ids = []
    for i in filtered:
        instance_ids.append(i["InstanceId"])

    try:
        ec2 = boto3.client("ec2", region_name=args.region)
        response = ec2.describe_instances(InstanceIds=instance_ids, DryRun=args.dry_run)
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
        print(f"[{i['State'].upper()}] {i['InstanceId']}" +
              f" {i['Name']} ({i['Type']}) launched at {i['LaunchTime']}")

    # I will leave these debug line to be commented out for future usage.
    # import sys
    # print("----------------------------------------------------")
    # print(i)
    # print("----------------------------------------------------")
    # sys.stdout.flush()


if __name__ == "__main__":
    get_ec2_metadata()
