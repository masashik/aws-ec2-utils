import unittest
from unittest.mock import patch, MagicMock
from ec2_utils import ec2_metadata


class TestEc2Metadata(unittest.TestCase):

    @patch("ec2_utils.ec2_metadata.get_ec2_instances")
    @patch("ec2_utils.ec2_metadata.filter_instances")
    @patch("ec2_utils.ec2_metadata.boto3.client")
    @patch("ec2_utils.ec2_metadata.argparse.ArgumentParser")
    def test_get_instance_metadata(self, mock_argparser, mock_boto3,
                                   mock_filter, mock_get_instances):
        # Set up mock args
        mock_args = MagicMock()
        mock_args.region = "us-west-1"
        mock_args.tag_key = "env"
        mock_args.tag_value = "dev"
        mock_args.dry_run = False
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_argparser.return_value = mock_parser

        # Mock instance list
        mock_get_instances.return_value = [{"InstanceId": "i-123456"}]
        mock_filter.return_value = [{"InstanceId": "i-123456"}]

        # Mock boto3 describe_instances
        mock_ec2 = MagicMock()
        mock_boto3.return_value = mock_ec2
        mock_ec2.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-123456",
                            "State": {"Name": "running"},
                            "InstanceType": "t2.micro",
                            "LaunchTime": "2023-01-01T00:00:00Z"
                        }
                    ]
                }
            ]
        }

        # Run
        ec2_metadata.get_ec2_metadata()

        # Assert call chain
        mock_get_instances.assert_called_once_with("us-west-1")
        mock_filter.assert_called_once()
        mock_ec2.describe_instances.assert_called_once_with(
            InstanceIds=["i-123456"], DryRun=False
        )


if __name__ == "__main__":
    unittest.main()
