import unittest
from unittest.mock import patch, MagicMock
from ec2_utils import ec2_start


class TestEC2Start(unittest.TestCase):

    @patch("ec2_utils.ec2_start.boto3.client")
    def test_start_instances_success(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        ec2_start.start_instances("us-east-1", ["i-abc123"], dry_run=True)
        mock_client.start_instances.assert_called_once_with(InstanceIds=["i-abc123"], DryRun=True)

    @patch("ec2_utils.ec2_start.boto3.client")
    def test_start_instances_failure(self, mock_boto_client):
        mock_client = MagicMock()
        mock_client.start_instances.side_effect = Exception("start failed")
        mock_boto_client.return_value = mock_client

        try:
            ec2_start.start_instances("us-east-1", ["i-abc123"], dry_run=True)
        except Exception:
            self.fail("start_instances() raised Exception unexpectedly!")

if __name__ == "__main__":
    unittest.main()
