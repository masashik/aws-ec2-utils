#!/usr/bin/env python3

import boto3
from datetime import datetime, timezone, timedelta
import argparse

def get_instances(region):
    ec2 = boto3.resource('ec2', region_name=region)
    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:auto_shutdown', 'Values': ['true']}
        ]
    )
    return instances

def should_shutdown(instance, threshold_minutes):
    launch_time = instance.launch_time.replace(tzinfo=timezone.utc)
    uptime = datetime.now(timezone.utc) - launch_time
    return uptime > timedelta(minutes=threshold_minutes)

def shutdown_instances(instances, threshold_minutes, dry_run):
    for instance in instances:
        #import sys
        #print("shutdown_instances....")
        #sys.stdout.flush()
        if should_shutdown(instance, threshold_minutes):
            print(f"Stopping {instance.id} (uptime exceeded)")
            try:
                instance.stop(DryRun=dry_run)
            except Exception as e:
                print(f"Failed to stop {instance.id}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', required=True)
    parser.add_argument('--minutes', type=int, default=1)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    instances = get_instances(args.region)
    import sys
    print(instances)
    sys.stdout.flush()
    shutdown_instances(instances, args.minutes, args.dry_run)

if __name__ == "__main__":
    main()
