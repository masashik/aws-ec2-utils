import unittest
from unittest.mock import patch
from ec2_utils.ec2_ops import filter_instances

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

if __name__ == "__main__":
    unittest.main()
