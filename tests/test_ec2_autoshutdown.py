import unittest
from unittest.mock import patch, MagicMock
from ec2_utils import ec2_autoshutdown
import datetime

class TestEc2Autoshutdown(unittest.TestCase):

    @patch("boto3.resource")
    def test_get_instances(self, mock_resource):
        mock_instance = MagicMock()
        mock_instance.state = {"Name": "running"}
        mock_instance.tags = [{"Key": "env", "Value": "dev"}]
        mock_instance.launch_time = datetime.datetime.now() - datetime.timedelta(minutes=20)

        mock_ec2 = MagicMock()
        mock_ec2.instances.all.return_value = [mock_instance]
        mock_resource.return_value = mock_ec2

        result = ec2_autoshutdown.get_instances("us-east-1", "env", "dev")
        self.assertEqual(len(result), 1)

    def test_should_shutdown_true(self):
        instance = MagicMock()
        instance.state = {"Name": "running"}
        instance.tags = [{"Key": "env", "Value": "dev"}]
        instance.launch_time = datetime.datetime.now() - datetime.timedelta(minutes=40)
        result = ec2_autoshutdown.should_shutdown(instance, "env", "dev", threshold_minutes=30)
        self.assertTrue(result)

    def test_should_shutdown_false_due_to_tag(self):
        instance = MagicMock()
        instance.state = {"Name": "running"}
        instance.tags = [{"Key": "env", "Value": "prod"}]
        instance.launch_time = datetime.datetime.now() - datetime.timedelta(minutes=40)
        result = ec2_autoshutdown.should_shutdown(instance, "env", "dev", threshold_minutes=30)
        self.assertFalse(result)

    def test_should_shutdown_false_due_to_state(self):
        instance = MagicMock()
        instance.state = {"Name": "stopped"}
        instance.tags = [{"Key": "env", "Value": "dev"}]
        instance.launch_time = datetime.datetime.now() - datetime.timedelta(minutes=40)
        result = ec2_autoshutdown.should_shutdown(instance, "env", "dev", threshold_minutes=30)
        self.assertFalse(result)

    @patch("boto3.client")
    def test_shutdown_instances(self, mock_client):
        mock_ec2 = MagicMock()
        mock_client.return_value = mock_ec2

        instance = MagicMock()
        instance.id = "i-123"
        instance.state = {"Name": "running"}
        instance.tags = [{"Key": "env", "Value": "dev"}]
        instance.launch_time = datetime.datetime.now() - datetime.timedelta(minutes=40)

        ec2_autoshutdown.shutdown_instances("us-east-1", [instance], "env", "dev", 30, dry_run=True)
        mock_ec2.stop_instances.assert_called_once_with(InstanceIds=["i-123"], DryRun=True)

if __name__ == "__main__":
    unittest.main()
