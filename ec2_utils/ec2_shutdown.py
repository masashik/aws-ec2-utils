#!/usr/bin/env python3

import argparse
import logging
from .ec2_ops import get_ec2_instances, stop_instances
from .filters import filter_instances
from .logging_config import setup_logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)


# Shutdown all EC2 instances in a specified region filtered by provided key/value.
def stop_ec2_instances():

    # import sys
    # logger.info("MAIN() IS RUNNING")
    # print("MAIN CALLED")
    # sys.stdout.flush()
    parser = argparse.ArgumentParser(description="List EC2 instances and their metadata.")
    parser.add_argument("--region", required=True, help="AWS region, e.g. us-west-2")
    parser.add_argument("--tag-key", help="Tag key to filter")
    parser.add_argument("--tag-value", help="Tag value to filter")
    parser.add_argument("--dry-run", action="store_true", help="Dry run only")
    parser.add_argument("--log-file", help="Optional log file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    setup_logging(log_file=args.log_file, verbose=args.verbose)

    instances = get_ec2_instances(args.region)
    filtered = filter_instances(instances, args.tag_key, args.tag_value)

    instance_ids = []
    for i in filtered:
        instance_ids.append(i["InstanceId"])

    stop_instances(args.region, instance_ids, dry_run=args.dry_run)


if __name__ == "__main__":
    stop_ec2_instances()
