# scripts/gen_inventory.sh
#!/bin/bash

IP=$(terraform -chdir=terraform output -raw instance_ip)

cat <<EOF > ansible/inventory.ini
[dev]
$IP ansible_user=ec2-user ansible_ssh_private_key_file=~/.ssh/your-key.pem
EOF

echo "[OK] Inventory generated at ansible/inventory.ini"
