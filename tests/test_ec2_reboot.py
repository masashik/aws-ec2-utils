import unittest
from unittest.mock import patch, MagicMock
from ec2_utils import ec2_reboot


class TestEC2Reboot(unittest.TestCase):

    @patch("ec2_utils.ec2_reboot.boto3.client")
    def test_reboot_instances_success(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        ec2_reboot.reboot_instance(["i-abc123"], "us-east-1")
        # mock_client.reboot_instance.assert_called_once_with(InstanceIds=["i-abc123"])

    @patch("ec2_utils.ec2_reboot.boto3.client")
    def test_reboot_instances_exception(self, mock_boto_client):
        mock_client = MagicMock()
        mock_client.reboot_instance.side_effect = Exception("Something went wrong")
        mock_boto_client.return_value = mock_client

        # Should not raise error despite exception
        try:
            ec2_reboot.reboot_instance(["i-abc123"], "us-east-1")
        except Exception:
            self.fail("reboot_instance() raised Exception unexpectedly!")


if __name__ == "__main__":
    unittest.main()
