#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import argparse
import logging
from ec2_utils.ec2_ops import get_ec2_instances, filter_instances, start_instances

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Start all EC2 instances in a specified region.
def start_ec2_instances(region):
    parser = argparse.ArgumentParser(description="List EC2 instances and their metadata.")
    parser.add_argument("--region", required=True, help="AWS region, e.g. us-west-2")
    parser.add_argument("--tag-key", help="Tag key to filter")
    parser.add_argument("--tag-value", help="Tag value to filter")
    parser.add_argument("--dry-run", action="store_true", help="Dry run only")
    args = parser.parse_args()

    instances = get_ec2_instances(args.region)
    filtered = filter_instances(instances,args.tag_key,args.tag_value)

    instance_ids = []
    for i in filtered:
        instance_ids.append(i["InstanceId"])

    start_instances(args.region, instance_ids, dry_run=args.dry_run)

if __name__ == "__main__":
    start_ec2_instances()
