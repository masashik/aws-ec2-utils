export AWS_REGION=ca-central-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export APP_NAME=llm-api-server
export ECR_REPO=${APP_NAME}
export CLUSTER_NAME=llm-eks
export K8S_NAMESPACE=llm
export POLICY_URL="https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json"
