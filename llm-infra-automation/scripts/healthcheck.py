import boto3
import requests


def check_ec2_health():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_status(IncludeAllInstances=True)
    unhealthy_instances = []

    for instance in response['InstanceStatuses']:
        instance_id = instance['InstanceId']
        status = instance['InstanceStatus']['Status']
        system_status = instance['SystemStatus']['Status']
        if status != 'ok' or system_status != 'ok':
            unhealthy_instances.append(instance_id)

    return unhealthy_instances


def check_http_service(ip, port=80):
    try:
        res = requests.get(f"http://{ip}:{port}", timeout=5)
        return res.status_code
    except requests.RequestException:
        return None


if __name__ == "__main__":
    instances = check_ec2_health()
    print("Unhealthy EC2 Instances:", instances)
