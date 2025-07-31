# import unittest
# from unittest.mock import patch, MagicMock
# from ec2_utils import ec2_terminate
# 
# 
# class TestEC2Terminate(unittest.TestCase):
# 
#     @patch("ec2_utils.ec2_terminate.boto3.client")
#     def test_terminate_instances_success(self, mock_boto_client):
#         mock_client = MagicMock()
#         mock_boto_client.return_value = mock_client
# 
#         ec2_terminate.terminate_instances("us-west-2", ["i-abc123"], dry_run=True)
#         mock_client.terminate_instances.assert_called_once_with(
#                 InstanceIds=["i-abc123"], DryRun=True)
# 
#     @patch("ec2_utils.ec2_terminate.boto3.client")
#     def test_terminate_instances_exception_handling(self, mock_boto_client):
#         mock_client = MagicMock()
#         mock_client.terminate_instances.side_effect = Exception("termination failed")
#         mock_boto_client.return_value = mock_client
# 
#         try:
#             ec2_terminate.terminate_instances("us-west-2", ["i-abc123"], dry_run=True)
#         except Exception:
#             self.fail("terminate_instances() raised Exception unexpectedly!")
# 
# 
# if __name__ == "__main__":
#     unittest.main()
