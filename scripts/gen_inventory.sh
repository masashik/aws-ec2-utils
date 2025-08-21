#!/bin/bash

cd ../tofu/ec2

IPS=$(tofu output -json instance_ips | jq -r '.[]')

cd ../..

cat <<EOF > ansible/inventory.ini
[dev]
EOF

for ip in $IPS; do
  echo "$ip ansible_user=ec2-user ansible_ssh_private_key_file=~/.ssh/$AWS_EC2_SSH_KEY_NAME" >> ansible/inventory.ini
done

echo "[OK] Inventory generated at ansible/inventory.ini"
