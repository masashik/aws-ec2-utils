#!/usr/bin/env python3

# Usage:
#   Ex. python3 ec2_start.py    --region ca-central-1 --tag-key env --tag-value dev --dry-run --log-file start.log --verbose
#   Ex. python3 ec2_shutdown.py --region ca-central-1 --tag-key env --tag-value dev --dry-run --log-file shutdown.log --verbose

import boto3
from botocore.exceptions import ClientError
import argparse
import logging
from ec2_utils.ec2_ops import get_ec2_instances, start_instances
from ec2_utils.filters import filter_instances
from ec2_utils.logging_config import setup_logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Start all EC2 instances in a specified region.
def start_ec2_instances():
    parser = argparse.ArgumentParser(description="List EC2 instances and their metadata.")
    parser.add_argument("--region", required=True, help="AWS region, e.g. us-west-2")
    parser.add_argument("--tag-key", help="Tag key to filter")
    parser.add_argument("--tag-value", help="Tag value to filter")
    parser.add_argument("--dry-run", action="store_true", help="Dry run only")
    parser.add_argument("--log-file", help="Optional log file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--state", help="instance state, e.g. running")
    parser.add_argument("--min-uptime-hours", help="AWS region, e.g. 2")

    args = parser.parse_args()

    setup_logging(log_file=args.log_file, verbose=args.verbose)

    instances = get_ec2_instances(args.region)
    filtered = filter_instances(instances,args.tag_key,args.tag_value)

    instance_ids = []
    for i in filtered:
        instance_ids.append(i["InstanceId"])

    start_instances(args.region, instance_ids, dry_run=args.dry_run)

if __name__ == "__main__":
    start_ec2_instances()
