#!/usr/bin/env python3

import boto3
import logging
import time
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_ec2_instances(region):
    instances = []
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance)
    return instances


def start_instances(region, instance_ids, dry_run=False, retries=3):
    if not instance_ids:
        logger.info("No instances to start.")
        return
    ec2 = boto3.client("ec2", region_name=region)
    for attempt in range(1, retries + 1):
        try:
            ec2.start_instances(InstanceIds=instance_ids, DryRun=dry_run)
            logger.info(f"{'Dry run:' if dry_run else 'Started'} {instance_ids}")
            return
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS ClientError on attempt {attempt}: {error_code}")
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff


def stop_instances(region, instance_ids, dry_run=False, retries=3):
    if not instance_ids:
        logger.info("No instances to stop.")
        return
    ec2 = boto3.client("ec2", region_name=region)

    for attempt in range(1, retries + 1):
        try:
            ec2.stop_instances(InstanceIds=instance_ids, DryRun=dry_run)
            logger.info(f"{'Dry run:' if dry_run else 'Stopped'} {instance_ids}")
            return
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS ClientError on attempt {attempt}: {error_code}")
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff


def terminate_instances(region, instance_ids, dry_run=False, retries=3):
    if not instance_ids:
        logger.info("No instances to stop.")
        return

    ec2 = boto3.client("ec2", region_name=region)

    for attempt in range(1, retries + 1):
        try:
            for inst_id in instance_ids:
                ensure_delete_on_termination(region, inst_id)
            print("Terminating…")
            ec2.terminate_instances(InstanceIds=instance_ids, DryRun=dry_run)
            logger.info(f"{'Dry run:' if dry_run else 'Terminated'} {instance_ids}")
            return
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS ClientError on attempt {attempt}: {error_code}")
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff


def ensure_delete_on_termination(region, instance_id):
    ec2 = boto3.client("ec2", region_name=region)
    """Set DeleteOnTermination=True for every EBS volume on the instance."""
    details = ec2.describe_instances(InstanceIds=[instance_id])
    mappings = (
        details["Reservations"][0]["Instances"][0]["BlockDeviceMappings"]
    )

    for mapping in mappings:
        vol_id = mapping["Ebs"]["VolumeId"]
        device = mapping["DeviceName"]
        flag = mapping["Ebs"]["DeleteOnTermination"]
        if not flag:
            print(f"Setting DeleteOnTermination for {vol_id} ({device})")
            ec2.modify_instance_attribute(
                InstanceId=instance_id,
                BlockDeviceMappings=[{
                    "DeviceName": device,
                    "Ebs": {"DeleteOnTermination": True}
                }]
            )
