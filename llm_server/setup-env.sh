AWS_REGION=ca-central-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
APP_NAME=aws-ec2-utils/llm-api-server
ECR_REPO=${APP_NAME}
CLUSTER_NAME=llm-eks
K8S_NAMESPACE=llm
