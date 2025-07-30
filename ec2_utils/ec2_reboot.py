import boto3


def reboot_instance(instance_id, region="ca-central-1"):
    ec2 = boto3.client("ec2", region_name=region)
    try:
        response = ec2.reboot_instances(InstanceIds=[instance_id])
        print(f"🔄 Reboot initiated for instance: {instance_id}")
        return response
    except Exception as e:
        print(f"❌ Failed to reboot instance {instance_id}: {e}")


def wait_for_instance_ok(instance_id, region="ca-central-1"):
    ec2 = boto3.client("ec2", region_name=region)
    print("⏳ Waiting for instance to pass status checks...")
    waiter = ec2.get_waiter("instance_status_ok")
    waiter.wait(InstanceIds=[instance_id])
    print(f"✅ Instance {instance_id} is healthy.")


if __name__ == "__main__":
    # Replace with your actual instance ID and region
    instance_id = "i-0abcd1234efgh5678"
    region = "us-west-2"
    reboot_instance(instance_id, region)
    wait_for_instance_ok(instance_id, region)
