# tofu/backend/ec2.hcl
bucket         = "tfstate-581649156172-ca-central-1"
key            = "ec2/terraform.tfstate"
region         = "ca-central-1"
dynamodb_table = "tflock-581649156172-ca-central-1"
encrypt        = true
