import unittest
from unittest.mock import patch
from ec2_utils import ec2_metadata


class TestEc2Metadata(unittest.TestCase):

    @patch("ec2_utils.ec2_metadata.requests.get")
    def test_get_metadata_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "mocked-data"
        result = ec2_metadata.get_metadata("http://169.254.169.254/latest/meta-data/")
        self.assertEqual(result, "mocked-data")

    @patch("ec2_utils.ec2_metadata.requests.get")
    def test_get_metadata_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        result = ec2_metadata.get_metadata("http://169.254.169.254/latest/meta-data/")
        self.assertEqual(result, "")

    @patch("ec2_utils.ec2_metadata.get_metadata")
    def test_get_instance_metadata(self, mock_get_metadata):
        mock_get_metadata.side_effect = lambda key: {
            "instance-id": "i-12345",
            "instance-type": "t2.micro",
            "placement/availability-zone": "us-west-2a"
        }.get(key, "")
        result = ec2_metadata.get_instance_metadata()
        self.assertEqual(result["instance-id"], "i-12345")
        self.assertEqual(result["instance-type"], "t2.micro")
        self.assertEqual(result["availability-zone"], "us-west-2a")


if __name__ == "__main__":
    unittest.main()
