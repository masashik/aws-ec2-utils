import unittest
from unittest.mock import patch, MagicMock
from ec2_utils import ec2_ops


class TestEC2Ops(unittest.TestCase):

    @patch("ec2_utils.ec2_ops.boto3.client")
    def test_get_ec2_instances_success(self, mock_boto_client):
        mock_client = MagicMock()
        mock_client.describe_instances.return_value = {
            "Reservations": [{"Instances": [{"InstanceId": "i-123"}]}]
        }
        mock_boto_client.return_value = mock_client

        result = ec2_ops.get_ec2_instances("us-west-1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["InstanceId"], "i-123")

    @patch("ec2_utils.ec2_ops.boto3.client")
    def test_stop_instances_success(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        ec2_ops.stop_instances("us-west-1", ["i-abc123"], dry_run=True)
        mock_client.stop_instances.assert_called_once_with(InstanceIds=["i-abc123"], DryRun=True)

    @patch("ec2_utils.ec2_ops.boto3.client")
    def test_stop_instances_retry_logic(self, mock_boto_client):
        mock_client = MagicMock()
        mock_client.stop_instances.side_effect = [
            Exception("API Error"), Exception("API Error"), None
        ]
        mock_boto_client.return_value = mock_client

        ec2_ops.stop_instances("us-west-1", ["i-abc123"], dry_run=True, retries=3)
        self.assertEqual(mock_client.stop_instances.call_count, 3)


if __name__ == "__main__":
    unittest.main()
