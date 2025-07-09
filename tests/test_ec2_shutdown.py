import unittest
from unittest.mock import patch, MagicMock
from ec2_utils.ec2_ops import stop_instances
from ec2_utils.filters import filter_instances


class TestEC2Utils(unittest.TestCase):

    def test_filter_instances_by_tag(self):
        instances = [
            {"InstanceId": "i-062d07d1aa995db3e", "Tags": [{"Key": "env", "Value": "dev"}]},
            {"InstanceId": "i-0a186009c5c711fd7", "Tags": [{"Key": "env", "Value": "stage"}]},
            {"InstanceId": "i-0fccfc4be44c3d997", "Tags": [{"Key": "env", "Value": "prod"}]},
        ]
        result = filter_instances(instances, tag_key="env", tag_value="dev")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["InstanceId"], "i-062d07d1aa995db3e")

    def test_filter_instances_tag_mismatch(self):
        instances = [
            {"InstanceId": "i-abc", "Tags": [{"Key": "env", "Value": "qa"}]},
        ]
        result = filter_instances(instances, tag_key="env", tag_value="prod")
        self.assertEqual(len(result), 0)

    def test_filter_instances_no_tags(self):
        instances = [
            {"InstanceId": "i-def"},  # No 'Tags' key at all
        ]
        result = filter_instances(instances, tag_key="env", tag_value="dev")
        self.assertEqual(len(result), 0)

    def test_filter_instances_multiple_match(self):
        instances = [
            {"InstanceId": "i-1", "Tags": [{"Key": "env", "Value": "dev"}]},
            {"InstanceId": "i-2", "Tags": [{"Key": "env", "Value": "dev"}]},
        ]
        result = filter_instances(instances, tag_key="env", tag_value="dev")
        self.assertEqual(len(result), 2)
        self.assertEqual({i["InstanceId"] for i in result}, {"i-1", "i-2"})

    def test_filter_instances_wrong_key(self):
        instances = [
            {"InstanceId": "i-123", "Tags": [{"Key": "role", "Value": "web"}]},
        ]
        result = filter_instances(instances, tag_key="env", tag_value="dev")
        self.assertEqual(len(result), 0)

    @patch("boto3.client")
    def test_stop_instances(self, mock_boto):
        fake_client = MagicMock()
        mock_boto.return_value = fake_client
        stop_instances("us-east-1", ["i-123"], dry_run=True)
        fake_client.stop_instances.assert_called_once_with(InstanceIds=["i-123"], DryRun=True)


if __name__ == "__main__":
    unittest.main()
