#!/usr/bin/env python3

# --state running --min-uptime-hours 2

from datetime import datetime, timezone, timedelta


def filter_instances(instances, tag_key=None, tag_value=None):
    filtered = []
    for instance in instances:
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        if tag_key and tags.get(tag_key) != tag_value:
            continue  # Skip this loop because the provided combination of key/value does not exist.
        filtered.append(instance)
    return filtered


def filter_by_state(instances, allowed_states):
    return [i for i in instances if i.get("State", {}).get("Name") in allowed_states]


def filter_by_uptime(instances, min_hours):
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=min_hours)
    return [
        i for i in instances
        if i.get("LaunchTime") and i["LaunchTime"] < cutoff_time
    ]
