import unittest
from ec2_utils import filters
from datetime import datetime, timedelta, timezone

class TestFilters(unittest.TestCase):

    def test_filter_instances_by_tag(self):
        instances = [
            {"InstanceId": "i-1", "Tags": [{"Key": "env", "Value": "dev"}]},
            {"InstanceId": "i-2", "Tags": [{"Key": "env", "Value": "prod"}]},
        ]
        result = filters.filter_instances(instances, "env", "dev")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["InstanceId"], "i-1")

    def test_filter_instances_tag_mismatch(self):
        instances = [{"InstanceId": "i-1", "Tags": [{"Key": "env", "Value": "prod"}]}]
        result = filters.filter_instances(instances, "env", "dev")
        self.assertEqual(len(result), 0)

    def test_filter_instances_no_tags(self):
        instances = [{"InstanceId": "i-1"}]
        result = filters.filter_instances(instances, "env", "dev")
        self.assertEqual(result, [])

    def test_filter_instances_multiple_match(self):
        instances = [
            {"InstanceId": "i-1", "Tags": [{"Key": "env", "Value": "dev"}]},
            {"InstanceId": "i-2", "Tags": [{"Key": "env", "Value": "dev"}]},
        ]
        result = filters.filter_instances(instances, "env", "dev")
        self.assertEqual(len(result), 2)

    def test_filter_instances_wrong_key(self):
        instances = [{"InstanceId": "i-1", "Tags": [{"Key": "stage", "Value": "dev"}]}]
        result = filters.filter_instances(instances, "env", "dev")
        self.assertEqual(result, [])

    def test_filter_by_uptime_excludes_new_instances(self):
        now = datetime.now(timezone.utc)
        instances = [
            {"InstanceId": "i-new", "LaunchTime": now - timedelta(hours=1)},
            {"InstanceId": "i-old", "LaunchTime": now - timedelta(hours=10)},
        ]
        filtered = filters.filter_by_uptime(instances, min_hours=5)
        assert len(filtered) == 1
        assert filtered[0]["InstanceId"] == "i-old"

if __name__ == "__main__":
    unittest.main()
