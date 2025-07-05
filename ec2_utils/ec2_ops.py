#!/usr/bin/env python3

import boto3
import logging

def get_ec2_instances(region):
    instances = []
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance)
    return instances

def filter_instances(instances, tag_key=None, tag_value=None)
    filtered = []
    for instance in instances:
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        if tag_key and tags.get(tag_key) != tag_value # If provided tag_key exists, and then provided tag_value does not exist in the current tag list.
            continue # Skip this loop because the provided combination of key/value does not exist in the current tag list of the regional EC2 instances.
        filtered.append(instance)
    return filtered

def stop_instances(region, instance_ids, dry_run=False):
    ec2 = boto3.client("ec2", region_name=region)
    if not instance_ids:
        logging.info("No instances to stop.")
        return
    try:
        ec2.stop_instances(InstanceIds=instance_ids, DryRun=dry_run)
        logging.info(f"{'Dry run:' if dry_run else 'Stopped'} {instance_ids}")
    except Exception as e:
        logging.error(f"Error stopping instances: {e}")

def start_instances(region, instance_ids, dry_run=False):
    ec2 = boto3.client("ec2", region_name=region)
    if not instance_ids:
        logging.info("No instances to start.")
        return
    try:
        ec2.start_instances(InstanceIds=instance_ids, DryRun=dry_run)
        logging.info(f"{'Dry run:' if dry_run else 'Stopped'} {instance_ids}")
    except Exception as e:
        logging.error(f"Error starting instances: {e}")
