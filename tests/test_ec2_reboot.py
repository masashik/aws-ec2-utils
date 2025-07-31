import unittest
from unittest.mock import patch, MagicMock
from ec2_utils import ec2_reboot


class TestEC2Reboot(unittest.TestCase):

    @patch("ec2_utils.ec2_reboot.boto3.client")
    def test_reboot_instances_success(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        ec2_reboot.reboot_instances("us-east-1", ["i-abc123"], dry_run=True)
        mock_client.reboot_instances.assert_called_once_with(InstanceIds=["i-abc123"], DryRun=True)

    @patch("ec2_utils.ec2_reboot.boto3.client")
    def test_reboot_instances_exception(self, mock_boto_client):
        mock_client = MagicMock()
        mock_client.reboot_instances.side_effect = Exception("Something went wrong")
        mock_boto_client.return_value = mock_client

        # Should not raise error despite exception
        try:
            ec2_reboot.reboot_instances("us-east-1", ["i-abc123"], dry_run=True)
        except Exception:
            self.fail("reboot_instances() raised Exception unexpectedly!")

if __name__ == "__main__":
    unittest.main()
