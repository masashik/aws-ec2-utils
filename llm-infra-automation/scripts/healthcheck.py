# healthcheck.py

import boto3
import datetime

def check_ec2_health(region="ca-central-1"):
    ec2 = boto3.client("ec2", region_name=region)
    cloudwatch = boto3.client("cloudwatch", region_name=region)

    response = ec2.describe_instance_status(IncludeAllInstances=True)
    results = []

    for instance in response["InstanceStatuses"]:
        instance_id = instance["InstanceId"]
        state = instance["InstanceState"]["Name"]
        status = instance["InstanceStatus"]["Status"]

        # CloudWatch CPU Utilization (last 10 minutes average)
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(minutes=10)

        metrics = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=["Average"]
        )

        avg_cpu = metrics["Datapoints"][0]["Average"] if metrics["Datapoints"] else 0.0

        results.append({
            "instance_id": instance_id,
            "state": state,
            "status": status,
            "avg_cpu": avg_cpu
        })

    return results
